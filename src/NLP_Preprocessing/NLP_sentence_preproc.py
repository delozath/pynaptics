import os
import yaml
from yaml.loader import SafeLoader
from pathlib import Path

import spacy, spacy_transformers

# GPU
import torch
#torch.cuda.set_device(0)
spacy.prefer_gpu()

# Transformer HF en GPU (elige otro backbone si quieres)
#BACKBONE = "dccuchile/bert-base-spanish-wwm-uncased"
#nlp.add_pipe("transformer", first=True, config={"model": {"name": BACKBONE}})
#nlp.initialize()

class LoadYaml:
    def __init__(self, fname='extra.yml') -> None:
        path = Path('.') / 'src/NLP_Preprocessing' / fname
        with open(path.absolute(), 'r') as file:
            docs = [*yaml.load_all(file, Loader=SafeLoader)]
            for d in docs:
                setattr(self, *[*d.items()][0])


class SentenceNLPPreproc:
    def __init__(self) -> None:
        self.nlp_pipeline = spacy.load("es_core_news_lg")
        config = LoadYaml()
        self.STOPWORDS = self._set_extra_stopwords(config)
        self.EXTRA_LEMMAS = self._set_extra_lemmas(config)

    def _set_extra_stopwords(self, config):
        stopwords = set(self.nlp_pipeline.Defaults.stop_words) | {w.lower() for w in config.stopwords}
        stopwords.discard("no")
        return stopwords
    
    def _set_extra_lemmas(self, config):
        return {j: k for k, i in config.lemmas.items() for j in i}

    def _extra_lemmas(self, tok):
        lw = tok.text.lower()
        if lw in self.EXTRA_LEMMAS:
            return self.EXTRA_LEMMAS[lw]
        if tok.pos_ in ("VERB","AUX"):
            return tok.lemma_.lower() if tok.lemma_ else lw
        return tok.lemma_.lower() if tok.lemma_ else lw

    def run(self, text: str):
        doc = self.nlp_pipeline(text)
        out = []
        for tok in doc:
            if tok.is_alpha:
                lw = tok.text.lower()
                if not lw in self.STOPWORDS:
                    out.append(self._extra_lemmas(tok))
        return out

if __name__ == "__main__":
    text = "La mamá de la paciente embarazada refiere que se le debe dar jugos y agua a los bebés recién nacidos porque no quedan satisfechos"
    nlp = SentenceNLPPreproc()
    res = nlp.run(text)
    print(" ".join(res))
    breakpoint()
