import re
import unicodedata
import spacy
from spacy.lang.es.stop_words import STOP_WORDS as SPACY_STOP_ES

from src.NLP_Preprocessing.NLP_sentence_preproc import LoadYaml

class SentencesNLPPreprocTransformer:
    BATCH_SIZE = 64
    N_PROC = 1

    def __init__(self) -> None:
        spacy.require_gpu()
        self.nlp_pipeline = spacy.load("es_dep_news_trf")
        self.nlp_pipeline.max_length = 2_000_000
        config = LoadYaml()

        self.STOP_ES_NOACC = {self._strip_accents(w.lower()) for w in SPACY_STOP_ES}
        self.NEG_KEEP_BASE = self._set_negative_words(config)

    def _strip_accents(self, s: str) -> str:
        return "".join(
            ch for ch in unicodedata.normalize("NFD", s)
            if unicodedata.category(ch) != "Mn"
        )

    def _set_negative_words(self, config):
        return config.negative

    def _is_numeric_token(self, tok) -> bool:
        pattern = re.compile(
                r"""^(
                    (\d+([.,]\d+)?([eE][+-]?\d+)?)      # 12 / 12.3 / 12,3 / 1e-3
                    (/%|%|‰|‱)?                         # sufijos de porcentaje
                    |
                    (\d+/\d+)                           # fracción simple como 120/80
                )$""",
                re.VERBOSE
             )

        txt = tok.text
        if tok.like_num or pattern.match(txt):
            return True
        else:
            return False
    
    def _normalize_token(self, token) -> str:
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
        out = []
        for doc in self.nlp_pipeline.pipe(texts, batch_size=self.BATCH_SIZE, n_process=self.N_PROC):
            toks = [self._normalize_token(t) for t in doc]
            toks = [w for w in toks if w]
            s = " ".join(toks)
            s = " ".join(s.split())
            out.append(s)
        return out


if __name__ == "__main__":
    textos = [
        "La mamá de la paciente embarazada refiere que se le debe dar jugos y agua a los bebés recién nacidos porque no quedan satisfechos",
        "Que hacer si no se sienten movimientos del bebé por más de 8 horas",
        "Puedo tomar bebidas alcoholicas mientras le estoy dando pecho a mi bebé, tiene 6 meses",
        "Mi bebé de 4 meses aún no puede sostener su cabeza, eso es normal",
        "A los cuantos meses ya le puedo dar de comer otra cosa a mi bebé que no sea leche o formula"
    ]

    model = SentencesNLPPreprocTransformer()
    for n, (org, proc) in enumerate(zip(textos, model.run(textos))):
        print(f"\n{n+1}:\n  {org}\n  {proc}")
    breakpoint()



