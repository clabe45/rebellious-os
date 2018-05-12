import re
import json
import os.path

import user

def validate_name(name):
    return not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name) is None

class EnvironmentDictionary(dict):
    def __init__(self, d=None):
        if not d is None:
            for key in d:   self[key] = d[key]

    def __setitem__(self, key, value):
        if self==global_variables and constants and key in constants: raise ValueError("Existing constant named '%s'" % key)
        if self==constants and global_variables and key in global_variables: raise ValueError("Existing variable named '%s'" % key)
        if not validate_name(key):
            raise ValueError("Invalid variable name: '%s'" % key)
        super().__setitem__(key, value)

def get(name, local_variables, modifier):
    """Return the value of the constant or local, entity or global variable ``name``.

    name -- (str) the name of the variable
    local_variables -- (EnvironmentDictionary) the local scope in a script or ``variables.global_``
    modifier -- (str) specifies the scope; either ``'$'`` (for local scope), ``'*'`` (for entity scope)
    or ``''`` (for global scope, including constants)
    """

    try:
        if modifier == '$':
            if not local_variables is None: return local_variables[name]
            raise ValueError('Cannot use `$` modifier in nonlocal scope!')
        if modifier == '*': return entity_variables[user.current_user][name]    # allow this level of KeyError too
        return constants[name] if name in constants else global_variables[name]
    except KeyError: return UNDEFINED_STRING

def set(name, value, local_variables, modifier):
    """Set the value of local, entity or global variable ``name`` to ``value``.

    name -- (str) the name of the variable
    value -- (str?) the value to assign to the variable
    local_variables -- (EnvironmentDictionary) the local scope in a script or ``variables.global_``
    modifier -- (str) specifies the scope; either ``'$'`` (for local scope), ``'*'`` (for entity scope)
    or ``''`` (for global scope, including constants)
    """

    if modifier == '$':
        if not local_variables is None: local_variables[name] = value
        raise ValueError('Cannot use `$` modifier in nonlocal scope!')
    if modifier == '*':
        if not user.current_user in entity_variables:
            entity_variables[user.current_user] = EnvironmentDictionary()
        entity_variables[user.current_user][name] = value
    else:
        global_variables[name] = value

def remove(name, local_variables, modifier):
    """Removes the local, entity or global variable ``name``.

    name -- (str) the name of the variable
    local_variables -- (EnvironmentDictionary) the local scope in a script or ``variables.global_``
    modifier -- (str) specifies the scope; either ``'$'`` (for local scope), ``'*'`` (for entity scope)
    or ``''`` (for global scope, including constants)
    """

    if modifier == '$':
        if not local_variables is None: del local_variables[name]
        raise ValueError('Cannot use `$` modifier in nonlocal scope!')
    if modifier == '*': del entity_variables[user.current_user][name]   # allow this level of KeyError to be raised too
    del global_variables[name]

def list(local_variables, modifier):
    """Return the map of the scope for the current modifier, or a tuple of the global variables and constants, respectively."""

    if modifier == '$':
        if not local_variables is None: return local_variables
        raise ValueError('Cannot use `$` modifier in nonlocal scope!')
    if modifier == '*': return entity_variables[user.current_user] if user.current_user in entity_variables else {}
    return (global_variables, constants)

def load_session(session):
    global entity_variables, global_variables, constants

    file = open(os.path.join('session', session, 'env.json'))
    obj = json.load(file)
    entity_variables = {}   # dict of `EnvironmentDictionary`s
    # entity (user/group) variables
    for entity_name in obj['variables']['entity']:   # list
        entity = obj['variables']['entity'][entity_name]
        entity_variables[entity_name] = EnvironmentDictionary(entity)
    # global variables
    global_variables = EnvironmentDictionary(obj['variables']['global'])
    # global constants
    constants = EnvironmentDictionary(obj['constants'])
    file.close()

def save_session():
    file = open(os.path.join('session', 'current', 'env.json'), 'w')
    json.dump({'variables': {'entity': entity_variables, 'global': global_variables}, 'constants': constants}, file)
    file.close()

entity_variables = None
global_variables = None
constants = None

UNDEFINED_STRING = '{unset}'
