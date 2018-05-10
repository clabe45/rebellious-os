from os import mkdir
import os.path

import path
import run
import env

def load_presets():
    for module in (path, run, env):     # path has to be before run
        module.load_session('presets')

def load_current():
    for module in (path, run, env):
        module.load_session('current')

def save():
    dir = os.path.join('session', 'current')
    if not os.path.exists(dir): mkdir(dir)
    for module in (path, run, env):
        module.save_session()   # implies 'current'
