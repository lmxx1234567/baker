from . import schema


def get_case_name(lines: [str]) -> str:
    for line in lines:
        for trial_procedure in schema['properties']['trial_procedure']['enum']:
            if trial_procedure in line:
                return line
    return 'Not found'
