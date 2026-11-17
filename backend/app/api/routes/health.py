from fastapi import APIRouter
import platform
import shutil

router = APIRouter()


@router.get("")
def health_check():
    has_cuda = False
    try:
        import torch
        has_cuda = torch.cuda.is_available()
    except Exception:
        pass

    return {
        "status": "ok",
        "version": "1.0.0",
        "gpu_available": has_cuda,
        "device": "cuda" if has_cuda else "cpu",
        "system": platform.system(),
        "python_version": platform.python_version(),
    }

