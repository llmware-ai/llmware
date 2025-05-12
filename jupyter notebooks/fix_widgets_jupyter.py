import os
import nbformat

def fix_notebook_metadata(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=nbformat.NO_CONVERT)

    # Remove broken widgets metadata
    if 'widgets' in nb.metadata:
        if 'application/vnd.jupyter.widget-state+json' in nb.metadata['widgets']:
            widget_meta = nb.metadata['widgets']['application/vnd.jupyter.widget-state+json']
            if 'state' not in widget_meta:
                print(f"[FIXING] {file_path}")
                widget_meta['state'] = {}

    with open(file_path, 'w', encoding='utf-8') as f:
        nbformat.write(nb, f)

# Walk through all notebooks
for root, _, files in os.walk("../examples/Notebooks"):
    for file in files:
        if file.endswith(".ipynb"):
            fix_notebook_metadata(os.path.join(root, file))
