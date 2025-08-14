import re
import os

import pandas as pd

import tkinter as tk
from tkinter import filedialog

class FileDriver:
    def __init__(self):
        self.driver_load = {'sav': self._load_sav}
        self.driver_save = {'csv': self._save_csv}
    #
    def _get_extension(self, pfname, default=None):
        _, ext = os.path.splitext(pfname)
        #
        ext = ext[1:].lower() if len(ext)>1 else default
        return ext
    #
    def _load_sav(self, pfname):
        data = pd.read_spss(pfname)
        return data
    #
    def load(self, pfname):
        if ext:=self._get_extension(pfname):
            data = self.driver_load[ext](pfname)
            return data
        else:
            raise TypeError(f"File with no extension")
    #
    def _save_csv(self, df, pfname):
        df.to_csv(pfname)
    #
    def save(self, df, pfname):
        ext = self._get_extension(pfname, default='.csv')
        try:
            func = self.driver_save.get(ext)
            func(df, pfname)
            print('Data saved')
        except KeyError:
            "No driver for the given extensiton"
#
#
class Dialogs:
    def __init__(self):
        self.exts = ['csv']
    #
    def load(self):
        window = tk.Tk()
        window.withdraw()
        #
        pfname = filedialog.askopenfilename(
            title="Select a file",
            filetypes=[
                #("All files", "*.*"),
                ("SPSS files", "*.sav"),
                ("Excel files", "*.xsl"),
                ("Excel 2005 files", "*.xlsx")
            ]
        )
        #
        return pfname
    #
    def save(self):
        pfname = filedialog.asksaveasfilename(
        title="Save file as",
        defaultextension=".csv",
        filetypes=[
            ("CSV file", "*.csv"),
            ]
        )
        #
        pfname, ext = self._test_extension(pfname)
        return f"{pfname}.{ext}"
    #
    def _test_extension(self, pfname):
        pfname, ext = os.path.splitext(pfname)
        ext = ext[1:] if ext in self.exts else 'csv'
        #
        return pfname, ext
