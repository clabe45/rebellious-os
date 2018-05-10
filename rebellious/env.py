import re
import json
import os.path

def validate_name(name):
    return not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name) is None

class EnvironmentDictionary(dict):
    def __setitem__(self, key, value):
        if self==variables and key in CONSTANTS: raise ValueError("Existing constant named '%s'" % key)
        if self==CONSTANTS and key in variables: raise ValueError("Existing variable named '%s'" % key)
        if not validate_name(key):
            raise ValueError("Invalid variable name: '%s'" % key)
        super().__setitem__(key, value)

def get(name, local_scope):
    """Return the value of the constant of global or local variable ``name``, searching in the following order:
    1. Constants
    2. Local variables (if ``local_scope`` is provided)
    3. Global variables
    """

    return CONSTANTS[name] if name in CONSTANTS \
        else local_scope[name] if local_scope and name in local_scope \
        else variables[name] if name in variables \
        else UNDEFINED_STRING

UNDEFINED_STRING = '{unset}'

# TODO: wait until support for datastructures (if ever)
# 'os': {
#     'name': 'yeah',
#     'version': '0.1'
# }

def load_session(session):
    global variables, CONSTANTS

    file = open(os.path.join('session', session, 'env.json'))
    obj = json.load(file)
    variables = EnvironmentDictionary()
    CONSTANTS = EnvironmentDictionary()
    for key in obj['variables']: variables[key] = obj['variables'][key]
    for key in obj['constants']: CONSTANTS[key] = obj['constants'][key]
    file.close()

def save_session():
    file = open(os.path.join('session', 'current', 'env.json'), 'w')
    json.dump({'variables': variables, 'constants': CONSTANTS}, file)
    file.close()

variables = None
CONSTANTS = None
