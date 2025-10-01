#!/usr/bin/env python3
"""
Simple search script for quick use
"""

import sys
from pathlib import Path
from search_engine import IslamicSearchEngine

def main():
    if len(sys.argv) < 3:
        print("Usage: python search_text.py <segments_dir> <search_query> [search_type] [book_filter]")
        print("Example: python search_text.py segments_v2 'wudu' full_text 'PURIFICATION'")
        print("Search types: full_text, islamic_terms, exact_phrase")
        sys.exit(1)
    
    segments_dir = Path(sys.argv[1])
    search_query = sys.argv[2]
    search_type = sys.argv[3] if len(sys.argv) > 3 else 'full_text'
    book_filter = sys.argv[4] if len(sys.argv) > 4 else None
    
    if not segments_dir.exists():
        print(f"Error: Segments directory '{segments_dir}' does not exist.")
        sys.exit(1)
    
    engine = IslamicSearchEngine(segments_dir)
    
    try:
        # Create index if it doesn't exist
        if not engine.db_path.exists():
            print("Creating search index...")
            engine.index_text()
        
        print(f"Searching for: '{search_query}'")
        if book_filter:
            print(f"In book: {book_filter}")
        
        results = engine.search(search_query, search_type, book_filter, 10)
        
        if results:
            print(f"\nFound {len(results)} results:")
            print("=" * 60)
            
            for i, result in enumerate(results, 1):
                print(f"{i}. {result['book_title']} - Chapter {result['chapter_number']}: {result['title']}")
                print(f"   Lines: {result['start_line']}-{result['end_line']}")
                
                # Show context
                if result['contexts']:
                    context = result['contexts'][0][:150] + "..." if len(result['contexts'][0]) > 150 else result['contexts'][0]
                    print(f"   Context: {context}")
                
                print()
        else:
            print("No results found.")
            
    except Exception as e:
        print(f"Error searching: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
