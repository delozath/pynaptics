# Natural Language Procesing
## Sentence Preprocesing in Mexican Spanish

```
[project]
dependencies = ['numpy', 'pandas', 'matplotlib', 'seaborn', 'pypandoc', 'spacy', 'spacy-transformers', 'es_dep_news_trf']
```

```bash
uv sync
source .venv/bin/activate
```

```bash
lspci | grep -i nvidia
sudo lshw -C display

```

buacar GeForce

driver=nouveau -> no cuda

```bash
sudo apt update
sudo ubuntu-drivers devices
```

driver   : nvidia-driver-580-open - distro non-free recommended

```bash
sudo apt install -y nvidia-driver-580-open
nvidia-smi

uv pip install --find-links https://download.pytorch.org/whl/cu128 torch==2.8.0
uv add "spacy>=3.8,<3.9" "spacy-transformers>=1.3,<2"
uv pip install https://github.com/explosion/spacy-models/releases/download/es_dep_news_trf-3.8.0/es_dep_news_trf-3.8.0-py3-none-any.whl


uv run python - <<'PY'
import torch
print("torch:", torch.__version__, "build:", torch.version.cuda)
print("cuda available:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("device:", torch.cuda.get_device_name(0))
PY
```
uv pip install https://github.com/explosion/spacy-models/releases/download/es_core_news_lg-3.8.0/es_core_news_lg-3.8.0-py3-none-any.whl
