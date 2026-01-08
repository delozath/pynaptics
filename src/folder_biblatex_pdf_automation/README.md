# Bibtex/Biblatex Retriving Entry Automation from Internet and PDF File Management

This repository contains scripts to automate the retrieval of BibTeX/BibLaTeX entries from online sources and to rename PDF files based on their bibliographic information, thes files are move to a specified directory.

The main functionalities include:
1. Fetching BibTeX/BibLaTeX entries using DOI
2. Renaming PDF files according to a SurnameYear format using the retrieved bibliographic data
3. Organizing files into specified directories
4. Update bibliographic bib-database with new entries


## 1. Setup
### 1.1 Requirements
- Python 3.10+
- Required Python packages: `pyperclip`, `bibtexparser`, `requests`, `python-dotenv`
You can install the required packages using pip:

```bash
pip install pyperclip bibtexparser requests python-dotenv
```

### 1.2 Path Configuration
This scripts use environment variables to manage paths and the bib-file database.

Create a `.env` file in the same folder as the scripts with the following structure:
> PATH_ORIGIN=/folder/downloads/pdfs
> PATH_DESTINATION=/folder/organized/pdfs
> BIBTEX_PATH=/folder/organized/pdfs/database.bib

## 2. Usage
Download PDF from internet sources (e.g., journal websites) and copy the DOI to your clipboard. Change to the folder where the scripts are located and run the script as is shown below:

```bash
python python ./folder_latex.py
```

## 3. Notes
- Ensure that the DOI is correctly copied to the clipboard before running the script.
- The script will handle errors such as missing DOI entries or file renaming conflicts.
- Make sure the paths in the `.env` file are correctly set to avoid file handling errors
- The script assumes that the latest added PDF file in the origin directory corresponds to the PDF being processed.