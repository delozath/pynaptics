# pynaptics
A collection of lightweight Python scripts|snippets that can solve several atomic tasks such as, APIs connection and preprocessing data, etc. pynaptics contains utilities that support, but don’t belong to my core research projects in machine learning, embedded AI, and medical applications. Fast, OOP, modular, and just smart enough to keep things firing.


## 🧠 Purpose

`pynaptics` serves as a flexible workspace for utility scripts that enable and accelerate my development workflow.  

Use cases include:

- Data preprocessing pipelines
- API clients (e.g., PubMed, ISBN lookup)
<!-- 
- Batch file handling and automation
- Metadata extraction
- Rapid prototyping for peripheral systems -->

## 📦 Projects
- [ISBN Metadata Retriever](#isbn-metadata-retriever)
- [BibLaTeX Checker](#biblatex-checker)
---

# ISBN Metadata Retriever

A lightweight tool to enrich lists of ISBNs with metadata by querying the Google Books API. Input is read from a CSV file, and the results are exported in CSV format.

[🔗 Code link](./src/isbn_metadata_retriver.py)

## 📚 What It Does

- Loads a list of ISBNs from `data/libros.csv`
- Cleans and normalizes each ISBN (e.g., removes hyphens)
- Queries Google Books API for metadata:
  - Title
  - Authors
  - Publisher
  - Published Date
- Outputs the results to `data/output.csv`

## 🧠 Purpose

Automate the retrieval of bibliographic metadata using only ISBNs, with minimal dependencies and zero configuration.

## 🗂️ Project Structure
```
src/
│
├── data/
│ ├── libros.csv # Input: CSV file with ISBNs
│ └── output.csv # Output
│
├── isbn_metadata_retriver.py # Core logic and entry point
│   ├── class ISBNChecker
│   ├── class ISBNDataBaseDriver
│   └── def main()
```

## 🚀 Usage

1. **Prepare your input file**

   Ensure `data/libros.csv` exists and contains a column named `ISBN` with valid ISBN-10 or ISBN-13 values.

   Example:

   ```csv
   ISBN
   9780134685991
   0-201-61622-X
    ```

2. **Run script**

   ```bash
   python -m src.get_data_from_isbn
    ```

## 🛠️ Requirements
 - Python 3.9 or higher
 - pandas 2.1 or higher


## ⚠️ Notes

 - Uses Google Books API without authentication (no API key required).
 - Limited to ~1000 requests/day (subject to change by Google).
 - If an ISBN is not found, output will include:
 ```python
   {"ISBN": "<value>", "title": "Book not found"}
 ```

## 🔧 TODO
 - Add support for API keys and quota tracking
 - Cache previously fetched results locally (e.g., in SQLite or JSON)


------
------


# BibLaTeX Checker

A lightweight tool to clean, normalize, and convert BibLaTeX files into JSON and back, extracting abstracts into a CSV.

[🔗 Code link](./src/biblatex_checker.py)

## 📚 What It Does

* **Loads** a `.bib` file from the `data/` folder
* **Normalizes** BibLaTeX entry keys (replaces special characters with ASCII equivalents)
* **Converts** the cleaned BibLaTeX content into CSL‑JSON using `pypandoc`
* **Deduplicates** authors and extracts abstracts into a DataFrame
* **Exports**

  * `data/output.bib` 
  * `data/abstracts.csv`

## 🧠 Purpose

Automate the cleaning and enrichment of BibLaTeX bibliographies and rapidly extract structured metadata (abstracts and authors) with zero configuration.

## 🗂️ Project Structure

```
src/
│
├── data/
│   ├── ResearchRabbit_Export.bib   # Input
│   ├── output.bib                  # Output
│   └── abstracts.csv               # Output
│
└── biblatex_checker.py            # Core logic and entry point
    ├── class BiblatexChecker
    └── def main()
```

## 🚀 Usage

1. **Prepare your input file**
   Ensure `src/data/ResearchRabbit_Export.bib` exists and is UTF‑8 encoded.

2. **Run the script**

   ```bash
   python -m src.biblatex_checker
   ```

   or:

   ```bash
   python src/biblatex_checker.py
   ```

3. **Review the results**

   * `src/data/output.bib`
   * `src/data/abstracts.csv`

## 🛠️ Requirements

* Python 3.8 or higher
* pandas ≥ 2.0
* pypandoc
* Pandoc installed and accessible in system PATH

## ⚠️ Notes

* Depends on Pandoc: ensure `pandoc` is installed and available on your system.
```bash
#Debian-like Linux distributions
sudo apt install pandoc
```
* If conversion fails, validate your BibLaTeX entries.
* `load_bibfile` handles `FileNotFoundError` and `UnicodeDecodeError` with console messages.

## 🔧 TODO

* Add support for retrieving missing DOIs

