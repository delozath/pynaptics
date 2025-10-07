# Natural Language Procesing
## Sentence Preprocesing in Mexican Spanish


### Setting up
pyproject.toml
```
[project]
dependencies = ['numpy', 'pandas', 'matplotlib', 'seaborn', 'pypandoc', 'spacy', 'spacy-transformers', 'es_dep_news_trf']
```

```bash
uv sync
source .venv/bin/activate
```

**Install CUDA-nvidia**

Check for the GPU model
```bash
lspci | grep -i nvidia
sudo lshw -C display

```

Search for the GPU, if something like this is displayed
```bash
driver=nouveau
```
it means that there is no appropiated driver installed

To install Nvidia drivers, first to check for the recommended driver through
```bash
sudo apt update
sudo ubuntu-drivers devices
```

Select the driver maked as *recomended*
```bash
sudo apt install -y nvidia-driver-X #use the recomended
nvidia-smi
```

The lastest command are going to show the Driver and CUDA version, and also the GPU Model.

Install cupy, pytoch, spacy, and the models *es_core_news_lg* and *es_dep_news_trf*

```bash
uv add cupy
uv pip install --find-links https://download.pytorch.org/whl/cu128 torch==2.8.0
uv add "spacy>=3.8,<3.9" "spacy-transformers>=1.3,<2"
uv pip install https://github.com/explosion/spacy-models/releases/download/es_core_news_lg-3.8.0/es_core_news_lg-3.8.0-py3-none-any.whl
uv pip install https://github.com/explosion/spacy-models/releases/download/es_dep_news_trf-3.8.0/es_dep_news_trf-3.8.0-py3-none-any.whl

```

For testing the instalation 
```bash
uv run python - <<'PY'
import torch
print("torch:", torch.__version__, "build:", torch.version.cuda)
print("cuda available:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("device:", torch.cuda.get_device_name(0))
PY
```

### To run the scripts

CPU-based
```bash
uv run -m src.NLP_Preprocessing.NLP_sentence_preproc
```

Transformer-based (GPU only)
```bash
uv run -m src.NLP_Preprocessing.NLP_sentence_preproc_trf
```

