#!/usr/bin/env python3
"""
Web interface for the Fiqh Revision Tool
Provides a simple web-based search interface for Islamic texts.
"""

import json
import os
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory
from search_engine import IslamicSearchEngine

app = Flask(__name__)

# Global search engine instance
search_engine = None

def init_search_engine(segments_dir: Path):
    """Initialize the search engine."""
    global search_engine
    search_engine = IslamicSearchEngine(segments_dir)
    
    # Create index if it doesn't exist
    if not search_engine.db_path.exists():
        print("Creating search index...")
        search_engine.index_text()

@app.route('/')
def index():
    """Main search page."""
    return render_template('index.html')

@app.route('/api/search', methods=['POST'])
def api_search():
    """API endpoint for search."""
    if not search_engine:
        return jsonify({'error': 'Search engine not initialized'}), 500
    
    data = request.get_json()
    query = data.get('query', '')
    search_type = data.get('type', 'full_text')
    book_filter = data.get('book', '')
    limit = data.get('limit', 20)
    
    if not query:
        return jsonify({'error': 'Query is required'}), 400
    
    try:
        results = search_engine.search(query, search_type, book_filter, limit)
        return jsonify({'results': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chapter/<int:chapter_id>')
def api_chapter(chapter_id):
    """API endpoint to get a specific chapter."""
    if not search_engine:
        return jsonify({'error': 'Search engine not initialized'}), 500
    
    try:
        chapter = search_engine.get_chapter(chapter_id)
        if chapter:
            return jsonify(chapter)
        else:
            return jsonify({'error': 'Chapter not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/book/<book_title>')
def api_book_chapters(book_title):
    """API endpoint to get all chapters in a book."""
    if not search_engine:
        return jsonify({'error': 'Search engine not initialized'}), 500
    
    try:
        chapters = search_engine.get_book_chapters(book_title)
        return jsonify({'chapters': chapters})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats')
def api_stats():
    """API endpoint for search engine statistics."""
    if not search_engine:
        return jsonify({'error': 'Search engine not initialized'}), 500
    
    try:
        stats = search_engine.get_statistics()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def create_templates():
    """Create HTML templates for the web interface."""
    templates_dir = Path('templates')
    templates_dir.mkdir(exist_ok=True)
    
    # Main search page
    index_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fiqh Revision Tool - Search</title>
    <style>
        :root {
            --bg-primary: #1a1a1a;
            --bg-secondary: #2d2d2d;
            --bg-tertiary: #3a3a3a;
            --text-primary: #e0e0e0;
            --text-secondary: #b0b0b0;
            --text-muted: #888;
            --accent: #4a9eff;
            --accent-hover: #357abd;
            --border: #444;
            --border-light: #555;
            --success: #4caf50;
            --error: #f44336;
            --warning: #ff9800;
        }

        * {
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: var(--bg-secondary);
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            border: 1px solid var(--border);
        }
        
        h1 {
            color: var(--text-primary);
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
            font-weight: 300;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        
        .search-form {
            display: flex;
            gap: 12px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }
        
        .search-form input, .search-form select {
            padding: 14px 16px;
            border: 2px solid var(--border);
            border-radius: 8px;
            font-size: 16px;
            background: var(--bg-tertiary);
            color: var(--text-primary);
            transition: all 0.3s ease;
        }
        
        .search-form input:focus, .search-form select:focus {
            outline: none;
            border-color: var(--accent);
            box-shadow: 0 0 0 3px rgba(74, 158, 255, 0.1);
        }
        
        .search-form input[type="text"] {
            flex: 1;
            min-width: 300px;
        }
        
        .search-form input::placeholder {
            color: var(--text-muted);
        }
        
        .search-form button {
            padding: 14px 28px;
            background: linear-gradient(135deg, var(--accent), var(--accent-hover));
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 500;
            transition: all 0.3s ease;
            box-shadow: 0 2px 8px rgba(74, 158, 255, 0.3);
        }
        
        .search-form button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(74, 158, 255, 0.4);
        }
        
        .search-form button:active {
            transform: translateY(0);
        }
        
        .results {
            margin-top: 30px;
        }
        
        .result-item {
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 24px;
            margin-bottom: 16px;
            background: var(--bg-tertiary);
            transition: all 0.3s ease;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .result-item:hover {
            border-color: var(--accent);
            box-shadow: 0 4px 16px rgba(0,0,0,0.2);
            transform: translateY(-2px);
        }
        
        .result-title {
            font-size: 18px;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 12px;
            line-height: 1.4;
        }
        
        .result-meta {
            color: var(--text-secondary);
            font-size: 14px;
            margin-bottom: 12px;
            display: flex;
            gap: 16px;
            flex-wrap: wrap;
        }
        
        .result-meta span {
            background: var(--bg-primary);
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
        }
        
        .result-context {
            color: var(--text-primary);
            line-height: 1.6;
            background: var(--bg-primary);
            padding: 16px;
            border-radius: 6px;
            border-left: 4px solid var(--accent);
        }
        
        .loading {
            text-align: center;
            color: var(--text-secondary);
            font-style: italic;
            padding: 40px;
            font-size: 18px;
        }
        
        .error {
            color: var(--error);
            background: rgba(244, 67, 54, 0.1);
            padding: 20px;
            border-radius: 8px;
            border: 1px solid rgba(244, 67, 54, 0.3);
            margin: 20px 0;
        }
        
        .stats {
            background: var(--bg-tertiary);
            padding: 24px;
            border-radius: 8px;
            margin-bottom: 30px;
            border: 1px solid var(--border);
        }
        
        .stats h3 {
            margin-top: 0;
            color: var(--text-primary);
            font-size: 1.3em;
            font-weight: 500;
            margin-bottom: 16px;
        }
        
        .stats p {
            margin: 8px 0;
            color: var(--text-secondary);
        }
        
        .stats strong {
            color: var(--accent);
        }
        
        /* Scrollbar styling */
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: var(--bg-primary);
        }
        
        ::-webkit-scrollbar-thumb {
            background: var(--border);
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: var(--border-light);
        }
        
        /* Responsive design */
        @media (max-width: 768px) {
            .container {
                padding: 20px;
                margin: 10px;
            }
            
            .search-form {
                flex-direction: column;
            }
            
            .search-form input[type="text"] {
                min-width: auto;
            }
            
            h1 {
                font-size: 2em;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📚 Fiqh Revision Tool</h1>
        
        <div class="stats" id="stats">
            <h3>Search Engine Statistics</h3>
            <div id="stats-content">Loading...</div>
        </div>
        
        <form class="search-form" id="searchForm">
            <input type="text" id="query" placeholder="Search for Islamic terms, concepts, or phrases..." required>
            <select id="type">
                <option value="full_text">Full Text Search</option>
                <option value="islamic_terms">Islamic Terms</option>
                <option value="exact_phrase">Exact Phrase</option>
            </select>
            <select id="book">
                <option value="">All Books</option>
                <option value="PURIFICATION">Purification</option>
                <option value="PRAYER">Prayer</option>
            </select>
            <button type="submit">Search</button>
        </form>
        
        <div class="results" id="results"></div>
    </div>

    <script>
        // Load statistics on page load
        fetch('/api/stats')
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    document.getElementById('stats-content').innerHTML = 
                        '<div class="error">Error loading statistics: ' + data.error + '</div>';
                } else {
                    document.getElementById('stats-content').innerHTML = 
                        '<p><strong>Books:</strong> ' + data.total_books + 
                        ' | <strong>Chapters:</strong> ' + data.total_chapters + 
                        ' | <strong>Words Indexed:</strong> ' + data.total_words_indexed.toLocaleString() + 
                        ' | <strong>Islamic Terms:</strong> ' + data.islamic_terms_indexed.toLocaleString() + '</p>';
                }
            })
            .catch(error => {
                document.getElementById('stats-content').innerHTML = 
                    '<div class="error">Error loading statistics: ' + error.message + '</div>';
            });

        // Handle search form submission
        document.getElementById('searchForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const query = document.getElementById('query').value;
            const type = document.getElementById('type').value;
            const book = document.getElementById('book').value;
            
            if (!query.trim()) {
                alert('Please enter a search query');
                return;
            }
            
            // Show loading
            document.getElementById('results').innerHTML = '<div class="loading">Searching...</div>';
            
            // Perform search
            fetch('/api/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: query,
                    type: type,
                    book: book,
                    limit: 20
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    document.getElementById('results').innerHTML = 
                        '<div class="error">Error: ' + data.error + '</div>';
                } else {
                    displayResults(data.results);
                }
            })
            .catch(error => {
                document.getElementById('results').innerHTML = 
                    '<div class="error">Error: ' + error.message + '</div>';
            });
        });
        
        function displayResults(results) {
            const resultsDiv = document.getElementById('results');
            
            if (results.length === 0) {
                resultsDiv.innerHTML = '<div class="error">No results found. Try a different search term.</div>';
                return;
            }
            
            let html = '<h3>Search Results (' + results.length + ')</h3>';
            
            results.forEach((result, index) => {
                html += '<div class="result-item">';
                html += '<div class="result-title">' + (index + 1) + '. ' + result.book_title + ' - Chapter ' + result.chapter_number + ': ' + result.title + '</div>';
                html += '<div class="result-meta">Lines: ' + result.start_line + '-' + result.end_line + ' | Match Type: ' + result.match_type + '</div>';
                
                if (result.contexts && result.contexts.length > 0) {
                    const context = result.contexts[0].length > 200 ? 
                        result.contexts[0].substring(0, 200) + '...' : 
                        result.contexts[0];
                    html += '<div class="result-context">' + context + '</div>';
                }
                
                html += '</div>';
            });
            
            resultsDiv.innerHTML = html;
        }
    </script>
</body>
</html>'''
    
    with open(templates_dir / 'index.html', 'w', encoding='utf-8') as f:
        f.write(index_html)

def main():
    """Main function to run the web interface."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Web interface for Fiqh Revision Tool')
    parser.add_argument('segments_dir', type=Path, help='Path to segments directory')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    if not args.segments_dir.exists():
        print(f"Error: Segments directory '{args.segments_dir}' does not exist.")
        return 1
    
    # Create templates
    create_templates()
    
    # Initialize search engine
    init_search_engine(args.segments_dir)
    
    print(f"Starting web interface...")
    print(f"Open your browser and go to: http://{args.host}:{args.port}")
    print("Press Ctrl+C to stop the server")
    
    # Run the Flask app
    app.run(host=args.host, port=args.port, debug=args.debug)
    
    return 0

if __name__ == '__main__':
    exit(main())
