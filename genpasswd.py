#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Password generating script for UNIX based systems
It uses system entropy (/dev/urandom) for password generation

Copyright (C) 2018-2019 _kodokami
"""
__author__ = '_kodokami <kodokami@protonmail.com>'
__version__ = '1.3.2'

import os
import sys
import random
import argparse
from argparse import ArgumentTypeError
from enum import Enum

_LOWERCASE = (
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'r', 's', 't',
    'u', 'v', 'w', 'x', 'y', 'z'
)
_LOWERCASE_SAFE = (
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'm', 'n', 'o', 'p', 'r', 's', 't', 'u',
    'v', 'w', 'x', 'y', 'z'
)
_UPPERCASE = (
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'R', 'S', 'T',
    'U', 'V', 'W', 'X', 'Y', 'Z'
)
_UPPERCASE_SAFE = (
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'R', 'S', 'T', 'U', 'V',
    'W', 'X', 'Y', 'Z'
)
_NUMBERS = ('1', '2', '3', '4', '5', '6', '7', '8', '9', '0')
_NUMBERS_SAFE = ('1', '2', '3', '4', '5', '6', '7', '8', '9')
_SPECIAL = ('!', '@', '#', '$', '%', '^', '&', '*', '(', ')')


class PasswordType(Enum):
    NUMERIC = 'num'
    LOWERCASE = 'low'
    UPPERCASE = 'upp'
    STANDARD = 'std'


def _positive(value):
    try:
        value = int(value)
        if value <= 0: raise ArgumentTypeError('value should be a positive number')
    except ValueError:
        ArgumentTypeError('value should be a positive number')
    return value


def _pass_type(value):
    valid_types = {
        'num': PasswordType.NUMERIC, 'numeric': PasswordType.NUMERIC,
        'low': PasswordType.LOWERCASE, 'lowercase': PasswordType.LOWERCASE,
        'upp': PasswordType.UPPERCASE, 'uppercase': PasswordType.UPPERCASE,
        'std': PasswordType.STANDARD, 'standard': PasswordType.STANDARD
    }
    if not isinstance(value, str) or value.lower() not in valid_types.keys():
        raise ArgumentTypeError('unsupported password type')
    else:
        return valid_types[value.lower()]


def commandmaker():
    script_name = sys.argv[0].split('/')[-1]
    script_desc = 'password generating script for UNIX based systems\n' \
                  'it uses system entropy (/dev/urandom) for password generation'
    parser = argparse.ArgumentParser(prog=script_name, description=script_desc,
                                     epilog='---\nCopyright (C) 2018-2019 _kodokami',
                                     formatter_class=argparse.RawTextHelpFormatter,
                                     add_help=False)

    # password options
    pass_args = parser.add_argument_group(title='password options')

    pass_args.add_argument('password_type', action='store', metavar='TYPE', type=_pass_type,
                           help='password type, available options:\n'
                                '  - num | numeric    - numeric password (PIN)\n'
                                '  - low | lowercase  - alfanumeric password with lowercase only characters\n'
                                '  - upp | uppercase  - alfanumeric password with uppercase only characters\n'
                                '  - std | standard   - standard alphanumeric password with lower- and uppercase characters')

    pass_args.add_argument('-c', '--characters-count', action='store', type=_positive,
                           help='describes how long the password should be (def: 12)',
                           default=12, required=False, metavar='COUNT')

    pass_args.add_argument('-s', '--special-characters', action='store_true',
                           help='adds special characters to the pool', dest='special')

    pass_args.add_argument('-S', '--safe', action='store_true',
                           help='removes confusing characters from pool (l, I, O, 0, etc.)')

    # script options
    script_args = parser.add_argument_group(title='other')

    script_args.add_argument('-p', '--password-count', action='store', type=_positive,
                             help='described how many passwords should be generated (def: 3)',
                             default=3, required=False, metavar='COUNT')

    script_args.add_argument('--compact', action='store_true',
                             help='inline compact view, with space as password separator')

    script_args.add_argument('-v', '--version', action='version',
                             version=f'{script_name} v{__version__}',
                             help='show script version and exit')

    script_args.add_argument('-h', '--help', action='help', help='show this help message and exit')

    return parser.parse_args()


def character_pool_generator(pass_type, special_characters=False, safe_mode=False):
    character_pool = _NUMBERS_SAFE if safe_mode else _NUMBERS
    if pass_type in (PasswordType.STANDARD, PasswordType.LOWERCASE):
        character_pool += _LOWERCASE_SAFE if safe_mode else _LOWERCASE
    if pass_type in (PasswordType.STANDARD, PasswordType.UPPERCASE):
        character_pool += _UPPERCASE_SAFE if safe_mode else _UPPERCASE
    if special_characters:
        character_pool += _SPECIAL
    return character_pool


def passwords_generator(character_pool, pass_size, pass_count):
    passwords = []
    try:
        random.seed(os.urandom(128))
        for _ in range(pass_count):
            passwords.append(
                str.join('', random.choices(character_pool, k=pass_size))
            )
    except NotImplementedError as err:
        print(f'ERR: could not read /dev/urandom, original message:\n\t{err}')

    return passwords


def print_passwords(passwords, compact=False):
    for i, password in enumerate(passwords):
        if compact:
            print(password, end=' ')
        else:
            print(password, end='    ' if (i + 1) % 3 != 0 else '\n')


def script():
    args = commandmaker()
    passwords = passwords_generator(
        character_pool_generator(args.password_type, args.special, args.safe),
        args.characters_count,
        args.password_count
    )
    print_passwords(passwords, args.compact)


if __name__ == '__main__':
    try:
        script()
    except KeyboardInterrupt:
        print('Keyboard interrupt - exiting')
