This an example Python/Django web site for displaying evolution of some variables over time.

Right now it has a set of views for:
  * `books`: books read

## Installation

It can be installed simply by cloning the repo:

```bash
$ git clone https://github.com/isilanes/django-progress.git
```

You might have to install the required python. You can do so via pip (using a virtualenv is HIGHLY recommended):

```bash
$ pip install -r conf/requirements.txt
```

## Configuration

Running `django-progress` requires defining some variables in a JSON configuration file. You can use the provided `conf/django-progress.json` sample config file directly, or make a copy and modify it to your liking. The path to the config file will be inferred at run time by checking in order:

1. The value of the environment variable `DJANGO_PROGRESS_CONF`, if provided
2. `~/.django-progress.json`, if this file exists
3. `conf/django-progress.json`, if all else fails

## Running

To run, do as with any Django project:

```bash
$ python -m manage runserver localhost:8081
```

or:

```bash
$ DJANGO_PROGRESS_CONF=/path/to/my/conf python -m manage runserver localhost:8081
```

The server can also be run with Gunicorn (edit script as appropriate):

```bash
$ bash gunicorn.sh
```

or even with Docker:

```bash
$ bash docker/build
$ bash docker/run $PWD/progress.db
```

## Example functionality

The main index:

```
http://localhost:8081/
```

## Administrative view

The administrative view can be accessed at:

```
http://localhost:8081/admin
```

The dummy database provided with this repository can be manipulated there, the user/password being admin/passwd1234.

