
import re
import pandas as pd
from pathlib import Path
import pypandoc, json


class BiblatexChecker:
    replace_symb = {
            '%': '\\%',
            '±': '$\\pm$',
            '&': '\\&',
            '’': "'",
            '<': '$<$',
            '>': '$>$',
            ' ': ' ',
            'κ': '$\\kappa$',
            ' ': ' ',
            '≥': '$\\geq$',
            '–': '--',
            '·': '.',
            '"': "''"
         }
    replace_bibkeys = {
            'ß': 'ss', #'\\s',
            'ã': 'a',  #'\\~{a}',
            'Ç': 'C',  #'\\cc',
            'ç': 'c',  #'\\cC',
            'á': 'a',
            'é': 'e',
            'í': 'i',
            'ó': 'o',
            'ú': 'u',
            'Á': 'A',
            'É': 'E',
            'Í': 'I',
            'Ó': 'O',
            'Ú': 'U',
            'ü': 'U',
            'Ü': 'U',
            '_': ''
         }
    replace_seq = (
        ('&amp', r'\&'),
        ( '“'  , '``' ),
        ( '”'  , "''" ),
        (r"\'\'", "''") #TODO: to optimize
     )
    def __init__(self):
        self.path = Path(__file__).parent.parent / 'data'
    #
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
    #
    def gral_replace(self, text):
        replacements = str.maketrans(BiblatexChecker.replace_symb)
        doc_rep = text.translate(replacements)
        doc_rep = doc_rep.replace('\\n', ' ')
        #
        for rep in BiblatexChecker.replace_seq:
            doc_rep = doc_rep.replace(*rep)
        #TODO
        return doc_rep
    #
    def clean_bibkeys(self, text):
        replacements = str.maketrans(BiblatexChecker.replace_bibkeys)
        text = re.sub(
            r'@(\w+)\{([\w-]+)',
            lambda m: f'@{m.group(1)}{{{m.group(2).translate(replacements)}',
            text
         )
        #
        return text
    #
    def __to_dict(self, text):
        raw_json = (
            pypandoc
                .convert_text(
                    text,
                    'csljson',
                    format='biblatex'
                 )
         )
        return json.loads(raw_json)
    #
    def run(self, fname):
        text = self.load_bibfile(fname)
        text = self.gral_replace(text)
        text = self.clean_bibkeys(text)
        text_decode = self.__to_dict(text)
        text_cure_authors = self.__check_duplicate_authors(text_decode)
    
        self.__save(text_cure_authors)
        breakpoint()
        return text
    #
    def __save(self, text):
        json_data = json.dumps(text, ensure_ascii=False, indent=2)
        #
        biblatex = pypandoc.convert_text(
            source=json_data,
            format='csljson',
            to='biblatex'
         )
        #
        Path("entries.bib").write_text(biblatex, encoding="utf-8") 

    #
    def __check_duplicate_authors(self, text):
        for a in text:
            authors = a.get('author', [{'family':'', 'given': ''}])
            authors = pd.DataFrame(authors)
            if len(authors)>1:
                authors = authors[~authors.duplicated(keep='first')]
            #
            a['author'] = authors[['family', 'given']].to_dict('records')
        #
        return text
    #
#
#
def main():
    bib = BiblatexChecker()
    text_clean = bib.run('ResearchRabbit_Export.bib')
    breakpoint()
#
#
if __name__=='__main__':
    main()