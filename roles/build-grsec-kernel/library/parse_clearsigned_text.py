#!/usr/bin/env python
# -*- coding: utf-8 -*-

# (c) 2016, Freedom of the Press Foundation
# Written by Noah Vesely <noah at freedom.press>
#
# This module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software.  If not, see <http://www.gnu.org/licenses/>.
#

DOCUMENTATION = '''
---
module: parse_clearsigned_text
short_description: Warns on unexpected formatting in single-sig clearsigned
files and weak hash use.
desription:
  - Checks each file passed to ensure that it only contains a single part,
cleartext signed, ASCII armored PGP message conforming to RFC 4880 and nothing
else. It also checks that a strong hash was used (opt. disabled).
version_added: "2.0.1.0"
options:
  file:
    description:
      - The file(s) to be checked.
    required: true
    default: null
  warn_on_weak_hash:
    description: 
      - By default a warning is issued if SHA256 or SHA512 was not used for the
signature.
    required: false
    default: true
requirements: [ ]
author:
    - Noah Vesely (@fowlslegs)
notes:
  - See https://github.com/freedomofpress/ansible-role-grsecurity/issues/60 for
an explanation of the sort attack this script was written to defend against.
'''

EXAMPLES = '''
# Check "foo" file
- parse_clearsigned_text: file=foo.asc

# Check "foo" file and don't warn on use the use of a weak hash
- parse_clearsigned_text: file=foo.asc warn_on_weak_hash=false
'''

RETURN='''
'''

# import argparse

# parser = argparse.ArgumentParser(description='''Checks each file passed to 
# ensure that it only contains a single part, cleartext signed, ASCII armored
# PGP message conforming to RFC 4880 and nothing else. It also checks that a
# strong hash was used (opt. disabled).''')
# parser.add_argument('files', type=argparse.FileType(), nargs='+', help='''one or
#                     more cleartext signed, ASCII armored PGP messages''')
# parser.add_argument('--allow-weak-hashes', action='store_true', 
#                     help='don\'t warn on use of weak/ broken hash')
# args = parser.parse_args()

def parse_files(files, warn_on_weak_hash):
    for fh in files:
        try:
            assert next(fh) == '-----BEGIN PGP SIGNED MESSAGE-----\n', \
                    begin_message_error(fh)

            if warn_on_weak_hash:
                assert next(fh) in ["Hash: {}\n".format(alg)
                                    for alg in SAFE_HASH_ALGS], \
                        hash_error(fh)
            else:
                next(fh)

            assert next(fh) == '\n', empty_line_error(fh)

            # 'True' is not a kwd in Py2 and instead a built-in global constant
            # assigned to 1. Using 1 directly removes a layer of indirection,
            # runs faster.
            while 1:
                line = next(fh)
                if line.startswith('-'):
                    if line == '-----BEGIN PGP SIGNATURE-----\n':
                        break
                    else:
                        assert line.startswith('- '), \
                        dash_escape_error(line, fh)

            while 1:
                line = next(fh)
                if line == '-----END PGP SIGNATURE-----\n':
                    break
            try:
                assert next(fh), end_sig_error(fh)
            except StopIteration:
                pass

        except StopIteration:
            print(abrupt_file_end_error(fh))
            raise 
        except:
            print(fh)
            raise
        finally:
            fh.close()

SAFE_HASH_ALGS = ['SHA256', 'SHA512']

def begin_message_error(file):
    return '''The cleartext signed PGP message does not begin with a \
cleartext header. Thus, the file "{}" may contain unsigned \
text.'''.format(file.name)

def hash_error(file):
    return '''The cleartext signed PGP message "{}" does not correctly specify \
its "Hash" Armor Header. This can result in a downgrade attack to a broken 
hash function like MD5.'''.format(file.name)

def empty_line_error(file):
    return '''The cleartext signed PGP message "{}" does not follow the OpenPGP \
specification to leave one empty line after the "Hash" Armor \
Header.'''.format(file.name)

def end_sig_error(file):
    return '''The Armor Tail of the cleartext signed PGP message's ASCII \
armored signature is not the last line of the file. Thus, the file {} may \
contain unsigned text.'''.format(file.name)

def dash_escape_error(line, file):
    return '''The line "{}" in the cleartext body of the cleartext signed PGP \
message {} is not properly dash escaped.'''.format(line, file.name)

def abrupt_file_end_error(file):
    return '''The file "{}" abruptly ended and does not consitute a valid \
cleartext signed PGP message.'''.format(file.name)

def main():
    module = AnsibleModule(
        argument_spec = dict(
            files             = dict(required=True, default=None, type='list'),
            warn_on_weak_hash = dict(type='bool')
            )
        )
    p = module.params
    parse_files(p['files'], p['warn_on_weak_hash'])

from ansible.module_utils.basic import *
if __name__ == "__main__":
    main()
