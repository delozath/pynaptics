# BibLaTeX Checker

A lightweight tool to clean, normalize, and convert BibLaTeX files into JSON and back, extracting abstracts into a CSV.

[🔗 repository link](./src/biblatex_checker)

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
├── data/
│   ├── ResearchRabbit_Export.bib   # Input
│   ├── output.bib                  # Output
│   └── abstracts.csv               # Output
src/
│
├── biblatex_checker
│   ├── biblatex_checker.py
│   │   ├── class BiblatexChecker
│   │   └── def main()
```

## 🚀 Usage

1. **Prepare your input file**
   Ensure `data/ResearchRabbit_Export.bib` exists and is UTF‑8 encoded.

2. **Run the script**

   ```bash
   uv run -m src.biblatex_checker.biblatex_checker
   ```

   or:

   ```bash
   uv run python src/biblatex_checker/biblatex_checker.py
   ```

3. **Review the results**

   * `data/output.bib`
   * `data/abstracts.csv`

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
