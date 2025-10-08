"""
Transformer-based Spanish sentence preprocessing with spaCy.

This module normalizes Spanish texts using a transformer pipeline
(``es_dep_news_trf``). It handles GPU activation, long text limits,
accent stripping, numeric detection, and stopword filtering while
preserving user-defined negation words from a YAML config.
"""

import re
import unicodedata
import spacy
from spacy.lang.es.stop_words import STOP_WORDS as SPACY_STOP_ES

from src.NLP_Preprocessing.sentence_preproc import LoadYaml


class SentencePreprocTransformer:
    """
    Transformer-backed sentence preprocessor for Spanish.

    This class wraps a spaCy transformer model to:
    1) tokenize and lemmatize,
    2) normalize to lowercase and strip accents,
    3) preserve numerics and percentages as-is,
    4) remove Spanish stopwords (accent-insensitive),
    5) retain negation tokens configured via YAML.

    Attributes
    ----------
    BATCH_SIZE : int
        Batch size passed to ``nlp.pipe``.
    N_PROC : int
        Number of processes for ``nlp.pipe``. Kept at 1 due to GPU use.
    nlp_pipeline : spacy.language.Language
        Loaded Spanish transformer pipeline (``es_dep_news_trf``).
    STOP_ES_NOACC : set[str]
        Spanish stopwords from spaCy with accents stripped and lowercased.
    NEG_KEEP_BASE : set[str]
        Negation terms to keep (read from YAML; compared against stripped forms).

    Notes
    -----
    - Requires GPU support; ``spacy.require_gpu()`` is called in ``__init__``.
    - ``nlp_pipeline.max_length`` is increased to allow very long inputs.
    """
    BATCH_SIZE = 64
    N_PROC = 1

    def __init__(self) -> None:
        """
        Initialize the transformer pipeline and preprocessing resources.

        Loads the Spanish dependency/transformer model, increases the maximum
        document length, and prepares:
        - accent-stripped stopword set,
        - domain-specific negation words loaded from YAML.

        Raises
        ------
        ValueError
            If the required spaCy model is not installed.
        RuntimeError
            If a GPU is not available when ``spacy.require_gpu()`` is enforced.
        """
        spacy.require_gpu()
        self.nlp_pipeline = spacy.load("es_dep_news_trf")
        self.nlp_pipeline.max_length = 2_000_000
        config = LoadYaml()

        self.STOP_ES_NOACC = {self._strip_accents(w.lower()) for w in SPACY_STOP_ES}
        self.NEG_KEEP_BASE = self._set_negative_words(config)

    def _strip_accents(self, s: str) -> str:
        """
        Remove diacritical marks using Unicode NFD normalization.

        Parameters
        ----------
        s : str
            Input string to normalize.

        Returns
        -------
        str
            String with combining marks removed (accent-insensitive form).

        Notes
        -----
        This is applied both to lemmas and stopwords to align comparisons.
        """
        return "".join(
            ch for ch in unicodedata.normalize("NFD", s)
            if unicodedata.category(ch) != "Mn"
        )

    def _set_negative_words(self, config):
        """
        Load negation words to preserve from configuration.

        Parameters
        ----------
        config : LoadYaml
            Configuration object expected to provide a ``negative`` iterable.

        Returns
        -------
        iterable
            Negation tokens that should not be removed during stopword filtering.

        Notes
        -----
        ``NEG_KEEP_BASE`` is later compared against accent-stripped lemmas.
        """
        return config.negative

    def _is_numeric_token(self, tok) -> bool:
        """
        Determine if a token is numeric or a numeric-like expression.

        Parameters
        ----------
        tok : spacy.tokens.Token
            Token to evaluate.

        Returns
        -------
        bool
            True if token is numeric, percentage (e.g., ``12%``, ``12/%``),
            decimal, scientific notation (e.g., ``12``, ``12.3``, ``1e-3``, ``12,3``, ), or fraction
            (e.g., ``120/80``); False otherwise.

        Notes
        -----
        Combines ``tok.like_num`` with a verbose regex to capture common
        clinical numeric formats.
        """
        pattern = re.compile(
                r"""^(
                    (\d+([.,]\d+)?([eE][+-]?\d+)?)
                    (/%|%)?
                    |
                    (\d+/\d+)
                )$""",
                re.VERBOSE
             )

        txt = tok.text
        if tok.like_num or pattern.match(txt):
            return True
        else:
            return False
    
    def _normalize_token(self, token) -> str:
        """
        Normalize a single token with lemmatization and filtering.

        Parameters
        ----------
        token : spacy.tokens.Token
            Token to normalize.

        Returns
        -------
        str
            Normalized token or empty string if filtered out.

        Processing Steps
        ----------------
        1) If numeric-like, return original text (preserve measurement fidelity).
        2) If whitespace or punctuation, drop it.
        3) Lemmatize --> lowercase --> strip accents.
        4) If lemma is a (accentless) stopword and not in negation keep-list,
           drop it.
        5) Otherwise return the normalized lemma.

        Notes
        -----
        Negation handling ensures polarity is not lost during normalization.
        """
        if self._is_numeric_token(token):
            return token.text

        if token.is_space or token.is_punct:
            return ""

        lem = token.lemma_.lower()
        lem = self._strip_accents(lem)

        if lem in self.STOP_ES_NOACC and lem not in self.NEG_KEEP_BASE:
            return ""

        return lem
    
    def run(self, texts):
        """
        Normalize a batch of texts with the transformer pipeline.

        Parameters
        ----------
        texts : iterable of str
            Sequence of raw input strings.

        Returns
        -------
        list[str]
            Each element is a whitespace-normalized string composed of
            processed tokens for the corresponding input text.

        Notes
        -----
        - Uses ``nlp.pipe`` with GPU for throughput.
        - Collapses multiple spaces after filtering to maintain clean output.
        - ``BATCH_SIZE`` and ``N_PROC`` control throughput; with GPU, keep
          ``N_PROC=1`` to avoid overhead.
        """
        out = []
        for doc in self.nlp_pipeline.pipe(texts, batch_size=self.BATCH_SIZE, n_process=self.N_PROC):
            toks = [self._normalize_token(t) for t in doc]
            toks = [w for w in toks if w]
            s = " ".join(toks)
            s = " ".join(s.split())
            out.append(s)
        return out


if __name__ == "__main__":
    """
    Minimal usage example.

    Processes a small list of Spanish clinical/parental queries and prints
    original vs. normalized outputs for quick inspection.
    """
    textos = [
        "La mamá de la paciente embarazada refiere que se le debe dar jugos y agua a los bebés recién nacidos porque no quedan satisfechos",
        "Que hacer si no se sienten movimientos del bebé por más de 8 horas",
        "Puedo tomar bebidas alcoholicas mientras le estoy dando pecho a mi bebé, tiene 6 meses",
        "Mi bebé de 4 meses aún no puede sostener su cabeza, eso es normal",
        "A los cuantos meses ya le puedo dar de comer otra cosa a mi bebé que no sea leche o formula"
    ]

    model = SentencePreprocTransformer()
    for n, (org, proc) in enumerate(zip(textos, model.run(textos))):
        print(f"\n{n+1}:\n  {org}\n  {proc}")
    breakpoint()



