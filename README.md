# mswappinit

This package is expected to only be used by @mwartell for personal development projects.
I've published it only after copying it into my third new project and figured an import
would be easier. Others are certainly welcome to use it, but I'd be surprised.

This library provides three application bootstrap utilites
1. project - a configuration dotenv loader that makes nice parameter accessors
2. log - a logger that is pleasing to the author
3. quickdb - a pickledb instance for quick and dirty persistence

dotenv is used to load environment variables from a file named .env
these could be something like: `AWS_PROFILE=cluster` and these
will all be loaded into the environment as expected.

this module provides convenience attribute access to project specificlog
variables that are loaded from the dotenv file. A PROJECT_NAME must
be defined and then all other variables of the form {PROJECT_NAME}_{VAR}
can be accessed as attributes of the project object.

For example, if the PROJECT_NAME is "rag" and the dotenv file contains
`RAG_DATA=/path/to/data` then the value of `project.data` will be the
Path object `/path/to/data`.

For convenience, the values are upcast to the most likely type. For example,
if the value is "true" or "false" it will be converted to a boolean. If the
value is a number it will be converted to an int or float. If the value is a
