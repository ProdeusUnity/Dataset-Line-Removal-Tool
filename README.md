# Dataset Line Removal Tool
Remove entire lines from a JSONL dataset using only keywords that exactly match, made for speed.

# Uses

- Filtering JSONL datasets by a word/tag, ex "bad word 1"

# Results

- Original Single Core (lineremoval.py): 2 minutes and 13 seconds
- Multicore (lineremoval_multicore.py): 11.84 seconds
- Lines removed: 3,366/41,355

2nd test (Multicore only)

Multicore (32k lines): 11.5 seconds

# Compatibility

Should be platform-agnostic as I did not use any specific features to windows, should work perfect on Linux, at least it does in my case. Unsure about ARM platforms like Mac

# License

Apache 2.0

# Usage

`python lineremoval.py "DATASET_PATH" "OUTPUT_PATH" "bad word 1" "bad word 2"`
`python lineremoval_multicore.py "DATASET_PATH" "OUTPUT_PATH" "bad word 1" "bad word 2"`

