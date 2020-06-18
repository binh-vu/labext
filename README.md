# Overview

![Demo](./assets/demo.png)

# Installation

To use this with JupyterLab, you need to have `requirejs` enable in Jupyter by installing either:

1. https://github.com/DraTeots/jupyterlab_requirejs (jupyterlab version <= 1.*)
2. https://github.com/binh-vu/jupyterlab_requirejs  (jupyterlab version >= 2.*)

Beside `requirejs`, you also need to have `ipywidgets` and `ipyevents`:

```bash
pip install ipywidgets
jupyter nbextension enable --py widgetsnbextension
jupyter labextension install @jupyter-widgets/jupyterlab-manager
```

```bash
pip install ipyevents
jupyter nbextension enable --py --sys-prefix ipyevents
jupyter labextension install @jupyter-widgets/jupyterlab-manager ipyevents
```