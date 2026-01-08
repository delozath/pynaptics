import os
import shutil
import unicodedata
import pyperclip
from urllib.parse import quote

from typing import Literal

import bibtexparser
from bibtexparser.bibdatabase import BibDatabase

import requests

import dotenv


from pathlib import Path

from sympy import Li

class DOI2BibManager:
    latex_chars = (
        (r'\&amp', r'\&'),
        (r'~', ''),
        (r'‐', '-'),
        (r'–', '-'),
        (r'_', r'\_')
     )
    
    def clean_encoding(self, text: str) -> str:
        """
        Normalize text encoding to NFC and remove non-UTF-8 characters.

        Parameters
        ----------
        text : str
            Input text to be cleaned.
        
        Returns
        -------
        str
            Cleaned text with normalized encoding.
        """
        text = (
            unicodedata
                .normalize('NFC', text)
                .encode('utf-8', 'ignore')
                .decode('utf-8')
         )
        return text

    def clean_bibkey(self, bib_entry: dict) -> dict:
        """
        Sanitize BibLaTeX entry key by removing underscores and normalizing encoding.

        Parameters
        ----------
        bib_entry : dict
            BibLaTeX entry as a dictionary.

        Returns
        -------
        dict
            BibLaTeX entry with cleaned key in ASCII format.   
        """
        bib_entry['ID'] = (
                unicodedata.normalize(
                    'NFKD',
                    bib_entry['ID'].replace('_', '')
             ).encode('ascii', 'ignore').decode('ascii'))

        return bib_entry
    
    def clean_fields(self, bib_entry: dict) -> dict:
        """
        Clean BibLaTeX entry fields by normalizing encoding and replacing LaTeX special characters.

        Parameters
        ----------
        bib_entry : dict
            BibLaTeX entry as a dictionary.

        Returns
        -------
        dict
            BibLaTeX entry with cleaned fields. 
        """
        for k in [k for k in bib_entry.keys() if k not in ['ID', 'year']]:
            tmp = unicodedata.normalize('NFC', bib_entry[k])
            for old, new in self.latex_chars:
                tmp = tmp.replace(old, new)    
            bib_entry[k] = tmp
        
        return bib_entry
    
    def fetch_bibtex(self,doi: str, timeout_s: float = 10.0):
        """
        Fetch BibTeX entry from DOI using doi.org service.
        
        Parameters
        ----------
        doi : str
            Digital Object Identifier.
        timeout_s : float, optional
            Request timeout in seconds. Default is 10.0 seconds.
        
        Returns
        -------
        str
            BibTeX entry as a string.
        """
        url = f"https://doi.org/{doi}"
        headers = {
            "Accept": "application/x-bibtex",
            "User-Agent": "doi2bibtex/1.0 (mailto:you@example.com)",
        }
        r = requests.get(url, headers=headers, allow_redirects=True, timeout=timeout_s)
        r.raise_for_status()
        return r.text.strip()

    def dict_to_bib_entry(self, bib_entry) -> str:
        """
        Convert a BibTeX entry dictionary to a BibTeX formatted string.
        Parameters
        ----------
        bib_entry : dict
            BibTeX entry as a dictionary.
        
        Returns
        -------
        str
            BibTeX entry as a formatted string.
        """
        db = BibDatabase()
        db.entries = [bib_entry]
        db.comments = []
        db.preambles = []
        db.strings = {}
        return bibtexparser.dumps(db)
        
    def fetch(self, text: str, format: Literal['bib', 'dict']) -> tuple[str, str | dict]:
        """
        Fetch doi from internet, clean encoding, remove mojibake, replace special Latex characters and return cleaned BibTeX entry.
        
        Parameters
        ----------
        text : str
            DOI or URL containing DOI.
        format : Literal['bib', 'dict']
            Desired output format: 'bib' for BibTeX string, 'dict' for dictionary
        
        Returns
        -------
        tuple[str, str | dict]
            Tuple containing BibTeX key and the BibTeX entry in the specified format.
        """
        doi = self.doi_strip(text)
        bib = self.fetch_bibtex(doi)
        bib = self.clean_encoding(bib)
        
        bib_decode = bibtexparser.loads(bib).entries[0]
        bib_clean = self.clean_bibkey(bib_decode)
        bib_clean = self.clean_fields(bib_clean)
        
        bibkey = bib_clean['ID']
        match format:
            case 'dict':
                return bibkey, bib_clean
            case 'bib':
                bib_entry = self.dict_to_bib_entry(bib_clean)
                return bibkey, bib_entry
            case _:
                raise ValueError(f"Unsupported format: {format}")

    def doi_strip(self, doi: str) -> str:
        """
        Extract DOI from a given string, removing URL prefixes if present.
        Parameters
        ----------
        doi : str
            Input string containing DOI or DOI URL.
        
        Returns
        -------
        str
            Extracted DOI."""
        doi = doi.strip()
        if doi.startswith("http://") or doi.startswith("https://"):
            return doi.split("doi.org/")[-1]
        else:
            return doi


class PDFFileManager:
    def __init__(self):
        """
        Initialize PDFFileManager by loading environment variables for origin and destination paths.

        Raises
        -------
        NotADirectoryError
            If either the origin or destination path is not a valid directory.
        """
        dotenv.load_dotenv()
        self.pth_org = Path(os.getenv("PATH_ORIGIN"))
        self.pth_dest = Path(os.getenv("PATH_DESTINATION"))

        if not self.pth_org.is_dir():
            raise NotADirectoryError(f"{self.pth_org} is not a directory.")
        if not self.pth_dest.is_dir():
            raise NotADirectoryError(f"{self.pth_dest} is not a directory.")
    
    def newest_file(self):
        """
        Find the most recently modified PDF file in the origin directory.

        Returns
        -------
        Path
            Path to the most recently modified PDF file.
        
        Raises
        -------
        FileNotFoundError
            If no PDF files are found in the origin directory.
        """
        pdfs = [p for p in self.pth_org.iterdir() if p.is_file() and p.suffix.lower() == ".pdf"]
        if len(pdfs) == 0:
            raise FileNotFoundError(f"No PDF files found in: {self.pth_org}")
        return max(pdfs, key=lambda p: p.stat().st_mtime)
    
    def move_file(self, fname: Path):
        """
        Move the most recently modified PDF file from the origin directory to the destination directory with a new name.

        Parameters
        ----------
        fname : Path
            New filename (without extension) for the moved PDF file.
        
        Raises
        -------
        FileExistsError
            If a file with the new name already exists in the destination directory.
        """
        old_pfname = self.newest_file()
        new_pfname = self.pth_dest / f"{fname}.pdf"

        if new_pfname.exists():
            raise FileExistsError(f"File already exists: {new_pfname}")
        
        shutil.move(
            old_pfname.as_posix(),
            new_pfname.as_posix()
         )
        
        print(f"Moved file from {old_pfname} to {new_pfname}")


def orchestrator():
    """
    Orchestrate the process of fetching BibTeX entry from DOI in clipboard, copying it back to clipboard,
    and moving the most recent PDF file to the destination directory with the BibTeX key as filename.
    """
    text = pyperclip.paste()
    doi2bib = DOI2BibManager()
    bibkey, bib_entry = doi2bib.fetch(text, format='dict')
    bib_entry['file'] = f":{bibkey}.pdf:PDF"
    bib_entry = doi2bib.dict_to_bib_entry(bib_entry)
    pyperclip.copy(bib_entry)
    print(bib_entry)
    print("\nBibTeX entry copied to clipboard.")
    
    pdf_manager = PDFFileManager()
    pdf_manager.move_file(bibkey)
    

if __name__ == "__main__":
    #https://doi.org/10.1136/bmj-2023-078378
    orchestrator()