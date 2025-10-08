import urllib.request
import json
import pandas as pd
from pathlib import Path

class ISBNChecker:
    """
    Queries the Google Books API to retrieve metadata for one or more ISBNs.

    Parameters
    ----------
    isbn_list : int, str, or list of (int or str)
        A single ISBN (int or str), or a list of ISBNs to query.

    Attributes
    ----------
    isbns : list of str or int
        Normalized internal list of ISBNs for processing.

    Examples
    --------
    >>> checker = ISBNChecker(['9780134685991', '0-201-61622-X'])
    >>> df = checker.search()
    >>> print(df[['title', 'authors']])
    """
    #
    URL_BASE = "https://www.googleapis.com/books/v1/volumes?q=isbn:"
    def __init__(self, isbn_list):
        if isinstance(isbn_list, list):
            self.isbns = isbn_list
        elif isinstance(isbn_list, (int, str)):
            self.isbns = [isbn_list]
        else:
            raise TypeError("Object isbn_list must be int|str|list")
    #
    def __strip(self, isbn):
        if isinstance(isbn, int):
            return isbn
        else:
            return isbn.replace('-', '')
    #
    def get_info(self, isbn):
        """
        Queries the Google Books API for a single ISBN.

        Parameters
        ----------
        isbn : str or int
            A normalized ISBN without dashes.

        Returns
        -------
        dict
            fields:
            - 'title'
            - 'publisher'
            - 'publishedDate'
            - 'authors' (comma-separated string)
            - 'ISBN'

            If the ISBN is not found, returns:
            {'ISBN': <isbn>, 'title': 'Book not found'}

        Notes
        -----
        This method performs a blocking HTTP request via urllib. No rate limiting or
        retries are implemented.
        """
        #
        with urllib.request.urlopen(f"{ISBNChecker.URL_BASE}{isbn}") as f:
            text = f.read()
        #
        text = text.decode("utf-8")
        parser = json.loads(text)
        #
        book = {}
        if parser['totalItems']>0:
            item = parser['items'][0]['volumeInfo']
            book = {key:item.get(key, 'null') for key in ['title', 'publisher', 'publishedDate']}
            book['authors'] = ', '.join(item.get('authors', ["null"]))
            book['ISBN'] = item['industryIdentifiers'][0]['identifier']
        else:
            book = {'ISBN': isbn, 'title': 'Book not found'}
            print("ISBN not found")
        #
        return book
    #
    def search(self, save=True):
        """
        Queries all ISBNs passed to the constructor and returns results in a pandas.DataFrame.

        Returns
        -------
        pandas.DataFrame
            DataFrame containing book metadata for each ISBN.
            See `get_info()` for output fields.

        See Also
        --------
        ISBNDataBaseDriver.save : To persist the results as CSV.
        """
        book_list = []
        for isbn in self.isbns:
            isbn = self.__strip(isbn)
            book = self.get_info(isbn)
            book_list.append(book)
        #
        book_list = pd.DataFrame(book_list)
        return book_list
#
#
class ISBNDataBaseDriver:
    """
    Handles loading and saving of ISBN lists using CSV files from the data/ folder.

    Parameters
    ----------
    fname : str
        Filename (without path) of the input CSV file located in the 'data' directory.

    Attributes
    ----------
    path : pathlib.Path
        Path to the data folder.
    fname : str
        Filename of the CSV to load.

    Examples
    --------
    >>> db = ISBNDataBaseDriver('libros.csv')
    >>> isbn_list = db.get_isbn()
    >>> len(isbn_list)
    12
    """
    #
    def __init__(self, fname):
        self.path = Path.cwd() / 'data'
        self.fname = fname
    #
    @property
    def db(self):
        if not hasattr(self, '_db'):
            self._db = pd.read_csv(self.path / self.fname)
        return self._db
    #
    def get_isbn(self):
        """
        Extracts the ISBN column from the loaded CSV.

        Returns
        -------
        list of str
        """
        return self._db['ISBN'].to_list()
    #
    def save(self, df):
        df.to_csv(self.path / 'output.csv', index=False)
#
#
def main():
    """
    Main routine.

    1. Loads ISBNs from 'libros.csv' in the data directory.
    2. Queries metadata from Google Books.
    3. Saves results to 'output.csv'.

    Run
    ---
    >>> python -m src.isbn_metadata_retriver
    """
    isbn_db = ISBNDataBaseDriver('libros.csv')
    isbn_list = isbn_db.db['ISBN'].to_list()
    #
    isbn_search = ISBNChecker(isbn_list)
    books = isbn_search.search()
    isbn_db.save(books)
    print(3*'\n', "Data saved...")
#
#
if __name__=='__main__':
    main()