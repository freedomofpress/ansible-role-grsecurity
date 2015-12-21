#!/usr/bin/env python
DOCUMENTATION = '''
---
module: grub_menu_options
short_description: Gather facts for GRUB boot menu options
description:
  - Gather name, root, and index info for GRUB menu selections
author:
    - Conor Schaefer (@conorsch)
    - Freedom of the Press Foundation (@freedomofpress)
requirements:
    - GRUB
options:
  grub_config:
    description:
      - location of the GRUB config file
    default: "/boot/grub/grub.cfg"
    required: no
notes:
  - Module preserves the order of menu entries from the GRUB config file
    and assigns the "index" attribute accordingly, starting at 0.
'''
EXAMPLES = '''
- action: grub_menu_options
'''

import re


# Note that the regex is not anchored, which allows for preceding whitespace.
# All names # for menu entries will be included in the matched results,
# including those tucked away in GRUB submenus. Solution adapted from:
# http://stackoverflow.com/q/9248436/140800
GRUB_CONFIG_REGEX = r"menuentry ['\"](?P<name>.*?)['\"].*?(set root='(?P<root>.*?))?'"


def parse_grub_config(grub_config_filepath):
    """
    Read in GRUB config file and return a list of named groups
    for menu entries.
    """
    with open(grub_config_filepath, 'r') as f:
        grub_config = f.read()
        menu_options = re.finditer(GRUB_CONFIG_REGEX, grub_config, re.S)
        return [m.groupdict() for m in menu_options]


def formatted_results(grub_config_filepath):
    """
    Reformat GRUB menu entries as Ansible facts.
    """
    formatted_results = list()
    for index, candidate in enumerate(parse_grub_config(grub_config_filepath)):
        candidate['index'] = index
        formatted_results.append(candidate)
    return dict(grub_menu_options=formatted_results)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            grub_config=dict(default="/boot/grub/grub.cfg"),
        ),
        supports_check_mode=False
    )
    grub_config = module.params['grub_config']

    try:
        results = formatted_results(grub_config)
    except IOError:
        msg = ("Could not find GRUB config file at {} . "
              "Check that the file exists and is readable. "
              "You can specify a custom filepath "
              "via the 'grub_config' module parameter.").format(grub_config)
        module.fail_json(msg=msg)

    if len(results['grub_menu_options']) >= 1:
        module.exit_json(changed=False, ansible_facts=results)
    else:
        msg = "Failed to parse GRUB config file {}".format(grub_config)
        module.fail_json(msg=msg)


from ansible.module_utils.basic import *
main()
