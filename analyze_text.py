#!/usr/bin/env python3
"""
Simple text analysis script for quick use
"""

import sys
from pathlib import Path
from text_analyzer import TextAnalyzer

def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_text.py <input_file> [output_file]")
        print("Example: python analyze_text.py nur_al_idah.txt analysis_report.txt")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    
    if not input_file.exists():
        print(f"Error: Input file '{input_file}' does not exist.")
        sys.exit(1)
    
    analyzer = TextAnalyzer()
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            text = f.read()
        
        analysis = analyzer.analyze_text(text)
        report = analyzer.generate_report(analysis, output_file)
        
        if not output_file:
            print(report)
        else:
            print(f"Analysis completed! Report saved to: {output_file}")
            
    except Exception as e:
        print(f"Error analyzing file: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
