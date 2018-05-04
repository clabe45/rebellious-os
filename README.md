# Rebellious OS
A virtual operating system built in python.

## Overview
Rebellious is an operating system that runs entirely as a process in memory.
It is cross-platform and relies only on python's core functionality.

## Explanation
Rebellious stores data in three different ways: the file system, variables and constants, and command information.
The file system mimics that of any other operating system, particularly similar to \*nix-based systems.
Plus, environment variables and system information are supported.
Most uniquely, in Rebellious, there are two types of commands: scripts and programs.
Scripts are sequences of commands with access to local and global variables.
Programs are pieces of python code that function as commands (echo and makedir are examples, but you can define your own, too).

## But, why?
Why? To reinvent the wheel. Also to improve my coding skills.

## Basic Commands
To print a string:

`echo "Hello, world!"`

To create a file `rebellious` with the text `I am rebellious`:

```
makefile rebellious
write rebellious 'I am rebellious'
```

To set an environment variable `x` equal to 2, and print it:

```
set x 2
echo <x>
```

But here's how Rebellious is unique:
it uses a very flexible alias system that defaults to a map of the commands used most to corresponding symbol notations.
For example:

```
* reblleious              # makefile reblleious
~ reblleious rebellious   # move reblleious rebellious
- rebellious              # delete rebellious
/                         # list

a = <b>                   # set a <b> (which sets `a` to the value of `b`)
```

## Full Tutorial
Coming soon!
