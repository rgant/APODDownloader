# APODDownloader

Download the Astronomy Picture of the Day every day, keeping only the most
recent 100 images. For use in a screensaver and wallpaper folder.

## Setup

`pylint` is configured to run spell checking in addition to linting. This requires
setting up `enchant`.

Install enchant and `pyenv` (on MacOS):

```sh
brew install enchant pyenv
```

Follow instructions for [setting up `pyenv` shell](https://github.com/pyenv/pyenv#set-up-your-shell-environment-for-pyenv).
You need to open a new shell after your `.bash_profile` (or whatever) changes.

For Silicon Macs: include `export PYENCHANT_LIBRARY_PATH=/opt/homebrew/lib/libenchant-2.2.dylib`
in your `.bash_profile` (or whatever) file to make sure that `pylint` works properly.
Without it you would encounter a `pylint` error
`argument --spelling-dict: invalid choice: 'en_US' (choose from '')`.

Setup python:

```sh
pyenv install 3.12
```

Setup `pipenv`:

```sh
pip install --user pipenv
```

> Note: If you have `PIP_REQUIRE_VIRTUALENV` then you will want to set this to
> false for this install to be outside of virtual environments.

Update your PATH to include `~/.local/bin` as per [documentation](https://pipenv.pypa.io/en/latest/installation/#preferred-installation-of-pipenv)

Sync dependencies:

```sh
pipenv sync --dev
```
