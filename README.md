# deephaven-ipywidgets

Deephaven Community IPython Widget Library

## Installation

You can install using `pip`:

```bash
pip install deephaven-ipywidgets
```

If you are using Jupyter Notebook 5.2 or earlier, you may also need to enable
the nbextension:

```bash
jupyter nbextension enable --py [--sys-prefix|--user|--system] deephaven-ipywidgets
```

## Usage

### Starting the server

First you'll need to start the [Deephaven server](https://github.com/deephaven/deephaven-core/blob/d73ef01cdf6fda43f7d03110995add26d16d4eae/py/embedded-server/README.md).

```python
# Start up the Deephaven Server
from deephaven_server import Server
s = Server(port=8080)
s.start()
```

### Display Tables

Pass the table into a `DeephavenWidget` to display a table:

```python
# Create a table and display it
from deephaven import empty_table
from deephaven_ipywidgets import DeephavenWidget
t = empty_table(1000).update("x=i")
display(DeephavenWidget(t))
```

You can also pass in the size you would like the widget to be:

```python
# Specify a size for the table
display(DeephavenWidget(t, width=100, height=250))
```

### Alternate Deephaven Server URL
By default, the Deephaven server is located at `http://localhost:{port}`, where `{port}` is the port set in the Deephaven server creation call. If the server is not there, such as when running a Jupyter notebook in a Docker container, modify the `DEEPHAVEN_IPY_URL` environmental variable to the correct URL before creating a `DeephavenWidget`. 
```python
import os 
os.environ["DEEPHAVEN_IPY_URL"] = "http://localhost:1234"
```
## Development Installation

Before starting, you will need [python3](https://www.python.org/downloads/), [node](https://nodejs.org/en/download/), and [yarn](https://classic.yarnpkg.com/lang/en/docs/install/) installed.

Create and source a dev python venv environment:

```bash
export JAVA_HOME=/Library/Java/JavaVirtualMachines/openjdk-11.jdk/Contents/Home
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip setuptools
pip install deephaven-server jupyter jupyterlab jupyter-packaging
```

After initial installation/creation, you can just do

```bash
source .venv/bin/activate
```

Install the python. This will also build the TS package.

```bash
pip install -e ".[test, examples]"
```

When developing your extensions, you need to manually enable your extensions with the
notebook / lab frontend. For lab, this is done by the command:

```
jupyter labextension develop --overwrite .
yarn run build
```

For classic notebook, you need to run:

```
jupyter nbextension install --sys-prefix --symlink --overwrite --py deephaven_ipywidgets
jupyter nbextension enable --sys-prefix --py deephaven_ipywidgets
```

Note that the `--symlink` flag doesn't work on Windows, so you will here have to run
the `install` command every time that you rebuild your extension. For certain installations
you might also need another flag instead of `--sys-prefix`, but we won't cover the meaning
of those flags here.

For running in VS Code, you need to run the classic notebook steps, as well as set up the VS Code environment:

1. Create a `.env` file with your `JAVA_HOME` variable set, e.g.

```bash
JAVA_HOME=/Library/Java/JavaVirtualMachines/openjdk-11.jdk/Contents/Home
```

2. Create a new notebook (.ipynb) or open an existing notebook file (such as [example.ipynb](./example.ipynb))
3. In the notebook, make sure your `.venv` Python environment is selected - either use the dropdown menu in the top right, or hit `Ctrl + P` then type `> Select Kernel` and select the `Notebook: Select Notebook Kernel` option and choose `.venv`.

### How to see your changes

#### Typescript:

If you use JupyterLab to develop then you can watch the source directory and run JupyterLab at the same time in different
terminals to watch for changes in the extension's source and automatically rebuild the widget.

```bash
# Watch the source directory in one terminal, automatically rebuilding when needed
yarn run watch
# Run JupyterLab in another terminal
jupyter lab
```

After a change wait for the build to finish and then refresh your browser and the changes should take effect.

#### Python:

If you make a change to the python code then you will need to restart the notebook kernel to have it take effect.

## Releasing your initial packages:

- Add tests
- Ensure tests pass locally and on CI. Check that the coverage is reasonable.
- Make a release commit, where you remove the `, 'dev'` entry in `_version.py`.
- Update the version in `package.json`
- Relase the npm packages:
  ```bash
  npm login
  npm publish
  ```
- Install publish dependencies:

```bash
pip install build twine
```

- Build the assets and publish
  ```bash
  python -m build .
  twine check dist/*
  twine upload dist/*
  ```
- Tag the release commit (`git tag <python package version identifier>`)
- Update the version in `_version.py`, and put it back to dev (e.g. 0.1.0 -> 0.2.0.dev).
  Update the versions of the npm packages (without publishing).
- Commit the changes.
- `git push` and `git push --tags`.
