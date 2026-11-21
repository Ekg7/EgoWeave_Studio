"""
TSM: Temporal Shift Module for EPIC-KITCHENS-100 action recognition.
Reference: Lin et al., 'TSM: Temporal Shift Module for Efficient Video Understanding' (arXiv:1811.08383)
Official C1 Action Recognition baseline adapted for EgoWeave Studio inference.
"""

from typing import Dict, Tuple
import torch
import torch.nn as nn
import torchvision.models as models


class TemporalShift(nn.Module):
    """
    Shifts 1/fold_div of channels left and 1/fold_div of channels right along temporal dimension.
    Zero FLOPs, zero extra parameters.
    """

    def __init__(self, net: nn.Module, n_segment: int = 8, n_div: int = 8):
        super().__init__()
        self.net = net
        self.n_segment = n_segment
        self.fold_div = n_div

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.shift(x, self.n_segment, fold_div=self.fold_div)
        return self.net(x)

    @staticmethod
    def shift(x: torch.Tensor, n_segment: int, fold_div: int = 8) -> torch.Tensor:
        nt, c, h, w = x.size()
        n_batch = nt // n_segment
        x = x.view(n_batch, n_segment, c, h, w)

        fold = c // fold_div
        out = torch.zeros_like(x)
        out[:, :-1, :fold] = x[:, 1:, :fold]                    # shift left (next frame)
        out[:, 1:, fold: 2 * fold] = x[:, :-1, fold: 2 * fold]  # shift right (prev frame)
        out[:, :, 2 * fold:] = x[:, :, 2 * fold:]               # stationary channels

        return out.view(nt, c, h, w)


def make_temporal_shift(net: nn.Module, n_segment: int = 8, n_div: int = 8):
    """Inserts TemporalShift modules into ResNet residual blocks."""
    def make_block_temporal(stage):
        blocks = list(stage.children())
        for i, b in enumerate(blocks):
            b.conv1 = TemporalShift(b.conv1, n_segment=n_segment, n_div=n_div)
        return nn.Sequential(*blocks)

    net.layer1 = make_block_temporal(net.layer1)
    net.layer2 = make_block_temporal(net.layer2)
    net.layer3 = make_block_temporal(net.layer3)
    net.layer4 = make_block_temporal(net.layer4)


class EpicTSM(nn.Module):
    """
    EPIC-KITCHENS-100 TSM Action Classifier.
    - Backbone: ResNet-50 with TemporalShift
    - Output: 397 logits (97 verbs, 300 nouns)
    - Consensus: Average across segments
    """

    def __init__(self, num_segments: int = 8, num_verbs: int = 97, num_nouns: int = 300):
        super().__init__()
        self.num_segments = num_segments
        self.num_verbs = num_verbs
        self.num_nouns = num_nouns
        self.total_classes = num_verbs + num_nouns  # 397

        # 1. Base ResNet-50
        base_resnet = models.resnet50(weights=None)
        make_temporal_shift(base_resnet, n_segment=num_segments, n_div=8)

        feature_dim = base_resnet.fc.in_features  # 2048
        base_resnet.fc = nn.Identity()
        self.base_model = base_resnet

        # 2. Linear classification head
        self.fc = nn.Linear(feature_dim, self.total_classes)

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Input shape: (batch_size, num_segments, 3, 224, 224)
        Returns:
            verb_logits: (batch_size, 97)
            noun_logits: (batch_size, 300)
        """
        b, t, c, h, w = x.shape
        assert t == self.num_segments, f"Expected {self.num_segments} segments, got {t}"

        # Flatten batch and time for 2D spatial backbone
        x = x.view(b * t, c, h, w)
        features = self.base_model(x)  # (b * t, 2048)
        logits = self.fc(features)    # (b * t, 397)

        # Reshape to (b, t, 397) and apply average consensus
        logits = logits.view(b, t, self.total_classes).mean(dim=1)  # (b, 397)

        verb_logits = logits[:, :self.num_verbs]
        noun_logits = logits[:, self.num_verbs:]

        return verb_logits, noun_logits


def load_epic_tsm_checkpoint(checkpoint_path: str, device: str = "cpu") -> EpicTSM:
    """Loads weights from official C1 tsm_rgb.ckpt into EpicTSM."""
    model = EpicTSM(num_segments=8, num_verbs=97, num_nouns=300)
    state = torch.load(checkpoint_path, map_location=device)
    state_dict = state.get("state_dict", state)

    # Clean prefixes from PyTorch Lightning / Distributed DataParallel
    cleaned_dict = {}
    for k, v in state_dict.items():
        name = k
        for prefix in ["model.", "module.", "base_model."]:
            if name.startswith(prefix):
                name = name[len(prefix):]
        # Match base_model vs fc
        if name.startswith("fc.") or name.startswith("new_fc."):
            cleaned_dict["fc." + name.split(".", 1)[1]] = v
        else:
            cleaned_dict["base_model." + name] = v

    missing, unexpected = model.load_state_dict(cleaned_dict, strict=False)
    print(f"[TSM Loader] Checkpoint loaded. Missing keys: {len(missing)}, Unexpected keys: {len(unexpected)}")
    model.eval()
    return model
