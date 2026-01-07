import re
import unicodedata
import pyperclip
from urllib.parse import quote

import bibtexparser
from bibtexparser.bibdatabase import BibDatabase


import requests

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
                .encode('mac_roman', 'ignore')
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
        
    def fetch(self, text: str):
        """
        Fetch doi from internet, clean encoding, remove mojibake, replace special Latex characters and return cleaned BibTeX entry.
        
        Parameters
        ----------
        text : str
            DOI or URL containing DOI.
        
        Returns
        -------
        str
            Cleaned BibTeX entry as a string.
        """
        doi = self.doi_strip(text)
        bib = self.fetch_bibtex(doi)
        bib = self.clean_encoding(bib)
        
        bib_decode = bibtexparser.loads(bib).entries[0]
        bib_clean = self.clean_bibkey(bib_decode)
        bib_clean = self.clean_fields(bib_clean)
        bib_entry = self.dict_to_bib_entry(bib_clean)
        
        return bib_entry

    def doi_strip(self, doi: str) -> str:
        doi = doi.strip()
        if doi.startswith("http://") or doi.startswith("https://"):
            return doi.split("doi.org/")[-1]
        else:
            return doi



if __name__ == "__main__":
    text = pyperclip.paste()
    doi2bib = DOI2BibManager()
    bib_entry = doi2bib.fetch(text)
    print(bib_entry)
    
    breakpoint()