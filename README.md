# Fiqh Revision Tool

A comprehensive text cleaning and analysis tool specifically designed for Islamic texts, with a focus on fiqh studies and Arabic content. This tool helps clean and analyze texts like Nur al-Idah by Shaykh Shurunbulali and other Islamic reference works.

## Features

### Text Cleaning (`text_cleaner.py`)
- **Unicode normalization** - Fixes encoding issues and normalizes characters
- **OCR error correction** - Automatically fixes common OCR mistakes in Arabic and transliterated text
- **Whitespace cleanup** - Removes multiple spaces, tabs, and normalizes line breaks
- **Punctuation fixes** - Corrects multiple punctuation marks and mixed quotes
- **Arabic text optimization** - Special handling for Arabic characters and diacritics
- **Interactive mode** - Manual review and confirmation of changes
- **Preview mode** - See issues without making changes

### Text Analysis (`text_analyzer.py`)
- **Comprehensive statistics** - Character, word, and line counts
- **Language distribution** - Analysis of Arabic vs English content
- **Islamic content detection** - Identifies Islamic terms, phrases, and references
- **Structure analysis** - Chapter markers, verse references, and paragraph structure
- **Quality metrics** - Text quality scoring and issue detection
- **Detailed reporting** - Comprehensive analysis reports

## Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Quick Start

#### Clean a text file:
```bash
python clean_text.py input_file.txt [output_file.txt]
```

#### Analyze a text file:
```bash
python analyze_text.py input_file.txt [report_file.txt]
```

### Advanced Usage

#### Text Cleaner
```bash
# Basic cleaning
python text_cleaner.py input_file.txt

# Specify output file
python text_cleaner.py input_file.txt -o cleaned_file.txt

# Aggressive cleaning (removes more characters)
python text_cleaner.py input_file.txt -a

# Interactive mode for manual review
python text_cleaner.py input_file.txt -i

# Preview issues without cleaning
python text_cleaner.py input_file.txt -p
```

#### Text Analyzer
```bash
# Basic analysis
python text_analyzer.py input_file.txt

# Save report to file
python text_analyzer.py input_file.txt -o report.txt

# Verbose output
python text_analyzer.py input_file.txt -v
```

## Workflow for Cleaning Islamic Texts

### 1. Initial Analysis
First, analyze your raw text to understand its current state:
```bash
python analyze_text.py nur_al_idah_raw.txt analysis_report.txt
```

### 2. Preview Issues
See what issues need to be fixed:
```bash
python text_cleaner.py nur_al_idah_raw.txt -p
```

### 3. Clean the Text
Clean the text with appropriate options:
```bash
# For most cases, basic cleaning is sufficient
python text_cleaner.py nur_al_idah_raw.txt -o nur_al_idah_cleaned.txt

# For heavily corrupted text, use aggressive cleaning
python text_cleaner.py nur_al_idah_raw.txt -o nur_al_idah_cleaned.txt -a
```

### 4. Verify Results
Analyze the cleaned text to verify quality:
```bash
python analyze_text.py nur_al_idah_cleaned.txt cleaned_analysis.txt
```

### 5. Manual Review (if needed)
For critical texts, use interactive mode for manual review:
```bash
python text_cleaner.py nur_al_idah_cleaned.txt -i
```

## Common Issues Fixed

### OCR Errors
- Arabic numeral corrections (0-9 → ٠-٩)
- Common transliteration fixes (allah → Allah, muhammad → Muhammad)
- Mixed character sets

### Formatting Issues
- Multiple consecutive spaces
- Tab characters
- Inconsistent line breaks
- Mixed quote types
- Multiple punctuation marks

### Encoding Issues
- Byte Order Mark (BOM) removal
- Unicode normalization
- Character encoding fixes

## Islamic Content Recognition

The tool recognizes and preserves:
- **Arabic terms**: الله، محمد، رسول، صلى، عليه، وسلم، رضي، عنه، etc.
- **Transliterated terms**: Allah, Muhammad, Rasulullah, sallallahu alayhi wasallam, etc.
- **Islamic phrases**: Common dua, salutations, and references
- **Structure markers**: باب، فصل، مبحث، كتاب، آية، حديث

## Quality Metrics

The analyzer provides a quality score (0-100) based on:
- Multiple spaces penalty
- Multiple punctuation penalty
- Mixed quotes penalty
- Tab characters penalty
- BOM characters penalty

## File Formats

- **Input**: Plain text files (.txt) with UTF-8 encoding preferred
- **Output**: Cleaned text files and analysis reports
- **Supported encodings**: UTF-8, UTF-8-sig, Latin-1, CP1252, ISO-8859-1

## Examples

### Cleaning a Raw Text
```bash
# Analyze the raw text first
python analyze_text.py nur_al_idah_raw.txt

# Clean with basic settings
python text_cleaner.py nur_al_idah_raw.txt -o nur_al_idah_cleaned.txt

# Verify the cleaning
python analyze_text.py nur_al_idah_cleaned.txt
```

### Batch Processing
```bash
# Process multiple files
for file in *.txt; do
    python text_cleaner.py "$file" -o "cleaned_$file"
done
```

## Tips for Best Results

1. **Start with analysis** - Always analyze your text first to understand its current state
2. **Use preview mode** - Check what will be changed before applying fixes
3. **Backup your files** - Keep original files safe
4. **Manual review** - For critical texts, use interactive mode
5. **Verify results** - Always analyze the cleaned text to ensure quality

## Troubleshooting

### Common Issues

**Encoding errors**: The tool automatically tries multiple encodings. If you get encoding errors, check your file encoding.

**Arabic text not displaying**: Ensure your terminal and text editor support UTF-8 encoding.

**Performance issues**: For very large files (>10MB), consider splitting them into smaller chunks.

### Getting Help

If you encounter issues:
1. Check the error messages carefully
2. Try the preview mode first
3. Use verbose output for more information
4. Ensure your Python environment has all required dependencies

## Contributing

This tool is designed specifically for Islamic texts and fiqh studies. Contributions that improve Arabic text handling, Islamic content recognition, or add new cleaning features are welcome.

## License

This project is open source and available under the MIT License.

## Acknowledgments

- Designed for Islamic text processing and fiqh studies
- Optimized for Arabic and transliterated content
- Built with respect for Islamic scholarly traditions