
import re
import pandas as pd
from pathlib import Path
import pypandoc, json


class BiblatexChecker:
    """
    Clean and convert BibLaTeX files to JSON and back, extracting abstracts.

    Attributes
    ----------
    replace_bibkeys : dict
        Mapping of special characters to ASCII equivalents for bib keys.
    replace_seq : tuple of tuple
        Substitutions to apply after reconverting to BibLaTeX.
    path : pathlib.Path
        Directory where input and output files are stored.
    """
    #
    replace_bibkeys = {
        'ß': 'ss', 'ã': 'a', 'Ç': 'C', 'ç': 'c',
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
        'ü': 'U', 'Ü': 'U', 'ć': 'c', '_': ''
     }
    #
    replace_seq = (
        (r'\&amp', r'\&'),
        (r'~', ''),
        (r'‐', '-'),
     )
    def __init__(self):
        self.path = Path.cwd() / 'data'
    
    def load_bibfile(self, fname):
        fname = self.path / fname
        try:
            with open(fname, 'r', encoding='utf-8') as f:
                text = f.read()
                return text
        except FileNotFoundError:
            print(f"Error: The file '{fname.as_posix()}' was not found.")
        except UnicodeDecodeError:
            print("Error: Could not decode the file with UTF-8 encoding.")
    
    def clean_bibkeys(self, text):
        """
        Sanitize BibLaTeX entry keys by replacing special characters.

        Parameters
        ----------
        text : str
            Raw BibLaTeX content.

        Returns
        -------
        str
            Content with normalized entry keys.
        """
        replacements = str.maketrans(BiblatexChecker.replace_bibkeys)
        text = re.sub(
            r'@(\w+)\{([\w-]+)',
            lambda m: f'@{m.group(1)}{{{m.group(2).translate(replacements)}',
            text
         )
        #
        return text
    
    def _text_to_json(self, text):
        raw_json = (
            pypandoc
                .convert_text(
                    text,
                    'csljson',
                    format='biblatex'
                 )
         )
        return json.loads(raw_json)
    
    def _scan_authors_and_abstracts(self, entries):
        """
        Normalize author lists and extract abstracts into a DataFrame.

        Parameters
        ----------
        entries : list of dict
            CSL JSON entries.

        Returns
        -------
        tuple
            - entries (list of dict): Entries with de-duplicated authors.
            - abstracts (pandas.DataFrame): Columns ['doi', 'abstract', 'bibkey', 'firsr author'].
        """
        abstracts = []
        for a in entries:
            authors = a.get('author', [{'family':'', 'given': ''}])
            if len(authors)>1:
                tmp = {(i['family'], i['given']): '' for i in a['author']}
                authors = [{'family': i[0], 'given': i[1]} for i in tmp.keys()]
            #
            a['author'] = authors
            #
            abstracts.append(
                {'doi': a.get('DOI', 'null'),
                 'abstract': a.get('abstract', 'null'),
                 'bibkey': a.get('id'),
                 'fst author': ', '.join(a.get('author')[0].values())
                 }
            )
        abstracts = pd.DataFrame(abstracts)
        
        return entries, abstracts
    
    def _save(self, entries, abstracts):
        """
        Write cleaned entries back to BibLaTeX and save abstracts CSV.

        Parameters
        ----------
        entries : list of dict
            CSL JSON entries to convert back.
        abstracts : pandas.DataFrame
            DataFrame of extracted abstracts.
        """
        json_data = json.dumps(entries, ensure_ascii=False, indent=2)
        
        biblatex = pypandoc.convert_text(
            source=json_data,
            format='csljson',
            to='biblatex'
         )
        for rep in BiblatexChecker.replace_seq:
            biblatex = biblatex.replace(*rep)
        
        (self.path/"output.bib").write_text(biblatex, encoding="utf-8")
        
        abstracts.to_csv(self.path/"abstracts.csv", index=False)
    
    def clean_entries(self, fname):
        text = self.load_bibfile(fname)
        text = self.clean_bibkeys(text)
        json_entries = self._text_to_json(text)
        json_entries, abstracts = self._scan_authors_and_abstracts(json_entries)
        #
        self._save(json_entries, abstracts)
#
#
def main():
    bib = BiblatexChecker()
    bib.clean_entries('ResearchRabbit_Export.bib')
    print("\nBiblatex cured and exported...")
#
#
if __name__=='__main__':
    main()