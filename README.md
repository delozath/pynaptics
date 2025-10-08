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
- [NLP for Spanish Sentences](#natural-language-processing-sentence-preprocessing-in-mexican-spanish)
- [Latex generated PDF to plain text](#latex-generated-pdf-to-plain-text)
---

## ISBN Metadata Retriever

A lightweight tool to enrich lists of ISBNs with metadata by querying the Google Books API. Input is read from a CSV file, and the results are exported in CSV format.

[🔗 repository link](./src/isbn_metadata/)

### 📚 What It Does

- Loads a list of ISBNs from `data/libros.csv`
- Cleans and normalizes each ISBN (e.g., removes hyphens)
- Queries Google Books API for metadata:
  - Title
  - Authors
  - Publisher
  - Published Date
- Outputs the results to `data/output.csv`

------

## BibLaTeX Checker

A lightweight tool to clean, normalize, and convert BibLaTeX files into JSON and back, extracting abstracts into a CSV.

[🔗 repository link](./src/biblatex_checker)

### 📚 What It Does

* **Loads** a `.bib` file from the `data/` folder
* **Normalizes** BibLaTeX entry keys (replaces special characters with ASCII equivalents)
* **Converts** the cleaned BibLaTeX content into CSL‑JSON using `pypandoc`
* **Deduplicates** authors and extracts abstracts into a DataFrame
* **Exports**

  * `data/output.bib` 
  * `data/abstracts.csv`


------
## Natural Language Processing: Sentence Preprocessing in Mexican Spanish
Provides tools to perform a preprocessing pipeline suitable for Natural Language Processing: tokenize, lemmanize, also to remove stopwords, accents and puctuation signs for Mexican Spanish senteces.

[🔗 repository link](./src/nlp_preprocessing)

### 📚 What It Does

* **Loads** `SpaCy` models: CPU and GPU based
* **Normalizes** Lower case, remove accents and stopwords, preserving negative words
* **Processing** Extract lemmas
* **Display** Show results in CLI


------
## Latex generated PDF to plain text
[🔗 repository link](./src/latexpdf_to_plaintext)
Pending documentation

------