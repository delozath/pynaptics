# Natural Language Processing: Sentence Preprocessing in Mexican Spanish

## 🧠 Purpose
Provides tools to perform a preprocessing pipeline suitable for Natural Language Processing: tokenize, lemmanize, also to remove stopwords, accents and puctuation signs for Mexican Spanish senteces.


### 📚 What It Does

* **Loads** `SpaCy` models: CPU and GPU based
* **Normalizes** Lower case, remove accents and stopwords, preserving negative words
* **Processing** Extract lemmas
* **Display** Show results in CLI


Automate the cleaning 
## 🗂️ Project Structure

```
src/
├── nlp_preprocessing
│   ├── extra.yml
│   ├── sentence_preproc.py
│   │   ├── class LoadYaml
│   │   ├── class SentencePreproc
│   │   └── __main__
│   ├── sentence_preproc_trf.py
│   │   ├── class class SentencePreprocTransformer:
│   │   └── __main__
```

## 🚀 Usage

**1. Setup uv**

1.1. Inicialize uv
```
uv init
```

1.2. Configure dependencies
Add the dependecies list to the `pyproject.toml` file
```
[project]
dependencies = ['numpy', 'pandas', 'matplotlib', 'seaborn', 'pypandoc', 'spacy', 'spacy-transformers', 'es_dep_news_trf']
```

3.3. Install dependencies and activate behave
```bash
uv sync
source .venv/bin/activate
```

**2. Install CUDA-NVIDIA in Debian-based Linux Distro**

2.1. Check your GPU model in CLI:
```bash
lspci | grep -i nvidia
sudo lshw -C display

```

If the following output appears when searching for the GPU:
```bash
driver=nouveau
```
it means that no appropriate driver is installed.

2.2. To install NVIDIA drivers, first check for the recommended driver using:
```bash
sudo apt update
sudo ubuntu-drivers devices
```

2.3. Select the driver maked as *recomended*
```bash
sudo apt install -y nvidia-driver-X # use the recomended driver
nvidia-smi
```

The lastest command will show the Driver and CUDA version, and also the GPU Model.

**3. Install / update python requiered libraries using uv**

3.1. Install CuPy, PyTorch, spaCy, and the language models `es_core_news_lg` (CPU-based) and `es_dep_news_trf` (GPU-based)

```bash
uv add cupy
uv pip install --find-links https://download.pytorch.org/whl/cu128 torch==2.8.0
uv add "spacy>=3.8,<3.9" "spacy-transformers>=1.3,<2"
uv pip install https://github.com/explosion/spacy-models/releases/download/es_core_news_lg-3.8.0/es_core_news_lg-3.8.0-py3-none-any.whl
uv pip install https://github.com/explosion/spacy-models/releases/download/es_dep_news_trf-3.8.0/es_dep_news_trf-3.8.0-py3-none-any.whl

```

3.2. To test the installation copy and paste this code in the CLI
```bash
uv run python - <<'PY'
import torch
print("torch:", torch.__version__, "build:", torch.version.cuda)
print("cuda available:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("device:", torch.cuda.get_device_name(0))
PY
```

3.1a. If CuPy installation fails, try with a pre-build CyPy version:

```bash
uv remove cupy
uv add cupy-cuda12x # pre-builed version
```


**4. Running the scripts**

CPU-based
```bash
uv run -m src.NLP_Preprocessing.sentence_preproc
#or
uv run python src/NLP_Preprocessing/sentence_preproc.py
```

Transformer-based (GPU only)
```bash
uv run python src.NLP_Preprocessing.sentence_preproc_trf
#or
uv run python src/NLP_Preprocessing/sentence_preproc_trf.py
```


## 🛠️ Requirements

* Python 3.12 or higher
* pytorch 2.8.0+cu128
* CuPy
* SpaCy


## ⚠️ Notes

* Depends on models: ensure `es_core_news_lg` and `es_dep_news_trf` are downloaded
* Depends: `CUDA` and `NVIDIA` drivers are installed and available on your system.

## 🔧 TODO



