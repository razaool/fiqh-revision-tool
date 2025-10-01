#!/usr/bin/env python3
"""
Simple text cleaning script for quick use
"""

import sys
from pathlib import Path
from text_cleaner import TextCleaner

def main():
    if len(sys.argv) < 2:
        print("Usage: python clean_text.py <input_file> [output_file]")
        print("Example: python clean_text.py nur_al_idah.txt nur_al_idah_cleaned.txt")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    
    if not input_file.exists():
        print(f"Error: Input file '{input_file}' does not exist.")
        sys.exit(1)
    
    cleaner = TextCleaner()
    cleaner.process_file(input_file, output_file)

if __name__ == '__main__':
    main()
