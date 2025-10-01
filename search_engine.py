#!/usr/bin/env python3
"""
Search engine for Islamic texts, specifically designed for fiqh studies.
Provides full-text search, semantic search, and Islamic terminology recognition.
"""

import json
import re
import sqlite3
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from collections import defaultdict
import click
from colorama import init, Fore, Style
import hashlib

init(autoreset=True)

class IslamicSearchEngine:
    """Search engine optimized for Islamic texts and fiqh studies."""
    
    def __init__(self, segments_dir: Path):
        self.segments_dir = segments_dir
        self.db_path = segments_dir / 'search_index.db'
        self.metadata = self.load_metadata()
        
        # Islamic terminology patterns
        self.islamic_terms = {
            'arabic': [
                'الله', 'محمد', 'رسول', 'صلى', 'عليه', 'وسلم', 'رضي', 'عنه', 'عنها',
                'عنهما', 'عنهم', 'قال', 'قيل', 'أو', 'إما', 'إذ', 'إذا', 'إن', 'أن',
                'بسم', 'الرحمن', 'الرحيم', 'الحمد', 'لله', 'رب', 'العالمين', 'الصلاة',
                'الزكاة', 'الصوم', 'الحج', 'الطهارة', 'الوضوء', 'الغسل', 'الجنابة'
            ],
            'transliterated': [
                'Allah', 'Muhammad', 'Rasulullah', 'sallallahu', 'alayhi', 'wasallam',
                'radiyallahu', 'anhu', 'anha', 'anhuma', 'anhum', 'qala', 'qila',
                'bismillah', 'rahman', 'raheem', 'hamd', 'rabb', 'alameen', 'salah',
                'zakat', 'sawm', 'hajj', 'taharah', 'wudu', 'ghusl', 'janabah'
            ],
            'fiqh_terms': [
                'wajib', 'sunnah', 'mustahabb', 'makruh', 'haram', 'mubah', 'fard',
                'nafl', 'qada', 'kafarah', 'fidyah', 'nifas', 'hayd', 'istihadah',
                'tayammum', 'masah', 'mukallaf', 'aqil', 'baligh', 'mukallaf'
            ]
        }
        
        # Search patterns
        self.patterns = {
            'arabic_text': r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]',
            'islamic_phrases': r'(?:sallallahu\s+alayhi\s+wasallam|radiyallahu\s+(?:anhu|anha|anhuma|anhum))',
            'chapter_reference': r'(?:chapter|bab|fasl|maqalah)\s*(\d+)',
            'verse_reference': r'(?:ayah|verse|ayat)\s*(\d+)',
            'hadith_reference': r'(?:hadith|sunnah|riwayah)',
        }

    def load_metadata(self) -> Dict:
        """Load metadata from segments directory."""
        metadata_file = self.segments_dir / 'metadata.json'
        if metadata_file.exists():
            with open(metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def create_database(self) -> None:
        """Create SQLite database for search index."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY,
                book_number INTEGER,
                title TEXT,
                start_line INTEGER,
                end_line INTEGER,
                line_count INTEGER
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chapters (
                id INTEGER PRIMARY KEY,
                book_id INTEGER,
                chapter_number INTEGER,
                title TEXT,
                start_line INTEGER,
                end_line INTEGER,
                line_count INTEGER,
                content TEXT,
                content_hash TEXT,
                FOREIGN KEY (book_id) REFERENCES books (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_index (
                id INTEGER PRIMARY KEY,
                chapter_id INTEGER,
                word TEXT,
                position INTEGER,
                context TEXT,
                is_islamic_term BOOLEAN,
                term_type TEXT,
                FOREIGN KEY (chapter_id) REFERENCES chapters (id)
            )
        ''')
        
        # Create indexes for faster search
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_word ON search_index (word)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_chapter_id ON search_index (chapter_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_islamic_term ON search_index (is_islamic_term)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_term_type ON search_index (term_type)')
        
        conn.commit()
        conn.close()

    def index_text(self) -> None:
        """Index all text content for search."""
        click.echo(f"{Fore.BLUE}Creating search index...")
        
        # Create database
        self.create_database()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Clear existing data
        cursor.execute('DELETE FROM search_index')
        cursor.execute('DELETE FROM chapters')
        cursor.execute('DELETE FROM books')
        
        # Index each book
        for book_dir in sorted(self.segments_dir.glob('book_*')):
            if not book_dir.is_dir():
                continue
                
            book_meta_file = book_dir / 'metadata.json'
            if not book_meta_file.exists():
                continue
                
            with open(book_meta_file, 'r', encoding='utf-8') as f:
                book_meta = json.load(f)
            
            # Insert book
            cursor.execute('''
                INSERT INTO books (book_number, title, start_line, end_line, line_count)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                book_meta['book_number'],
                book_meta['title'],
                book_meta['start_line'],
                book_meta['end_line'],
                book_meta['line_count']
            ))
            
            book_id = cursor.lastrowid
            
            # Index each chapter
            for chapter_meta in book_meta['chapters']:
                chapter_file = book_dir / chapter_meta['filename']
                if not chapter_file.exists():
                    continue
                
                # Read chapter content
                with open(chapter_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Create content hash
                content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
                
                # Insert chapter
                cursor.execute('''
                    INSERT INTO chapters (book_id, chapter_number, title, start_line, end_line, line_count, content, content_hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    book_id,
                    chapter_meta['chapter_number'],
                    chapter_meta['title'],
                    chapter_meta['start_line'],
                    chapter_meta['end_line'],
                    chapter_meta['line_count'],
                    content,
                    content_hash
                ))
                
                chapter_id = cursor.lastrowid
                
                # Index words in chapter
                self.index_chapter_content(cursor, chapter_id, content)
        
        conn.commit()
        conn.close()
        
        click.echo(f"{Fore.GREEN}✓ Search index created successfully!")

    def index_chapter_content(self, cursor, chapter_id: int, content: str) -> None:
        """Index words in a chapter for search."""
        # Split content into words
        words = re.findall(r'\b\w+\b', content.lower())
        
        for position, word in enumerate(words):
            # Check if it's an Islamic term
            is_islamic_term = False
            term_type = None
            
            if word in [term.lower() for term in self.islamic_terms['transliterated']]:
                is_islamic_term = True
                term_type = 'transliterated'
            elif word in [term.lower() for term in self.islamic_terms['fiqh_terms']]:
                is_islamic_term = True
                term_type = 'fiqh'
            
            # Get context (surrounding words)
            start = max(0, position - 3)
            end = min(len(words), position + 4)
            context = ' '.join(words[start:end])
            
            # Insert into search index
            cursor.execute('''
                INSERT INTO search_index (chapter_id, word, position, context, is_islamic_term, term_type)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (chapter_id, word, position, context, is_islamic_term, term_type))

    def search(self, query: str, search_type: str = 'full_text', 
               book_filter: Optional[str] = None, limit: int = 20) -> List[Dict]:
        """Search the indexed content."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if search_type == 'full_text':
            results = self.full_text_search(cursor, query, book_filter, limit)
        elif search_type == 'islamic_terms':
            results = self.islamic_terms_search(cursor, query, book_filter, limit)
        elif search_type == 'exact_phrase':
            results = self.exact_phrase_search(cursor, query, book_filter, limit)
        else:
            results = self.full_text_search(cursor, query, book_filter, limit)
        
        conn.close()
        return results

    def full_text_search(self, cursor, query: str, book_filter: Optional[str], limit: int) -> List[Dict]:
        """Perform full-text search."""
        query_words = query.lower().split()
        
        # Build SQL query
        sql = '''
            SELECT DISTINCT c.id, c.title, c.content, b.title as book_title, 
                   c.chapter_number, c.start_line, c.end_line,
                   GROUP_CONCAT(si.context) as contexts
            FROM chapters c
            JOIN books b ON c.book_id = b.id
            JOIN search_index si ON c.id = si.chapter_id
            WHERE '''
        
        conditions = []
        params = []
        
        for word in query_words:
            conditions.append('si.word LIKE ?')
            params.append(f'%{word}%')
        
        sql += ' AND '.join(conditions)
        
        if book_filter:
            sql += ' AND b.title LIKE ?'
            params.append(f'%{book_filter}%')
        
        sql += '''
            GROUP BY c.id
            ORDER BY 
                CASE WHEN si.word = ? THEN 1 ELSE 2 END,
                c.chapter_number
            LIMIT ?
        '''
        params.extend([query_words[0], limit])
        
        cursor.execute(sql, params)
        results = []
        
        for row in cursor.fetchall():
            results.append({
                'chapter_id': row[0],
                'title': row[1],
                'content': row[2],
                'book_title': row[3],
                'chapter_number': row[4],
                'start_line': row[5],
                'end_line': row[6],
                'contexts': row[7].split(',') if row[7] else [],
                'match_type': 'full_text'
            })
        
        return results

    def islamic_terms_search(self, cursor, query: str, book_filter: Optional[str], limit: int) -> List[Dict]:
        """Search for Islamic terms specifically."""
        sql = '''
            SELECT DISTINCT c.id, c.title, c.content, b.title as book_title,
                   c.chapter_number, c.start_line, c.end_line,
                   GROUP_CONCAT(si.context) as contexts
            FROM chapters c
            JOIN books b ON c.book_id = b.id
            JOIN search_index si ON c.id = si.chapter_id
            WHERE si.is_islamic_term = 1 AND si.word LIKE ?
        '''
        
        params = [f'%{query.lower()}%']
        
        if book_filter:
            sql += ' AND b.title LIKE ?'
            params.append(f'%{book_filter}%')
        
        sql += '''
            GROUP BY c.id
            ORDER BY c.chapter_number
            LIMIT ?
        '''
        params.append(limit)
        
        cursor.execute(sql, params)
        results = []
        
        for row in cursor.fetchall():
            results.append({
                'chapter_id': row[0],
                'title': row[1],
                'content': row[2],
                'book_title': row[3],
                'chapter_number': row[4],
                'start_line': row[5],
                'end_line': row[6],
                'contexts': row[7].split(',') if row[7] else [],
                'match_type': 'islamic_terms'
            })
        
        return results

    def exact_phrase_search(self, cursor, query: str, book_filter: Optional[str], limit: int) -> List[Dict]:
        """Search for exact phrases."""
        # This is a simplified version - in practice, you'd want more sophisticated phrase matching
        return self.full_text_search(cursor, query, book_filter, limit)

    def get_chapter(self, chapter_id: int) -> Optional[Dict]:
        """Get a specific chapter by ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT c.id, c.title, c.content, b.title as book_title,
                   c.chapter_number, c.start_line, c.end_line, c.line_count
            FROM chapters c
            JOIN books b ON c.book_id = b.id
            WHERE c.id = ?
        ''', (chapter_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'chapter_id': row[0],
                'title': row[1],
                'content': row[2],
                'book_title': row[3],
                'chapter_number': row[4],
                'start_line': row[5],
                'end_line': row[6],
                'line_count': row[7]
            }
        return None

    def get_book_chapters(self, book_title: str) -> List[Dict]:
        """Get all chapters in a book."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT c.id, c.title, c.chapter_number, c.start_line, c.end_line, c.line_count
            FROM chapters c
            JOIN books b ON c.book_id = b.id
            WHERE b.title LIKE ?
            ORDER BY c.chapter_number
        ''', (f'%{book_title}%',))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'chapter_id': row[0],
                'title': row[1],
                'chapter_number': row[2],
                'start_line': row[3],
                'end_line': row[4],
                'line_count': row[5]
            })
        
        conn.close()
        return results

    def get_statistics(self) -> Dict:
        """Get search engine statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get counts
        cursor.execute('SELECT COUNT(*) FROM books')
        book_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM chapters')
        chapter_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM search_index')
        word_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM search_index WHERE is_islamic_term = 1')
        islamic_term_count = cursor.fetchone()[0]
        
        # Get book titles
        cursor.execute('SELECT title FROM books ORDER BY book_number')
        books = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            'total_books': book_count,
            'total_chapters': chapter_count,
            'total_words_indexed': word_count,
            'islamic_terms_indexed': islamic_term_count,
            'books': books
        }

@click.command()
@click.argument('segments_dir', type=click.Path(exists=True, path_type=Path))
@click.option('--index', '-i', is_flag=True, help='Create search index')
@click.option('--search', '-s', type=str, help='Search query')
@click.option('--type', '-t', type=click.Choice(['full_text', 'islamic_terms', 'exact_phrase']), 
              default='full_text', help='Search type')
@click.option('--book', '-b', type=str, help='Filter by book title')
@click.option('--limit', '-l', type=int, default=20, help='Maximum results')
@click.option('--stats', is_flag=True, help='Show search engine statistics')
def main(segments_dir: Path, index: bool, search: Optional[str], type: str, 
         book: Optional[str], limit: int, stats: bool):
    """Search engine for Islamic texts."""
    
    engine = IslamicSearchEngine(segments_dir)
    
    if index:
        engine.index_text()
    
    if stats:
        stats_data = engine.get_statistics()
        click.echo(f"{Fore.BLUE}Search Engine Statistics:")
        click.echo(f"  Books: {stats_data['total_books']}")
        click.echo(f"  Chapters: {stats_data['total_chapters']}")
        click.echo(f"  Words indexed: {stats_data['total_words_indexed']:,}")
        click.echo(f"  Islamic terms: {stats_data['islamic_terms_indexed']:,}")
        click.echo(f"  Books: {', '.join(stats_data['books'])}")
    
    if search:
        click.echo(f"{Fore.BLUE}Searching for: '{search}'")
        if book:
            click.echo(f"{Fore.BLUE}In book: {book}")
        
        results = engine.search(search, type, book, limit)
        
        if results:
            click.echo(f"{Fore.GREEN}Found {len(results)} results:")
            click.echo("=" * 60)
            
            for i, result in enumerate(results, 1):
                click.echo(f"{Fore.CYAN}{i}. {result['book_title']} - Chapter {result['chapter_number']}: {result['title']}")
                click.echo(f"{Fore.YELLOW}   Lines: {result['start_line']}-{result['end_line']}")
                
                # Show context
                if result['contexts']:
                    context = result['contexts'][0][:100] + "..." if len(result['contexts'][0]) > 100 else result['contexts'][0]
                    click.echo(f"{Fore.WHITE}   Context: {context}")
                
                click.echo()
        else:
            click.echo(f"{Fore.RED}No results found.")

if __name__ == '__main__':
    main()
