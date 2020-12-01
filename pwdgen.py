#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Password generator for UNIX based systems
It uses the system entropy (/dev/urandom) for password generation

Copyright (C) 2018-2020 _kodokami
"""
__author__ = '_kodokami <kodokami@protonmail.com>'
__version__ = '2.0.1'

import os
import sys
import random
from argparse import ArgumentParser, ArgumentTypeError, RawTextHelpFormatter
from enum import Enum

# character collections
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
    NUMERIC = 1
    LOWERCASE = 2
    UPPERCASE = 3
    STANDARD = 4


def _positive_num(value):
    try:
        value = int(value)
        if value <= 0: raise ArgumentTypeError('should be a positive number')
    except ValueError:
        ArgumentTypeError('should be a positive number')
    return value


_VALID_PASS_TYPES = {
    'num': PasswordType.NUMERIC, 'numeric': PasswordType.NUMERIC,
    'low': PasswordType.LOWERCASE, 'lowercase': PasswordType.LOWERCASE,
    'upp': PasswordType.UPPERCASE, 'uppercase': PasswordType.UPPERCASE,
    'std': PasswordType.STANDARD, 'standard': PasswordType.STANDARD
}


def _pass_type(value):
    if not isinstance(value, str) or value.lower() not in _VALID_PASS_TYPES.keys():
        raise ArgumentTypeError('unsupported password type')
    return _VALID_PASS_TYPES[value.lower()]


def commandmaker():
    name = os.path.basename(sys.argv[0]).split('.')[0]
    desc = 'password generator for UNIX based systems\n' \
           'it uses the system entropy (/dev/urandom) for password generation'
    foot = 'Copyright (C) 2018-2020 _kodokami'

    parser = ArgumentParser(prog=name, description=desc, epilog=foot, add_help=False)
    parser.formatter_class = RawTextHelpFormatter

    # password options
    pass_args = parser.add_argument_group(title='password options')

    pass_args.add_argument(
        '-t', '--password-type', action='store', metavar='TYPE', type=_pass_type,
        help='password type (def: standard), available options:\n'
             '  - num | numeric    - numeric password (PIN)\n'
             '  - low | lowercase  - alphanumeric password with lowercase characters only\n'
             '  - upp | uppercase  - alphanumeric password with uppercase characters only\n'
             '  - std | standard   - standard alphanumeric password with mixed characters',
        default='std', required=False
    )

    pass_args.add_argument(
        '-l', '--password-length', action='store', type=_positive_num,
        help='password length (def: 12)',
        default=12, required=False, metavar='LENGTH'
    )

    pass_args.add_argument(
        '-s', '--special-characters', action='store_true',
        help='adds special characters to the pool', dest='special'
    )

    pass_args.add_argument(
        '-S', '--safe', action='store_true',
        help='removes confusing characters from pool (l, I, O, 0, etc.)'
    )

    # script options
    script_args = parser.add_argument_group(title='other')

    script_args.add_argument(
        '-c', '--passwords-count', action='store', type=_positive_num,
        help='describes how many passwords should be generated (def: 3)',
        default=3, required=False, metavar='COUNT'
    )

    script_args.add_argument(
        '--compact', action='store_true', help='compact view with space as a separator'
    )

    script_args.add_argument(
        '-v', '--version', action='version', version=f'{name} v{__version__}',
        help='show program version and exit'
    )

    script_args.add_argument(
        '-h', '--help', action='help', help='show this help message and exit'
    )

    return parser.parse_args()


def get_character_pool(pass_type, special_characters=False, safe_mode=False):
    character_pool = _NUMBERS_SAFE if safe_mode else _NUMBERS

    if pass_type in (PasswordType.STANDARD, PasswordType.LOWERCASE):
        character_pool += _LOWERCASE_SAFE if safe_mode else _LOWERCASE

    if pass_type in (PasswordType.STANDARD, PasswordType.UPPERCASE):
        character_pool += _UPPERCASE_SAFE if safe_mode else _UPPERCASE

    if special_characters:
        character_pool += _SPECIAL

    return character_pool


def generate_passwords(character_pool, pass_size, pass_count):
    try:
        random.seed(os.urandom(128))
        return [
            str.join('', random.choices(character_pool, k=pass_size)) for _ in range(pass_count)
        ]

    except NotImplementedError as err:
        # Exception taken from documentation:
        # https://docs.python.org/3.8/library/os.html#os.urandom
        print(f'ERR: could not read /dev/urandom, original message:\n\t{err}')
        return []


def print_results(passwords, compact=False):
    if not compact:
        for i in range(0, len(passwords), 3):
            print(str.join('    ', passwords[i:i + 3]))
    else:
        print(str.join(' ', passwords))


if __name__ == '__main__':
    try:
        args = commandmaker()
        passwords = generate_passwords(
            get_character_pool(args.password_type, args.special, args.safe),
            args.password_length,
            args.passwords_count
        )
        print_results(passwords, args.compact)

    except KeyboardInterrupt:
        print('Keyboard interrupt - exiting')
