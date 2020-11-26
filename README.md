# Baker
## Dependent
[Anaconda](https://www.anaconda.com/) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html) with Python 3.6+
## Getting start
Use the following command to set up the environment.
```shell
conda env create --file environment.yml [-p /path/to/save/env]
```
## Source tree
- data
    - formatted -- `Formated data output`
    - raw -- `Raw data input`
## Contribute
* Add dependent

    After add dependent by `conda` or `pip`. Use `conda env export | grep -v "^prefix: " > environment.yml` to export your env configuration to a file.

**TBC**

