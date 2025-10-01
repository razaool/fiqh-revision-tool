#!/usr/bin/env python3
"""
Text analysis tool for Islamic texts to identify patterns, issues, and quality metrics.
Helps understand the structure and content of texts like Nur al-Idah.
"""

import re
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Counter, Optional
from collections import Counter, defaultdict
import click
from colorama import init, Fore, Style

init(autoreset=True)

class TextAnalyzer:
    """Analyzes Islamic texts to provide insights and quality metrics."""
    
    def __init__(self):
        self.stats = {
            'total_chars': 0,
            'total_words': 0,
            'total_lines': 0,
            'arabic_chars': 0,
            'english_chars': 0,
            'numbers': 0,
            'punctuation': 0,
            'whitespace': 0,
        }
        
        # Common Islamic terms and phrases
        self.islamic_terms = {
            'arabic': [
                'الله', 'محمد', 'رسول', 'صلى', 'عليه', 'وسلم', 'رضي', 'عنه', 'عنها',
                'عنهما', 'عنهم', 'قال', 'قيل', 'أو', 'إما', 'إذ', 'إذا', 'إن', 'أن',
                'بسم', 'الرحمن', 'الرحيم', 'الحمد', 'لله', 'رب', 'العالمين'
            ],
            'transliterated': [
                'Allah', 'Muhammad', 'Rasulullah', 'sallallahu', 'alayhi', 'wasallam',
                'radiyallahu', 'anhu', 'anha', 'anhuma', 'anhum', 'qala', 'qila',
                'bismillah', 'rahman', 'raheem', 'hamd', 'rabb', 'alameen'
            ]
        }
        
        # Patterns for analysis
        self.patterns = {
            'arabic_text': r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]',
            'english_text': r'[a-zA-Z]',
            'numbers': r'[0-9\u0660-\u0669]',
            'punctuation': r'[.,!?;:()\[\]{}""''-]',
            'whitespace': r'\s',
            'islamic_phrases': r'(?:sallallahu\s+alayhi\s+wasallam|radiyallahu\s+(?:anhu|anha|anhuma|anhum))',
            'chapter_markers': r'(?:باب|فصل|مبحث|كتاب)',
            'verse_markers': r'(?:آية|حديث|رواية)',
        }

    def analyze_text(self, text: str) -> Dict:
        """Comprehensive text analysis."""
        analysis = {
            'basic_stats': self._get_basic_stats(text),
            'language_distribution': self._analyze_language_distribution(text),
            'islamic_content': self._analyze_islamic_content(text),
            'structure_analysis': self._analyze_structure(text),
            'quality_metrics': self._calculate_quality_metrics(text),
            'common_issues': self._detect_common_issues(text),
        }
        
        return analysis

    def _get_basic_stats(self, text: str) -> Dict:
        """Get basic text statistics."""
        stats = {
            'total_characters': len(text),
            'total_words': len(text.split()),
            'total_lines': len(text.splitlines()),
            'non_empty_lines': len([line for line in text.splitlines() if line.strip()]),
            'average_line_length': len(text) / len(text.splitlines()) if text.splitlines() else 0,
            'average_word_length': sum(len(word) for word in text.split()) / len(text.split()) if text.split() else 0,
        }
        
        return stats

    def _analyze_language_distribution(self, text: str) -> Dict:
        """Analyze the distribution of different languages and character types."""
        arabic_chars = len(re.findall(self.patterns['arabic_text'], text))
        english_chars = len(re.findall(self.patterns['english_text'], text))
        numbers = len(re.findall(self.patterns['numbers'], text))
        punctuation = len(re.findall(self.patterns['punctuation'], text))
        whitespace = len(re.findall(self.patterns['whitespace'], text))
        
        total_chars = len(text)
        
        return {
            'arabic_percentage': (arabic_chars / total_chars * 100) if total_chars > 0 else 0,
            'english_percentage': (english_chars / total_chars * 100) if total_chars > 0 else 0,
            'numbers_percentage': (numbers / total_chars * 100) if total_chars > 0 else 0,
            'punctuation_percentage': (punctuation / total_chars * 100) if total_chars > 0 else 0,
            'whitespace_percentage': (whitespace / total_chars * 100) if total_chars > 0 else 0,
            'arabic_count': arabic_chars,
            'english_count': english_chars,
            'numbers_count': numbers,
            'punctuation_count': punctuation,
            'whitespace_count': whitespace,
        }

    def _analyze_islamic_content(self, text: str) -> Dict:
        """Analyze Islamic-specific content and terminology."""
        # Count Islamic phrases
        islamic_phrases = len(re.findall(self.patterns['islamic_phrases'], text, re.IGNORECASE))
        
        # Count Arabic Islamic terms
        arabic_terms_found = []
        for term in self.islamic_terms['arabic']:
            count = text.count(term)
            if count > 0:
                arabic_terms_found.append({'term': term, 'count': count})
        
        # Count transliterated terms
        transliterated_terms_found = []
        for term in self.islamic_terms['transliterated']:
            count = len(re.findall(r'\b' + re.escape(term) + r'\b', text, re.IGNORECASE))
            if count > 0:
                transliterated_terms_found.append({'term': term, 'count': count})
        
        return {
            'islamic_phrases_count': islamic_phrases,
            'arabic_terms_found': arabic_terms_found,
            'transliterated_terms_found': transliterated_terms_found,
            'total_islamic_terms': len(arabic_terms_found) + len(transliterated_terms_found),
        }

    def _analyze_structure(self, text: str) -> Dict:
        """Analyze the structural elements of the text."""
        # Count chapter markers
        chapter_markers = len(re.findall(self.patterns['chapter_markers'], text, re.IGNORECASE))
        
        # Count verse/reference markers
        verse_markers = len(re.findall(self.patterns['verse_markers'], text, re.IGNORECASE))
        
        # Analyze paragraph structure
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        # Analyze line structure
        lines = text.splitlines()
        non_empty_lines = [line for line in lines if line.strip()]
        
        return {
            'chapter_markers_count': chapter_markers,
            'verse_markers_count': verse_markers,
            'paragraphs_count': len(paragraphs),
            'average_paragraph_length': sum(len(p) for p in paragraphs) / len(paragraphs) if paragraphs else 0,
            'lines_count': len(lines),
            'non_empty_lines_count': len(non_empty_lines),
            'empty_lines_count': len(lines) - len(non_empty_lines),
        }

    def _calculate_quality_metrics(self, text: str) -> Dict:
        """Calculate text quality metrics."""
        # Check for common quality issues
        multiple_spaces = len(re.findall(r'\s{2,}', text))
        multiple_punctuation = len(re.findall(r'[.]{2,}|[!]{2,}|[?]{2,}', text))
        mixed_quotes = len(re.findall(r'[""''„"‚\']', text))
        tabs = text.count('\t')
        bom = text.count('\ufeff')
        
        # Calculate quality score (0-100)
        quality_score = 100
        quality_score -= min(multiple_spaces * 2, 20)  # Penalize multiple spaces
        quality_score -= min(multiple_punctuation * 5, 20)  # Penalize multiple punctuation
        quality_score -= min(mixed_quotes * 3, 15)  # Penalize mixed quotes
        quality_score -= min(tabs * 2, 10)  # Penalize tabs
        quality_score -= min(bom * 10, 10)  # Penalize BOM
        
        return {
            'quality_score': max(quality_score, 0),
            'multiple_spaces_count': multiple_spaces,
            'multiple_punctuation_count': multiple_punctuation,
            'mixed_quotes_count': mixed_quotes,
            'tabs_count': tabs,
            'bom_count': bom,
            'encoding_issues': bom > 0,
        }

    def _detect_common_issues(self, text: str) -> List[Dict]:
        """Detect common text issues."""
        issues = []
        
        # Check for encoding issues
        if '\ufeff' in text:
            issues.append({
                'type': 'BOM_character',
                'severity': 'high',
                'description': 'Byte Order Mark found at beginning of file',
                'count': text.count('\ufeff')
            })
        
        # Check for multiple spaces
        multiple_spaces = len(re.findall(r'\s{2,}', text))
        if multiple_spaces > 0:
            issues.append({
                'type': 'multiple_spaces',
                'severity': 'low',
                'description': 'Multiple consecutive spaces found',
                'count': multiple_spaces
            })
        
        # Check for tabs
        tabs = text.count('\t')
        if tabs > 0:
            issues.append({
                'type': 'tabs',
                'severity': 'low',
                'description': 'Tab characters found (should be spaces)',
                'count': tabs
            })
        
        # Check for mixed quotes
        mixed_quotes = len(re.findall(r'[""''„"‚\']', text))
        if mixed_quotes > 0:
            issues.append({
                'type': 'mixed_quotes',
                'severity': 'medium',
                'description': 'Mixed quote types found',
                'count': mixed_quotes
            })
        
        # Check for multiple punctuation
        multiple_punctuation = len(re.findall(r'[.]{2,}|[!]{2,}|[?]{2,}', text))
        if multiple_punctuation > 0:
            issues.append({
                'type': 'multiple_punctuation',
                'severity': 'medium',
                'description': 'Multiple consecutive punctuation marks',
                'count': multiple_punctuation
            })
        
        return issues

    def generate_report(self, analysis: Dict, output_file: Optional[Path] = None) -> str:
        """Generate a comprehensive analysis report."""
        report = []
        report.append("=" * 60)
        report.append("ISLAMIC TEXT ANALYSIS REPORT")
        report.append("=" * 60)
        report.append("")
        
        # Basic Statistics
        report.append("BASIC STATISTICS")
        report.append("-" * 20)
        stats = analysis['basic_stats']
        report.append(f"Total Characters: {stats['total_characters']:,}")
        report.append(f"Total Words: {stats['total_words']:,}")
        report.append(f"Total Lines: {stats['total_lines']:,}")
        report.append(f"Non-empty Lines: {stats['non_empty_lines']:,}")
        report.append(f"Average Line Length: {stats['average_line_length']:.1f} characters")
        report.append(f"Average Word Length: {stats['average_word_length']:.1f} characters")
        report.append("")
        
        # Language Distribution
        report.append("LANGUAGE DISTRIBUTION")
        report.append("-" * 25)
        lang = analysis['language_distribution']
        report.append(f"Arabic Characters: {lang['arabic_count']:,} ({lang['arabic_percentage']:.1f}%)")
        report.append(f"English Characters: {lang['english_count']:,} ({lang['english_percentage']:.1f}%)")
        report.append(f"Numbers: {lang['numbers_count']:,} ({lang['numbers_percentage']:.1f}%)")
        report.append(f"Punctuation: {lang['punctuation_count']:,} ({lang['punctuation_percentage']:.1f}%)")
        report.append(f"Whitespace: {lang['whitespace_count']:,} ({lang['whitespace_percentage']:.1f}%)")
        report.append("")
        
        # Islamic Content
        report.append("ISLAMIC CONTENT ANALYSIS")
        report.append("-" * 30)
        islamic = analysis['islamic_content']
        report.append(f"Islamic Phrases Found: {islamic['islamic_phrases_count']}")
        report.append(f"Arabic Terms Found: {len(islamic['arabic_terms_found'])}")
        report.append(f"Transliterated Terms Found: {len(islamic['transliterated_terms_found'])}")
        report.append("")
        
        if islamic['arabic_terms_found']:
            report.append("Top Arabic Terms:")
            for term_info in sorted(islamic['arabic_terms_found'], key=lambda x: x['count'], reverse=True)[:10]:
                report.append(f"  {term_info['term']}: {term_info['count']}")
            report.append("")
        
        if islamic['transliterated_terms_found']:
            report.append("Top Transliterated Terms:")
            for term_info in sorted(islamic['transliterated_terms_found'], key=lambda x: x['count'], reverse=True)[:10]:
                report.append(f"  {term_info['term']}: {term_info['count']}")
            report.append("")
        
        # Structure Analysis
        report.append("STRUCTURE ANALYSIS")
        report.append("-" * 20)
        structure = analysis['structure_analysis']
        report.append(f"Chapter Markers: {structure['chapter_markers_count']}")
        report.append(f"Verse/Reference Markers: {structure['verse_markers_count']}")
        report.append(f"Paragraphs: {structure['paragraphs_count']}")
        report.append(f"Average Paragraph Length: {structure['average_paragraph_length']:.1f} characters")
        report.append(f"Empty Lines: {structure['empty_lines_count']}")
        report.append("")
        
        # Quality Metrics
        report.append("QUALITY METRICS")
        report.append("-" * 17)
        quality = analysis['quality_metrics']
        report.append(f"Quality Score: {quality['quality_score']}/100")
        report.append(f"Multiple Spaces: {quality['multiple_spaces_count']}")
        report.append(f"Multiple Punctuation: {quality['multiple_punctuation_count']}")
        report.append(f"Mixed Quotes: {quality['mixed_quotes_count']}")
        report.append(f"Tab Characters: {quality['tabs_count']}")
        report.append(f"BOM Characters: {quality['bom_count']}")
        report.append("")
        
        # Issues
        report.append("DETECTED ISSUES")
        report.append("-" * 17)
        issues = analysis['common_issues']
        if issues:
            for issue in issues:
                severity_color = {
                    'high': Fore.RED,
                    'medium': Fore.YELLOW,
                    'low': Fore.GREEN
                }.get(issue['severity'], Fore.WHITE)
                
                report.append(f"{severity_color}{issue['type'].upper()} ({issue['severity']})")
                report.append(f"  Description: {issue['description']}")
                report.append(f"  Count: {issue['count']}")
                report.append("")
        else:
            report.append("No issues detected!")
            report.append("")
        
        report.append("=" * 60)
        
        report_text = "\n".join(report)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_text)
            click.echo(f"{Fore.GREEN}Report saved to: {output_file}")
        
        return report_text

@click.command()
@click.argument('input_file', type=click.Path(exists=True, path_type=Path))
@click.option('--output', '-o', type=click.Path(path_type=Path), 
              help='Output file for the analysis report')
@click.option('--verbose', '-v', is_flag=True, 
              help='Show detailed output')
def main(input_file: Path, output: Optional[Path], verbose: bool):
    """Analyze Islamic text files to understand structure, content, and quality."""
    
    analyzer = TextAnalyzer()
    
    try:
        # Read the file
        with open(input_file, 'r', encoding='utf-8') as f:
            text = f.read()
        
        if verbose:
            click.echo(f"{Fore.BLUE}Analyzing file: {input_file}")
            click.echo(f"{Fore.BLUE}File size: {len(text):,} characters")
        
        # Perform analysis
        analysis = analyzer.analyze_text(text)
        
        # Generate and display report
        report = analyzer.generate_report(analysis, output)
        
        if verbose or not output:
            click.echo(report)
        
        if not verbose and output:
            click.echo(f"{Fore.GREEN}Analysis completed! Report saved to: {output}")
            
    except Exception as e:
        click.echo(f"{Fore.RED}Error analyzing file: {e}")

if __name__ == '__main__':
    main()
