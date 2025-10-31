"""
Text preprocessing utilities for Spanish clinical sentences using spaCy.

This module provides:
- `LoadYaml`: loads project-specific configuration (stopwords and lemmatization
  mappings) from a YAML file.
- `SentencePreproc`: tokenization, stopword filtering (with domain-specific
  overrides), and lemmatization with optional custom lemma mappings.

Notes
-----
- Requires the spaCy model ``es_core_news_lg`` to be installed.
- YAML file is expected under ``./src/NLP_Preprocessing/<fname>``.
"""

import yaml
from yaml.loader import SafeLoader
from pathlib import Path

import spacy


class LoadYaml:
    """
    Load YAML configuration into attributes.

    Parameters
    ----------
    fname : str, optional
        File name of the YAML configuration located in
        ``./src/NLP_Preprocessing/``. By default ``'extra.yml'``.

    Attributes
    ----------
    stopwords : list[str]
        Additional stopwords to merge with spaCy defaults (expected key in YAML).
    lemmas : dict[str, list[str]]
        Mapping from canonical lemma to a list of surface forms to normalize
        (expected key in YAML).

    Notes
    -----
    The loader reads all documents from the YAML stream and sets the first
    key-value pair of each document as an attribute on the instance. This
    enables a flexible, document-per-setting YAML layout.
    """
    def __init__(self, fname='extra.yml') -> None:
        path = Path('.') / 'src/NLP_Preprocessing' / fname
        with open(path.absolute(), 'r', encoding="utf-8") as file:
            docs = [*yaml.load_all(file, Loader=SafeLoader)]
            for d in docs:
                setattr(self, *[*d.items()][0])
