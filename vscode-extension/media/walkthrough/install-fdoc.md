## Install the fdoc CLI

The extension shells out to `fdoc` for every operation, so it needs to be on your PATH.

```sh
pipx install "git+ssh://git@github.com/Fiddlie/latex-tools.git#subdirectory=cli"
```

If you don't have SSH access to the GitHub repo, use HTTPS:

```sh
pipx install "git+https://github.com/Fiddlie/latex-tools.git#subdirectory=cli"
```

Verify:

```sh
fdoc --version
```

If `fdoc` isn't on PATH, set **fdoc › Cli Path** in settings to the absolute path returned by `which fdoc` (`where fdoc` on Windows).
