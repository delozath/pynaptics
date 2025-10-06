import os, spacy, spacy_transformers

# GPU
import torch
#torch.cuda.set_device(0)
spacy.prefer_gpu()

# Modelo base (lemmatización/pos)
nlp = spacy.load("es_core_news_lg")

# Transformer HF en GPU (elige otro backbone si quieres)
#BACKBONE = "dccuchile/bert-base-spanish-wwm-uncased"
#nlp.add_pipe("transformer", first=True, config={"model": {"name": BACKBONE}})
#nlp.initialize()

# Stopwords ES + extras MX
mx_extra_stops = {
    "órale","orale","ándale","andale","chale","nel","neta",
    "nomás","nomas","pos","pa","ora","sale","vale",
    "osea","o","sea","este","eh","mmm"
}
stopwords = set(nlp.Defaults.stop_words) | {w.lower() for w in mx_extra_stops}
stopwords.discard("no")

# Overrides lemas MX
LEMMA_OVERRIDES_ES_MX = {
    "checo":"checar","checas":"checar","checa":"checar","checamos":"checar","checan":"checar","checando":"checar",
    "checado":"checar","chequé":"checar","checaste":"checar","checaron":"checar","checó":"checar","checar":"checar",
    "chambeo":"chambear","chambeas":"chambear","chambea":"chambear","chambeamos":"chambear","chambeando":"chambear",
    "chateo":"chatear","chateas":"chatear","chatea":"chatear","chateando":"chatear",
    "whatsappeo":"whatsappear","whatsappeas":"whatsappear","whatsappea":"whatsappear","whatsappeando":"whatsappear",
    "texteo":"textear","texteas":"textear","textea":"textear","texteando":"textear",
    "parqueo":"parquear","parqueas":"parquear","parquea":"parquear","parqueando":"parquear",
}

def lemma_with_overrides(tok):
    l = tok.text.lower()
    if l in LEMMA_OVERRIDES_ES_MX:
        return LEMMA_OVERRIDES_ES_MX[l]
    if tok.pos_ in ("VERB","AUX"):
        return tok.lemma_.lower() if tok.lemma_ else l
    return tok.lemma_.lower() if tok.lemma_ else l

def preprocess(text: str):
    doc = nlp(text)
    out = []
    for tok in doc:
        if not tok.is_alpha:
            continue
        lw = tok.text.lower()
        if lw != "no" and lw in stopwords:
            continue
        out.append(lemma_with_overrides(tok))
    return out

if __name__ == "__main__":
    txt = "Por qué mi madre dice que tengo que darle juguito a mi bebé desde recien nacido"
    res = preprocess(txt)
    print(" ".join(res))
    breakpoint()
