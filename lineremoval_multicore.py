import json
import argparse
import re
from pathlib import Path
import concurrent.futures
import os
from tqdm import tqdm  # For progress bar (optional)

def process_chunk(chunk, patterns, case_sensitive):
    """Process a chunk of lines and return filtered results"""
    filtered_lines = []
    removed_count = 0
    
    for line in chunk:
        # Parse JSON to get text content
        try:
            data = json.loads(line)
            text = str(data)  # Convert whole JSON object to string for matching
        except json.JSONDecodeError:
            text = line.strip()
        
        # Check if any pattern matches
        if not any(pattern.search(text) for pattern in patterns):
            filtered_lines.append(line)
        else:
            removed_count += 1
    
    return filtered_lines, removed_count

def filter_lines(input_file: str, output_file: str, words_to_remove: list[str], case_sensitive: bool = False) -> tuple[int, int]:
    """
    Filter lines from a JSONL file based on exact word matches using multiple cores.
    
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
    patterns = [
        re.compile(r'\b' + re.escape(word) + r'\b', 
                  re.IGNORECASE if not case_sensitive else 0)
        for word in words_to_remove
    ]
    
    # Read all lines from input file
    with open(input_file, 'r', encoding='utf-8') as infile:
        all_lines = infile.readlines()
    
    total_lines = len(all_lines)
    
    # Determine number of CPU cores and chunk size
    num_cores = os.cpu_count()
    chunk_size = max(1, total_lines // num_cores)
    
    # Split lines into chunks
    chunks = [all_lines[i:i + chunk_size] for i in range(0, total_lines, chunk_size)]
    
    filtered_results = []
    removed_lines = 0
    
    # Process chunks in parallel
    with concurrent.futures.ProcessPoolExecutor(max_workers=num_cores) as executor:
        futures = [executor.submit(process_chunk, chunk, patterns, case_sensitive) for chunk in chunks]
        
        # Collect results as they complete
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc="Processing"):
            filtered_chunk, removed_count = future.result()
            filtered_results.extend(filtered_chunk)
            removed_lines += removed_count
    
    # Write filtered lines to output file
    with open(output_file, 'w', encoding='utf-8') as outfile:
        outfile.writelines(filtered_results)
    
    return total_lines, removed_lines

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Filter JSONL lines based on word matches")
    parser.add_argument("input_file", help="Input JSONL file path")
    parser.add_argument("output_file", help="Output file path")
    parser.add_argument("words", nargs="+", help="Words to remove lines containing them")
    parser.add_argument("--case-sensitive", action="store_true", help="Enable case-sensitive matching")
    parser.add_argument("--workers", type=int, default=None, help="Number of worker processes (default: all available cores)")
    
    args = parser.parse_args()
    
    total, removed = filter_lines(args.input_file, args.output_file, args.words, args.case_sensitive)
    print(f"Processed {total} lines")
    print(f"Removed {removed} lines")
    print(f"Remaining: {total - removed} lines")