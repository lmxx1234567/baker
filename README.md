# Baker
## Dependent
[Anaconda](https://www.anaconda.com/) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html) with Python 3.6

[jieba](https://github.com/fxsjy/jieba) Chinese word segmentation

[paddle](https://github.com/PaddlePaddle/Paddle) NER model

[urllib3](https://pypi.org/project/urllib3/) TFX Restful API Calling

## Getting start
Use the following command to set up the environment.
```shell
conda env create --file environment.yml
```
If you have create a environment by environment.yml. Use the following command to update your env.
```shell
# Activate your env
conda activate baker

# Update env by file
conda env update -f environment.yml
```
## Usage
```shell
usage: baker.py [-h] attr filepath

Legal document parser

positional arguments:
  attr                  Select {all,case_name,case_id,year,cause,
                        trial_procedure,case_type,court,document_type,judge,clerk,
                        plaintiff_info,defendant_info,case_summary}
                        Which attributes to resolve
  filepath              Path to legal document

optional arguments:
  -h, --help            show this help message and exit
```

## Source tree
- case_parsers -- `Parser of cases`
- data
    - formatted -- `Formatted constant`
    - raw -- `Raw data input`
    - training -- `Data example for tarining`
- docs -- `Documents for developers`
- test -- `Unit test cases`
- training -- `Python notebooks for tarining `
- utils -- `Useful tools`
## Contribute
* Add dependent

    After add dependent by `conda` or `pip`. Use `conda env export --no-builds | grep -v "^prefix: " > environment.yml` to export your env configuration to a file.
* Add unittest case

    Use [unittest](https://docs.python.org/3/library/unittest.html) module to write unit test cases. Each file in the test folder corresponds to a test module which contains a set of test case defined by methods.
* Development documents

    For more developer documentation, see [this directory](md/).
