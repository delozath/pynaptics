# gpu_spacy_text_preprocessed_negnums.py
# Ejecuta así (sin validaciones):
#   uv run python gpu_spacy_text_preprocessed_negnums.py
#
# Requisitos (ya asumidos por tu entorno):
#   - spacy, spacy-transformers, torch (GPU OK)
#   - modelo: es_core_news_trf

import re
import unicodedata
import spacy
from spacy.lang.es.stop_words import STOP_WORDS as SPACY_STOP_ES

spacy.require_gpu()
nlp = spacy.load("es_dep_news_trf")
nlp.max_length = 2_000_000

BATCH_SIZE = 64
N_PROC = 1  # con GPU y transformer, 1 proceso

# -------------------------------------------------------------------
# Normalización
# -------------------------------------------------------------------
def strip_accents(s: str) -> str:
    return "".join(
        ch for ch in unicodedata.normalize("NFD", s)
        if unicodedata.category(ch) != "Mn"
    )

# Preparamos el set de stopwords y las negaciones a conservar.
STOP_ES_NOACC = {strip_accents(w.lower()) for w in SPACY_STOP_ES}

# “no y sus variantes” (ajusta si quieres ser más estricto o más laxo):
NEG_KEEP_BASE = {
    "no", "ni", "nunca", "jamas", "sin", "tampoco",
    "ningun", "ninguna", "ninguno", "ningunas", "ningunos", "nada", "nadie"
}
# Nota: usamos formas sin acento para comparar tras strip_accents.

# Detecta tokens numéricos (además de t.like_num) incluyendo formatos clínicos: 3, 3.5, 3,5, 1e-3, 12%, 120/80
NUM_PAT = re.compile(
    r"""^(
        (\d+([.,]\d+)?([eE][+-]?\d+)?)      # 12 / 12.3 / 12,3 / 1e-3
        (/%|%|‰|‱)?                         # sufijos de porcentaje
        |
        (\d+/\d+)                           # fracción simple como 120/80
    )$""",
    re.VERBOSE
)

def is_numeric_token(t) -> bool:
    txt = t.text
    if t.like_num:
        return True
    if NUM_PAT.match(txt):
        return True
    return False

def normalize_token(t) -> str:
    # 1) lema contextual en minúsculas
    x = t.lemma_.lower()

    # 2) convertir a marcador numérico si es cantidad
    if is_numeric_token(t):
        return "<num>"

    # 3) descartar puntuación/espacio
    if t.is_space or t.is_punct:
        return ""

    # 4) quitar acentos
    x_noacc = strip_accents(x)

    # 5) eliminar stopwords excepto negaciones
    if x_noacc in STOP_ES_NOACC and x_noacc not in NEG_KEEP_BASE:
        return ""

    return x_noacc

# -------------------------------------------------------------------
# API principal
# -------------------------------------------------------------------
def preprocess_texts_to_string(texts):
    """
    Devuelve lista de strings lematizados, sin stopwords, SIN acentos,
    conservando negaciones (no/ni/nunca/…),
    y con cantidades numéricas normalizadas a <num>.
    """
    out = []
    for doc in nlp.pipe(texts, batch_size=BATCH_SIZE, n_process=N_PROC):
        toks = [normalize_token(t) for t in doc]
        toks = [w for w in toks if w]           # quitar vacíos
        s = " ".join(toks)                      # mezcla final
        s = " ".join(s.split())                 # colapsar espacios múltiples
        out.append(s)
    return out

# -------------------------------------------------------------------
# Ejemplo mínimo (sin validaciones)
# -------------------------------------------------------------------
if __name__ == "__main__":
    textos = [
        "El inhibidor no mostró una reducción significativa del biomarcador en 24 horas (12%).",
        "La RM no reveló lesiones compatibles con esclerosis múltiple: 120/80 mmHg.",
        "El paciente nunca toma alcohol ni tabaco; saturación 96.5%."
    ]
    for s in preprocess_texts_to_string(textos):
        print(s)
