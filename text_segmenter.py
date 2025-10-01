#!/usr/bin/env python3
"""
Text segmentation tool for Islamic texts, specifically designed to split
Nur al-Idah and similar fiqh texts into books and chapters.
"""

import re
import json
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import click
from colorama import init, Fore, Style

init(autoreset=True)

class TextSegmenter:
    """Segments Islamic texts into books and chapters."""
    
    def __init__(self):
        self.segments = {
            'books': [],
            'chapters': [],
            'metadata': {
                'total_books': 0,
                'total_chapters': 0,
                'total_lines': 0,
                'segmentation_quality': 0
            }
        }
        
        # Patterns for identifying structure
        self.patterns = {
            'main_book': r'^\* BOOK [IVX]+ - (.+)$',
            'book_header': r'^BOOK [IVX]+: ([A-Z]+)$',
            'chapter_header': r'^BOOK [IVX]+: ([A-Z]+) (\d+)$',
            'arabic_chapter': r'^(\d+) BOOK [IVX]+: ([A-Z]+)$',
            'chapter_title': r'^The Chapter Of (.+)$',
            'section_number': r'^(\d+)\.',
        }

    def identify_structure(self, text: str) -> Dict:
        """Identify the structure of the text."""
        lines = text.split('\n')
        structure = {
            'main_books': [],
            'book_headers': [],
            'chapter_headers': [],
            'arabic_chapters': [],
            'chapter_titles': []
        }
        
        for i, line in enumerate(lines):
            line_clean = line.strip()
            
            # Main book markers
            if re.match(self.patterns['main_book'], line_clean):
                match = re.match(self.patterns['main_book'], line_clean)
                structure['main_books'].append({
                    'line': i + 1,
                    'title': match.group(1),
                    'content': line_clean
                })
            
            # Book headers
            elif re.match(self.patterns['book_header'], line_clean):
                match = re.match(self.patterns['book_header'], line_clean)
                structure['book_headers'].append({
                    'line': i + 1,
                    'book': match.group(1),
                    'content': line_clean
                })
            
            # Chapter headers with numbers
            elif re.match(self.patterns['chapter_header'], line_clean):
                match = re.match(self.patterns['chapter_header'], line_clean)
                structure['chapter_headers'].append({
                    'line': i + 1,
                    'book': match.group(1),
                    'chapter': match.group(2),
                    'content': line_clean
                })
            
            # Arabic numbered chapters
            elif re.match(self.patterns['arabic_chapter'], line_clean):
                match = re.match(self.patterns['arabic_chapter'], line_clean)
                structure['arabic_chapters'].append({
                    'line': i + 1,
                    'chapter': match.group(1),
                    'book': match.group(2),
                    'content': line_clean
                })
            
            # Chapter titles
            elif re.match(self.patterns['chapter_title'], line_clean):
                match = re.match(self.patterns['chapter_title'], line_clean)
                structure['chapter_titles'].append({
                    'line': i + 1,
                    'title': match.group(1),
                    'content': line_clean
                })
        
        return structure

    def segment_into_books(self, text: str) -> List[Dict]:
        """Segment text into main books."""
        lines = text.split('\n')
        books = []
        
        # Find actual book start markers (not table of contents)
        book_markers = []
        for i, line in enumerate(lines):
            line_clean = line.strip()
            # Look for actual book headers, not table of contents
            if re.match(r'^BOOK [IVX]+: [A-Z]+$', line_clean):
                # Extract book name
                match = re.match(r'^BOOK [IVX]+: ([A-Z]+)$', line_clean)
                if match:
                    book_name = match.group(1)
                    # Only add if this is the first occurrence of this book
                    if not any(m['title'] == book_name for m in book_markers):
                        book_markers.append({
                            'line': i,
                            'title': book_name,
                            'content': line_clean
                        })
        
        # Segment into books
        for i, marker in enumerate(book_markers):
            start_line = marker['line']
            end_line = book_markers[i + 1]['line'] if i + 1 < len(book_markers) else len(lines)
            
            book_content = '\n'.join(lines[start_line:end_line])
            
            books.append({
                'book_number': i + 1,
                'title': marker['title'],
                'start_line': start_line + 1,
                'end_line': end_line,
                'content': book_content,
                'line_count': end_line - start_line
            })
        
        return books

    def segment_into_chapters(self, book_content: str, book_title: str) -> List[Dict]:
        """Segment a book into chapters."""
        lines = book_content.split('\n')
        chapters = []
        
        # Find chapter markers
        chapter_markers = []
        for i, line in enumerate(lines):
            line_clean = line.strip()
            
            # Look for various chapter patterns
            if (re.match(self.patterns['chapter_header'], line_clean) or
                re.match(self.patterns['arabic_chapter'], line_clean) or
                re.match(self.patterns['chapter_title'], line_clean)):
                chapter_markers.append({
                    'line': i,
                    'content': line_clean
                })
        
        # Segment into chapters
        for i, marker in enumerate(chapter_markers):
            start_line = marker['line']
            end_line = chapter_markers[i + 1]['line'] if i + 1 < len(chapter_markers) else len(lines)
            
            chapter_content = '\n'.join(lines[start_line:end_line])
            
            # Extract chapter title
            chapter_title = self.extract_chapter_title(marker['content'])
            
            chapters.append({
                'chapter_number': i + 1,
                'title': chapter_title,
                'start_line': start_line + 1,
                'end_line': end_line,
                'content': chapter_content,
                'line_count': end_line - start_line
            })
        
        return chapters

    def extract_chapter_title(self, content: str) -> str:
        """Extract a clean chapter title from the content."""
        # Try different patterns
        if re.match(self.patterns['chapter_title'], content):
            match = re.match(self.patterns['chapter_title'], content)
            return match.group(1)
        elif re.match(self.patterns['chapter_header'], content):
            match = re.match(self.patterns['chapter_header'], content)
            return f"{match.group(1)} - Chapter {match.group(2)}"
        elif re.match(self.patterns['arabic_chapter'], content):
            match = re.match(self.patterns['arabic_chapter'], content)
            return f"{match.group(2)} - Chapter {match.group(1)}"
        else:
            return content

    def segment_text(self, text: str) -> Dict:
        """Main segmentation function."""
        click.echo(f"{Fore.BLUE}Analyzing text structure...")
        
        # Identify structure
        structure = self.identify_structure(text)
        
        click.echo(f"{Fore.GREEN}Found {len(structure['main_books'])} main books")
        click.echo(f"{Fore.GREEN}Found {len(structure['book_headers'])} book headers")
        click.echo(f"{Fore.GREEN}Found {len(structure['chapter_headers'])} chapter headers")
        
        # Segment into books
        books = self.segment_into_books(text)
        
        # Segment each book into chapters
        all_chapters = []
        for book in books:
            click.echo(f"{Fore.CYAN}Segmenting {book['title']}...")
            chapters = self.segment_into_chapters(book['content'], book['title'])
            book['chapters'] = chapters
            all_chapters.extend(chapters)
            click.echo(f"  Found {len(chapters)} chapters")
        
        # Create final structure
        self.segments = {
            'books': books,
            'chapters': all_chapters,
            'metadata': {
                'total_books': len(books),
                'total_chapters': len(all_chapters),
                'total_lines': len(text.split('\n')),
                'segmentation_quality': self.calculate_quality_score(structure)
            }
        }
        
        return self.segments

    def calculate_quality_score(self, structure: Dict) -> int:
        """Calculate segmentation quality score."""
        score = 0
        
        # Base score for having main books
        if structure['main_books']:
            score += 30
        
        # Score for having book headers
        if structure['book_headers']:
            score += 20
        
        # Score for having chapter headers
        if structure['chapter_headers']:
            score += 30
        
        # Score for having chapter titles
        if structure['chapter_titles']:
            score += 20
        
        return min(score, 100)

    def save_segments(self, output_dir: Path) -> None:
        """Save segmented text to files."""
        output_dir.mkdir(exist_ok=True)
        
        # Save metadata
        with open(output_dir / 'metadata.json', 'w', encoding='utf-8') as f:
            json.dump(self.segments['metadata'], f, indent=2)
        
        # Save each book
        for book in self.segments['books']:
            book_dir = output_dir / f"book_{book['book_number']}"
            book_dir.mkdir(exist_ok=True)
            
            # Save book content
            with open(book_dir / 'book.txt', 'w', encoding='utf-8') as f:
                f.write(book['content'])
            
            # Save book metadata
            book_meta = {
                'book_number': book['book_number'],
                'title': book['title'],
                'start_line': book['start_line'],
                'end_line': book['end_line'],
                'line_count': book['line_count'],
                'chapters': []
            }
            
            # Save each chapter
            for chapter in book['chapters']:
                chapter_file = book_dir / f"chapter_{chapter['chapter_number']}.txt"
                with open(chapter_file, 'w', encoding='utf-8') as f:
                    f.write(chapter['content'])
                
                book_meta['chapters'].append({
                    'chapter_number': chapter['chapter_number'],
                    'title': chapter['title'],
                    'start_line': chapter['start_line'],
                    'end_line': chapter['end_line'],
                    'line_count': chapter['line_count'],
                    'filename': f"chapter_{chapter['chapter_number']}.txt"
                })
            
            # Save book metadata
            with open(book_dir / 'metadata.json', 'w', encoding='utf-8') as f:
                json.dump(book_meta, f, indent=2)
        
        click.echo(f"{Fore.GREEN}✓ Segmented text saved to {output_dir}")

    def generate_report(self) -> str:
        """Generate a segmentation report."""
        report = []
        report.append("=" * 60)
        report.append("TEXT SEGMENTATION REPORT")
        report.append("=" * 60)
        report.append("")
        
        # Metadata
        metadata = self.segments['metadata']
        report.append("SEGMENTATION METADATA")
        report.append("-" * 25)
        report.append(f"Total Books: {metadata['total_books']}")
        report.append(f"Total Chapters: {metadata['total_chapters']}")
        report.append(f"Total Lines: {metadata['total_lines']}")
        report.append(f"Quality Score: {metadata['segmentation_quality']}/100")
        report.append("")
        
        # Books
        report.append("BOOKS")
        report.append("-" * 10)
        for book in self.segments['books']:
            report.append(f"Book {book['book_number']}: {book['title']}")
            report.append(f"  Lines: {book['start_line']}-{book['end_line']} ({book['line_count']} lines)")
            report.append(f"  Chapters: {len(book['chapters'])}")
            report.append("")
        
        # Chapters summary
        report.append("CHAPTERS SUMMARY")
        report.append("-" * 20)
        for book in self.segments['books']:
            report.append(f"{book['title']}:")
            for chapter in book['chapters']:
                report.append(f"  Chapter {chapter['chapter_number']}: {chapter['title']}")
            report.append("")
        
        report.append("=" * 60)
        
        return "\n".join(report)

@click.command()
@click.argument('input_file', type=click.Path(exists=True, path_type=Path))
@click.option('--output', '-o', type=click.Path(path_type=Path), 
              help='Output directory for segmented text (default: input_file_segments)')
@click.option('--report', '-r', type=click.Path(path_type=Path), 
              help='Output file for segmentation report')
@click.option('--preview', '-p', is_flag=True, 
              help='Preview structure without segmenting')
def main(input_file: Path, output: Optional[Path], report: Optional[Path], preview: bool):
    """Segment Islamic text files into books and chapters."""
    
    if output is None:
        output = input_file.parent / f"{input_file.stem}_segments"
    
    segmenter = TextSegmenter()
    
    try:
        # Read the file
        with open(input_file, 'r', encoding='utf-8') as f:
            text = f.read()
        
        click.echo(f"{Fore.BLUE}Processing: {input_file}")
        click.echo(f"{Fore.BLUE}File size: {len(text):,} characters")
        
        if preview:
            # Preview mode - just show structure
            structure = segmenter.identify_structure(text)
            click.echo(f"{Fore.YELLOW}Structure preview:")
            click.echo(f"  Main books: {len(structure['main_books'])}")
            click.echo(f"  Book headers: {len(structure['book_headers'])}")
            click.echo(f"  Chapter headers: {len(structure['chapter_headers'])}")
            click.echo(f"  Arabic chapters: {len(structure['arabic_chapters'])}")
            click.echo(f"  Chapter titles: {len(structure['chapter_titles'])}")
            
            if structure['main_books']:
                click.echo(f"{Fore.CYAN}Main books found:")
                for book in structure['main_books']:
                    click.echo(f"  Line {book['line']}: {book['title']}")
        else:
            # Full segmentation
            segments = segmenter.segment_text(text)
            
            # Save segments
            segmenter.save_segments(output)
            
            # Generate and save report
            report_text = segmenter.generate_report()
            if report:
                with open(report, 'w', encoding='utf-8') as f:
                    f.write(report_text)
                click.echo(f"{Fore.GREEN}Report saved to: {report}")
            else:
                click.echo(report_text)
            
            click.echo(f"{Fore.GREEN}✓ Segmentation completed successfully!")
            
    except Exception as e:
        click.echo(f"{Fore.RED}Error processing file: {e}")

if __name__ == '__main__':
    main()
