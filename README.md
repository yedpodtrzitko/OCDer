# OCDer

OCDer is Python utility to check if multiline collections (dicts, lists...)
have a trailing comma after their last element.


## Quick Start

OCDer can be installed from PyPi

```
$ pip install ocder
```

Now you can run it to check your code for missing trailing commas

```
$ ocder ./my/codebase
```

## Advanced Usage

By default OCDer won't modify any files, only report non-trailed items:

```
$ ocder ./my/codebase

ERROR: OCD node:
./my/codebase/schemas.py, line 2
{
    'type': 'application/json'
}
```

### Fixing Mode

**Always have a backup before running fixing mode!**


To fix non-trailed collection in files, you can use flag `--fix`:

```
$ ocder ./my/codebase/schemas.py --fix
```

### Verbose Mode

You can add `--verbose` option to get details what happened.

```
$ ocder ./my/codebase/schemas.py --fix --verbose
INFO: collecting files
INFO: starting check; workers: 1
INFO: checking ./my/codebase/schemas.py
INFO: fixing ./my/codebase/schemas.py
```

### Workers Count

OCDer uses only one worker by default.

To add more workers, use `--jobs` option followed by number of workers:

```
$ ocder ./my/codebase/schemas.py --fix --verbose --jobs 10
INFO: collecting files
INFO: starting check; workers: 10
INFO: checking ./my/codebase/schemas.py
INFO: fixing ./my/codebase/schemas.py
```

## Known Limitations

For now OCDer expects files to have utf-8 encoding. It may or may not work otherwise.

# License

OCDer is licensed under the terms of the MIT License (see the file LICENSE).


# TODO

- add CI check
