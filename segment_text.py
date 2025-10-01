#!/usr/bin/env python3
"""
Simple text segmentation script for quick use
"""

import sys
from pathlib import Path
from text_segmenter import TextSegmenter

def main():
    if len(sys.argv) < 2:
        print("Usage: python segment_text.py <input_file> [output_dir]")
        print("Example: python segment_text.py nur_al_idah_cleaned_v2.txt segments")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    
    if not input_file.exists():
        print(f"Error: Input file '{input_file}' does not exist.")
        sys.exit(1)
    
    if output_dir is None:
        output_dir = input_file.parent / f"{input_file.stem}_segments"
    
    segmenter = TextSegmenter()
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            text = f.read()
        
        print(f"Segmenting {input_file}...")
        segments = segmenter.segment_text(text)
        
        segmenter.save_segments(output_dir)
        
        print(f"Segmentation completed!")
        print(f"Found {segments['metadata']['total_books']} books")
        print(f"Found {segments['metadata']['total_chapters']} chapters")
        print(f"Quality score: {segments['metadata']['segmentation_quality']}/100")
        print(f"Output saved to: {output_dir}")
        
    except Exception as e:
        print(f"Error segmenting file: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
