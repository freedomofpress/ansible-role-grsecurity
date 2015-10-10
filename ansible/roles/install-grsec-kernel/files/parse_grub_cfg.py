#!/usr/bin/env python
import re


GRUB_CONFIG = '/boot/grub/grub.cfg'
# Note that the regex is not anchored, which
# allows for preceding whitespace. All names
# for menu entries will be included in the
# matched results, including those tucked away
# in GRUB submenus. Solution via:
# http://stackoverflow.com/q/9248436/140800
GRUB_CONFIG_REGEX = r"menuentry ['\"](?P<name>.*?)['\"].*?set root='(?P<root>.*?)'"


def parse_grub_config():
    with open(GRUB_CONFIG, 'r') as f:
        grub_config = f.read()
        menu_options = re.finditer(GRUB_CONFIG_REGEX, grub_config, re.S)
        return [m.groupdict() for m in menu_options]


def formatted_results():
    formatted_results = list()
    for index, candidate in enumerate(parse_grub_config()):
        candidate['index'] = index
        formatted_results.append(candidate)
    return formatted_results


print(formatted_results())
