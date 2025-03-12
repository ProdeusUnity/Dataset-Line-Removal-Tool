import json
import argparse
import re
from pathlib import Path

def filter_lines(input_file: str, output_file: str, words_to_remove: list[str], case_sensitive: bool = False) -> tuple[int, int]:
    """
    Filter lines from a JSONL file based on exact word matches.
    
    Args:
        input_file: Path to input JSONL file
        output_file: Path to output filtered file
        words_to_remove: List of words to remove lines containing them
        case_sensitive: Whether matching should be case sensitive
        
    Returns:
        Tuple of (total_lines, removed_lines)
    """
    if not case_sensitive:
        words_to_remove = [word.lower() for word in words_to_remove]
    
    # Create regex patterns for each word
    # This will match words bounded by spaces, punctuation, or start/end of string
    patterns = [
        re.compile(r'\b' + re.escape(word) + r'\b', 
                  re.IGNORECASE if not case_sensitive else 0)
        for word in words_to_remove
    ]
    
    total_lines = 0
    removed_lines = 0
    
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8') as outfile:
        
        for line in infile:
            total_lines += 1
            
            # Parse JSON to get text content
            try:
                data = json.loads(line)
                text = str(data)  # Convert whole JSON object to string for matching
            except json.JSONDecodeError:
                text = line.strip()
            
            # Check if any pattern matches
            if not any(pattern.search(text) for pattern in patterns):
                outfile.write(line)
            else:
                removed_lines += 1
                
    return total_lines, removed_lines

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Filter JSONL lines based on word matches")
    parser.add_argument("input_file", help="Input JSONL file path")
    parser.add_argument("output_file", help="Output file path")
    parser.add_argument("words", nargs="+", help="Words to remove lines containing them")
    parser.add_argument("--case-sensitive", action="store_true", help="Enable case-sensitive matching")
    
    args = parser.parse_args()
    
    total, removed = filter_lines(args.input_file, args.output_file, args.words, args.case_sensitive)
    print(f"Processed {total} lines")
    print(f"Removed {removed} lines")
    print(f"Remaining: {total - removed} lines")