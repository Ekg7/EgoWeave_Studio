import pandas as pd
import csv

# 1. Load manifest.csv (competition evaluation set)
with open('student_kit/manifest.csv') as f:
    manifest_rows = list(csv.DictReader(f))
manifest_video_ids = set(r['video_id'] for r in manifest_rows)
print(f"Manifest total videos: {len(manifest_video_ids)}")

# 2. Load EPIC-KITCHENS-100 train annotations
train_df = pd.read_csv('data/annotations/epic_kitchens/EPIC_100_train.csv')
train_video_ids = set(train_df['video_id'].unique())
print(f"EPIC-100 train total videos: {len(train_video_ids)}")

# Check overlap between train_video_ids and manifest_video_ids
overlap = train_video_ids.intersection(manifest_video_ids)
print(f"Overlap between EPIC-100 train and manifest: {len(overlap)} (Must be 0)")

# 3. Analyze videos with rich, diverse actions
# Target actions: cut, wash, open, close, take, put, stir, pour
target_verbs = ['cut', 'wash', 'open', 'close', 'take', 'put', 'pour']
target_nouns = ['onion', 'knife', 'tap', 'pan', 'plate', 'bottle', 'cupboard', 'drawer']

# Filter train annotations for target participants and short-to-medium durations
video_stats = []
for vid, group in train_df.groupby('video_id'):
    participant = group['participant_id'].iloc[0]
    num_actions = len(group)
    verbs = group['verb'].tolist()
    nouns = group['noun'].tolist()
    
    # Check for cut onion or cut vegetable
    has_cut_onion = any(v == 'cut' and 'onion' in str(n) for v, n in zip(verbs, nouns))
    has_wash = any(v in ['wash', 'clean'] for v in verbs)
    has_take_knife = any('knife' in str(n) for n in nouns)
    
    # Calculate duration approximately from max stop_timestamp
    # Timestamps are hh:mm:ss.ms
    def ts_to_sec(ts):
        parts = str(ts).split(':')
        return float(parts[0])*3600 + float(parts[1])*60 + float(parts[2])
    
    max_sec = max(ts_to_sec(ts) for ts in group['stop_timestamp'])
    
    video_stats.append({
        'video_id': vid,
        'participant': participant,
        'duration_sec': round(max_sec, 1),
        'num_actions': num_actions,
        'has_cut_onion': has_cut_onion,
        'has_wash': has_wash,
        'has_take_knife': has_take_knife,
        'verb_diversity': len(set(verbs)),
        'noun_diversity': len(set(nouns))
    })

stats_df = pd.DataFrame(video_stats)
# Filter out manifest videos just in case
stats_df = stats_df[~stats_df['video_id'].isin(manifest_video_ids)]

print("\n--- Videos with 'cut onion': ---")
cut_onion_vids = stats_df[stats_df['has_cut_onion']].sort_values(by='duration_sec')
print(cut_onion_vids[['video_id', 'participant', 'duration_sec', 'num_actions', 'verb_diversity', 'noun_diversity']].head(10))

print("\n--- Diverse Candidate Videos (Short to Medium Duration < 300s): ---")
candidates = stats_df[(stats_df['duration_sec'] <= 300) & (stats_df['duration_sec'] >= 30) & (stats_df['num_actions'] >= 10)].sort_values(by='num_actions', ascending=False)
print(candidates[['video_id', 'participant', 'duration_sec', 'num_actions', 'has_cut_onion', 'has_wash', 'has_take_knife']].head(15))
