import pandas as pd
from pathlib import Path

import re

def _get_extension(path_file):
    extension = r"\.([^.]+)$"
    ext = re.search(extension, path_file)
    return ext

def _load_sav(path_file):
    data = pd.read_spss(path_file)
    return data

def load_ext(path_file):
    ext = _get_extension(path_file)
    #
    drivers = {'sav': _load_sav}
    #
    if ext:
        ext = ext.group(1)
        data = drivers[ext](path_file)
        return data
    else:
        raise TypeError(f"File with no extension")

def _save_csv(df, pfname, ext):
    df.to_csv((f"{pfname}.{ext}"))

def save_ext(df, path_file, ext):
    drivers = {'csv': _save_csv}
    try:
        drivers[ext.lower()](df, path_file, ext)
        print('Data saved')
    except KeyError:
        "No driver for the given extensiton"
    

