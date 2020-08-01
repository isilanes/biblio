This an example Python/Django web site for displaying evolution books read over time.

## Installation

It can be installed simply by cloning the repo:

```bash
$ git clone https://github.com/isilanes/biblio.git
```

You might have to install the required python. You can do so via pip (using a virtualenv is HIGHLY recommended):

```bash
$ pip install -r conf/requirements.txt
```

## Configuration

Running `biblio` requires defining some variables in a JSON configuration file. You can use the provided `conf/biblio.json` sample config file directly, or make a copy and modify it to your liking. The path to the config file will be inferred at run time by checking in order:

1. The value of the environment variable `DJANGO_BIBLIO_CONF`, if defined
2. `~/.biblio.json`, if this file exists

## Running

To run, do as with any Django project:

```bash
$ python -m manage runserver localhost:8081
```

or:

```bash
$ DJANGO_BIBLIO_CONF=/path/to/my/conf python -m manage runserver localhost:8081
```
