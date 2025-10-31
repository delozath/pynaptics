import spacy
from utils import LoadYaml

class SentencePreproc:
    """
    Sentence-level Spanish preprocessing pipeline.

    This wrapper around spaCy performs:
    1) tokenization and POS tagging,
    2) domain-aware stopword filtering (preserving negation "no"),
    3) lemmatization with custom overrides for domain terms and verbs/auxiliaries.

    Parameters
    ----------
    None

    Attributes
    ----------
    nlp_pipeline : spacy.language.Language
        Loaded spaCy Spanish pipeline (``es_core_news_lg``).
    STOPWORDS : set[str]
        Combined stopword set: spaCy defaults Union YAML stopwords, minus ``"no"``.
    EXTRA_LEMMAS : dict[str, str]
        Lowercased surface-form --> canonical-lemma overrides from YAML.

    Examples
    --------
    >>> nlp = SentencePreproc()
    >>> nlp.run("Los bebés no deben tomar agua al nacer.")
    ['bebé', 'no', 'deber', 'tomar', 'agua', 'nacer']
    """
    def __init__(self) -> None:
        config = LoadYaml()
        self.nlp_pipeline = spacy.load("es_core_news_lg")
        self.STOPWORDS = self._set_extra_stopwords(config)
        self.EXTRA_LEMMAS = self._set_extra_lemmas(config)

    def _set_extra_stopwords(self, config):
        """
        Build the stopword set with domain-specific additions while preserving negation.

        Parameters
        ----------
        config : LoadYaml
            Configuration object providing ``stopwords``.

        Returns
        -------
        set[str]
            Merged stopword set where the token ``"no"`` is explicitly retained.

        Notes
        -----
        Retaining ``"no"`` helps preserve the semantic polarity of sentences in
        downstream tasks (e.g., assertion/negation detection).
        """
        stopwords = set(self.nlp_pipeline.Defaults.stop_words) | {w.lower() for w in config.stopwords}
        stopwords.discard("no")
        return stopwords
    
    def _set_extra_lemmas(self, config):
        """
        Construct a surface-to-lemma override dictionary from YAML.

        Parameters
        ----------
        config : LoadYaml
            Configuration object providing ``lemmas`` as a mapping
            ``{lemma: [forms...]}``.

        Returns
        -------
        dict[str, str]
            Lowercased surface form --> canonical lemma mapping.
        """
        return {j: k for k, i in config.lemmas.items() for j in i}

    def _extra_lemmas(self, tok):
        """
        Apply custom lemma overrides and sensible defaults.

        Parameters
        ----------
        tok : spacy.tokens.Token
            Token to normalize.

        Returns
        -------
        str
            Normalized lemma (lowercased). Prefers:
            1) explicit override in ``EXTRA_LEMMAS``,
            2) spaCy lemma for verbs/auxiliaries,
            3) spaCy lemma for other POS,
            4) lowercased surface form if lemma is unavailable.

        Notes
        -----
        Handling verbs and auxiliaries explicitly reduces inflectional variance
        that otherwise leaks into features.
        """
        lw = tok.text.lower()
        if lw in self.EXTRA_LEMMAS:
            return self.EXTRA_LEMMAS[lw]
        if tok.pos_ in ("VERB","AUX"):
            return tok.lemma_.lower() if tok.lemma_ else lw
        return tok.lemma_.lower() if tok.lemma_ else lw

    def run(self, text: str):
        """
        Tokenize, filter, and lemmatize a Spanish sentence.

        Parameters
        ----------
        text : str
            Raw input text.

        Returns
        -------
        list[str]
            Sequence of normalized tokens after:
            - alphabetic filtering (``tok.is_alpha``),
            - stopword removal with preserved negation,
            - lemma normalization with domain overrides.

        Notes
        -----
        Punctuation, numbers, and non-alphabetic tokens are skipped. To retain
        numerals or symbols for specific tasks, adjust the ``is_alpha`` filter.
        """
        doc = self.nlp_pipeline(text)
        out = []
        for tok in doc:
            if tok.is_alpha:
                lw = tok.text.lower()
                if not lw in self.STOPWORDS:
                    out.append(self._extra_lemmas(tok))
        return out

if __name__ == "__main__":
    """
    Minimal example demonstrating the preprocessing pipeline.

    The sample contains clinical/colloquial content where domain-specific
    normalization and the preservation of negation are relevant.
    """
    text = "La mamá de la paciente embarazada refiere que se le debe dar jugos y agua a los bebés recién nacidos porque no quedan satisfechos"
    nlp = SentencePreproc()
    res = nlp.run(text)
    print(" ".join(res))
    breakpoint()
