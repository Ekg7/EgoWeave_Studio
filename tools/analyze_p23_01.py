import pandas as pd

train_df = pd.read_csv('data/annotations/epic_kitchens/EPIC_100_train.csv')
p23_01 = train_df[train_df['video_id'] == 'P23_01']
print(f"P23_01 action count in train set: {len(p23_01)}")

for idx, (_, row) in enumerate(p23_01.iterrows()):
    start = row['start_timestamp']
    stop = row['stop_timestamp']
    verb = row['verb']
    vc = row['verb_class']
    noun = row['noun']
    nc = row['noun_class']
    narr = row['narration']
    print(f"[{idx+1:02d}] {start} -> {stop} | verb: {verb:<10} (id {vc:2d}) | noun: {noun:<15} (id {nc:3d}) | narr: {narr}")
