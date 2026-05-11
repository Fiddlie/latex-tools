## Install Python 3.9 or newer

fdoc is a Python CLI and needs Python ≥ 3.9.

- **macOS** — easiest via Homebrew:
  ```sh
  brew install python pipx
  pipx ensurepath
  ```
- **Linux** — most distros bundle a recent enough Python. Install `pipx` too:
  ```sh
  sudo apt install python3 python3-pip pipx
  pipx ensurepath
  ```
- **Windows** — install from [python.org](https://www.python.org/downloads/) (tick "Add Python to PATH"), then:
  ```ps
  python -m pip install --user pipx
  python -m pipx ensurepath
  ```

Verify in a terminal:

```sh
python3 --version    # 3.9+
pipx --version
```

> **Why pipx?** It installs the CLI in an isolated environment so it doesn't conflict with other Python tools.
