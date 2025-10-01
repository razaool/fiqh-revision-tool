#!/usr/bin/env python3
"""
Text cleaning tool for Islamic texts, specifically designed for Arabic and transliterated content.
Focuses on cleaning Nur al-Idah and similar fiqh texts.
"""

import re
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import unicodedata
from tqdm import tqdm
import click
from colorama import init, Fore, Style

# Initialize colorama for cross-platform colored output
init(autoreset=True)

class TextCleaner:
    """Main class for cleaning Islamic texts with focus on Arabic content."""
    
    def __init__(self):
        self.cleaning_stats = {
            'lines_processed': 0,
            'errors_fixed': 0,
            'common_issues': {}
        }
        
        # Common OCR errors and their corrections
        self.ocr_corrections = {
            # Common OCR mistakes for Arabic letters
            '0': '٠',  # Arabic zero
            '1': '١',  # Arabic one
            '2': '٢',  # Arabic two
            '3': '٣',  # Arabic three
            '4': '٤',  # Arabic four
            '5': '٥',  # Arabic five
            '6': '٦',  # Arabic six
            '7': '٧',  # Arabic seven
            '8': '٨',  # Arabic eight
            '9': '٩',  # Arabic nine
            
            # Common transliteration fixes
            'allah': 'Allah',
            'muhammad': 'Muhammad',
            'rasulullah': 'Rasulullah',
            'sallallahu alayhi wasallam': 'sallallahu alayhi wasallam',
            'radiyallahu anhu': 'radiyallahu anhu',
            'radiyallahu anha': 'radiyallahu anha',
            'radiyallahu anhuma': 'radiyallahu anhuma',
            'radiyallahu anhum': 'radiyallahu anhum',
        }
        
        # Patterns for common text issues
        self.issue_patterns = {
            'multiple_spaces': r'\s{2,}',
            'tabs_to_spaces': r'\t+',
            'line_breaks': r'\r\n|\r|\n',
            'extra_punctuation': r'[.]{2,}|[!]{2,}|[?]{2,}',
            'mixed_quotes': r'[""''„"‚\']',
            'bracket_spacing': r'\s*([\(\)\[\]\{\}])\s*',
        }

    def normalize_unicode(self, text: str) -> str:
        """Normalize Unicode characters and fix encoding issues."""
        # Normalize to NFC form
        text = unicodedata.normalize('NFC', text)
        
        # Fix common encoding issues
        text = text.replace('\ufeff', '')  # Remove BOM
        text = text.replace('\u200e', '')  # Remove left-to-right mark
        text = text.replace('\u200f', '')  # Remove right-to-left mark
        
        return text

    def fix_ocr_errors(self, text: str) -> str:
        """Fix common OCR errors in the text."""
        for error, correction in self.ocr_corrections.items():
            if error in text:
                text = text.replace(error, correction)
                self.cleaning_stats['errors_fixed'] += 1
                self.cleaning_stats['common_issues']['ocr_errors'] = \
                    self.cleaning_stats['common_issues'].get('ocr_errors', 0) + 1
        
        return text

    def clean_whitespace(self, text: str) -> str:
        """Clean up whitespace issues."""
        # Replace multiple spaces with single space (but preserve line structure)
        text = re.sub(r'[ \t]+', ' ', text)
        
        # Replace tabs with spaces
        text = re.sub(self.issue_patterns['tabs_to_spaces'], ' ', text)
        
        # Normalize line breaks but preserve them
        text = re.sub(self.issue_patterns['line_breaks'], '\n', text)
        
        # Remove leading/trailing whitespace from lines but keep empty lines
        lines = text.split('\n')
        lines = [line.strip() for line in lines]
        
        return '\n'.join(lines)

    def fix_punctuation(self, text: str) -> str:
        """Fix punctuation issues."""
        # Fix multiple punctuation marks
        text = re.sub(self.issue_patterns['extra_punctuation'], 
                     lambda m: m.group(0)[0], text)
        
        # Normalize quotes
        text = re.sub(self.issue_patterns['mixed_quotes'], '"', text)
        
        # Fix spacing around brackets
        text = re.sub(self.issue_patterns['bracket_spacing'], r'\1', text)
        
        return text

    def clean_arabic_text(self, text: str) -> str:
        """Specific cleaning for Arabic text."""
        # Remove diacritics if requested (optional)
        # text = re.sub(r'[\u064B-\u0652\u0670\u0640]', '', text)
        
        # Fix common Arabic OCR issues
        arabic_corrections = {
            'ا': 'ا',  # Alif
            'أ': 'أ',  # Alif with hamza above
            'إ': 'إ',  # Alif with hamza below
            'آ': 'آ',  # Alif with madda
        }
        
        for error, correction in arabic_corrections.items():
            if error in text:
                text = text.replace(error, correction)
        
        return text

    def detect_issues(self, text: str) -> List[Dict]:
        """Detect potential issues in the text."""
        issues = []
        
        # Check for common problems
        if re.search(self.issue_patterns['multiple_spaces'], text):
            issues.append({'type': 'multiple_spaces', 'severity': 'low'})
        
        if re.search(self.issue_patterns['extra_punctuation'], text):
            issues.append({'type': 'extra_punctuation', 'severity': 'medium'})
        
        if '\t' in text:
            issues.append({'type': 'tabs', 'severity': 'low'})
        
        if '\ufeff' in text:
            issues.append({'type': 'bom', 'severity': 'high'})
        
        return issues

    def clean_text(self, text: str, aggressive: bool = False) -> Tuple[str, List[Dict]]:
        """Main text cleaning function."""
        original_text = text
        issues = self.detect_issues(text)
        
        # Apply cleaning steps
        text = self.normalize_unicode(text)
        text = self.clean_whitespace(text)
        text = self.fix_punctuation(text)
        text = self.fix_ocr_errors(text)
        text = self.clean_arabic_text(text)
        
        if aggressive:
            # More aggressive cleaning
            text = re.sub(r'[^\w\s\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF.,!?;:()\[\]{}""''-]', '', text)
        
        self.cleaning_stats['lines_processed'] += 1
        
        return text, issues

    def process_file(self, input_path: Path, output_path: Optional[Path] = None, 
                    aggressive: bool = False) -> None:
        """Process a text file and clean it."""
        if not input_path.exists():
            click.echo(f"{Fore.RED}Error: Input file {input_path} does not exist.")
            return
        
        if output_path is None:
            output_path = input_path.parent / f"{input_path.stem}_cleaned{input_path.suffix}"
        
        click.echo(f"{Fore.BLUE}Processing: {input_path}")
        click.echo(f"{Fore.BLUE}Output: {output_path}")
        
        try:
            # Read the file with different encodings
            text = None
            encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
            
            for encoding in encodings:
                try:
                    with open(input_path, 'r', encoding=encoding) as f:
                        text = f.read()
                    click.echo(f"{Fore.GREEN}Successfully read file with {encoding} encoding")
                    break
                except UnicodeDecodeError:
                    continue
            
            if text is None:
                click.echo(f"{Fore.RED}Error: Could not read file with any supported encoding")
                return
            
            # Clean the text
            cleaned_text, issues = self.clean_text(text, aggressive)
            
            # Write the cleaned text
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_text)
            
            # Report results
            click.echo(f"{Fore.GREEN}✓ Text cleaned successfully!")
            click.echo(f"{Fore.YELLOW}Issues found: {len(issues)}")
            for issue in issues:
                click.echo(f"  - {issue['type']} ({issue['severity']})")
            
            click.echo(f"{Fore.CYAN}Cleaning stats:")
            click.echo(f"  - Lines processed: {self.cleaning_stats['lines_processed']}")
            click.echo(f"  - Errors fixed: {self.cleaning_stats['errors_fixed']}")
            
        except Exception as e:
            click.echo(f"{Fore.RED}Error processing file: {e}")

    def interactive_clean(self, text: str) -> str:
        """Interactive cleaning mode for manual review."""
        click.echo(f"{Fore.BLUE}Interactive cleaning mode")
        click.echo(f"{Fore.YELLOW}Original text length: {len(text)} characters")
        
        # Show first few lines
        lines = text.split('\n')[:10]
        click.echo(f"{Fore.CYAN}First 10 lines:")
        for i, line in enumerate(lines, 1):
            click.echo(f"{i:2d}: {line}")
        
        text_lines = text.split('\n')
        if len(lines) < len(text_lines):
            click.echo(f"... and {len(text_lines) - len(lines)} more lines")
        
        # Ask for confirmation
        if click.confirm(f"{Fore.GREEN}Proceed with cleaning?"):
            cleaned_text, issues = self.clean_text(text)
            click.echo(f"{Fore.GREEN}Cleaning completed!")
            return cleaned_text
        else:
            click.echo(f"{Fore.YELLOW}Cleaning cancelled.")
            return text

@click.command()
@click.argument('input_file', type=click.Path(exists=True, path_type=Path))
@click.option('--output', '-o', type=click.Path(path_type=Path), 
              help='Output file path (default: input_file_cleaned)')
@click.option('--aggressive', '-a', is_flag=True, 
              help='Apply aggressive cleaning (removes more characters)')
@click.option('--interactive', '-i', is_flag=True, 
              help='Interactive mode for manual review')
@click.option('--preview', '-p', is_flag=True, 
              help='Preview issues without cleaning')
def main(input_file: Path, output: Optional[Path], aggressive: bool, 
         interactive: bool, preview: bool):
    """Clean Islamic text files, focusing on Arabic content and common OCR errors."""
    
    cleaner = TextCleaner()
    
    if preview:
        # Preview mode - just show issues
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                text = f.read()
            
            issues = cleaner.detect_issues(text)
            click.echo(f"{Fore.BLUE}Preview mode - Issues found:")
            for issue in issues:
                click.echo(f"  - {issue['type']} ({issue['severity']})")
            
            if not issues:
                click.echo(f"{Fore.GREEN}No issues detected!")
                
        except Exception as e:
            click.echo(f"{Fore.RED}Error reading file: {e}")
    else:
        # Normal processing
        cleaner.process_file(input_file, output, aggressive)

if __name__ == '__main__':
    main()
