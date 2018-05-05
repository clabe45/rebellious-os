import re

# TODO: see if I can override the set operator when something like `variables['x'] = '10'` occurs

UNDEFINED_STRING = '{undefined}'

variables = {}
CONSTANTS = {
    'OS-NAME': 'Rebellious',
    'OS-VERSION': '0.1'
    # TODO: wait until support for datastructures (if ever)
    # 'os': {
    #     'name': 'yeah',
    #     'version': '0.1'
    # }
}

def validate_varname(name):
    return not re.match(r'^[a-zA-Z0-9_]+$', name) is None
