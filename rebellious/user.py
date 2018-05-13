import json
import re
import os.path

import path
import internal

# TODO: encrypt passwords

def load_session(session):
    global users

    file = open(os.path.join("session", session, "user.json"), 'r')
    obj = json.load(file)
    users, groups = obj['users'], obj['groups']
    file.close()

    if session == 'presets': # first time opening VOS, so create new user
        print("***Welcome to Rebellious! Please create an admin account below:")
        create_user(True)
    else:
        login()

def login():
    """Prompt for username and password and log that user in."""

    global current_user

    print("*Please log in:")
    username, password = input('Username: '), input('Password: ')
    while not {'username': username, 'password': password} in users:
        print("*Incorrect username or password.")
        username, password = input('Username: '), input('Password: ')
    current_user = username
    print("*User %s logged in." % current_user)

def save_session():
    file = open(os.path.join("session", "current", "user.json"), 'w')
    json.dump({ 'users': users, 'groups': groups }, file)
    file.close()

    if not current_user is None: logout()

def logout():
    """Log the current user out."""

    global current_user

    print("*User %s logged out." % current_user)
    current_user = None

def create_user(admin_=False):
    global admin

    # TODO: make it so username prompt is repeated when the passwords don't match
    username = input('Username: ')
    while not validate_name(username):
        print("*Invalid username! Username must be alphanumeric with `_`s, and cannot begin with a number.")
        username = input('Username: ')

    password, cpassword = input('Password: '), input('Confirm password: ')
    while password != cpassword:
        print("*Passwords do not match!")
        password, cpassword = input('Password: '), input('Confirm password: ')

    users.append({'username': username, 'password': password})
    user_dir = path.get('/user').create(username, path.Directory)
    run_dir = user_dir.create('run', path.Directory)
    run_dir.create('scripts', path.Directory)
    run_dir.create('programs', path.Directory)

    if admin_:
        admin = username
        print("*Congratulation! the system's admin account has been set to yours.")
    print("*Please restart for all services to work with your new account.", end=" ")
    input()
    internal.shutdown()

def validate_name(name):
    return not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name) is None

users = None
groups = None

current_user = None # make function and add getter?
admin = None
