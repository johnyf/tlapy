#!/usr/bin/env python
"""Renumber the proof steps in a TLA+ module."""
import collections
import re


# TODO: renumber proof levels 2..5
# This renumbering could be obtained by counting from 1 and restarting the
# count whenever a new level 1 step name is encountered.


def main(fname, start_line, end_line):
    with open(fname, 'r') as f:
        lines = f.readlines()
    lines = lines[start_line : end_line]
    spec = ''.join(lines)
    # print(spec)
    level = 1
    pattern = '<{level}>\d+\.'.format(level=level)
    step_names = re.findall(pattern, spec)
    mapping = rename_steps(step_names, suffix='temp', level=level)
    s = replace_step_names(mapping, spec)
    # print(s)
    temp_names = [
        v for v in mapping.values()
        if v.endswith('.')]
    new_names = rename_steps(temp_names)
    s = replace_step_names(new_names, s)
    with open('input.tla', 'w') as f:
        f.write(spec)
    return s


def rename_steps(step_names, suffix='', level=1):
    renaming = collections.OrderedDict()
    for i, name in enumerate(step_names, 1):
        new_name = '<{level}>{i}{temp}'.format(
            level=level, i=i, temp=suffix)
        # renaming the definition of the step name
        renaming[name] = new_name + '.'
        # renaming references to the step name
        old_ref = name[:-1] + ' '
        new_ref = new_name + ' '
        renaming[old_ref] = new_ref
    return renaming

def replace_step_names(step_names, s):
    for old, new in step_names.items():
        s = s.replace(old, new)
    return s


if __name__ == '__main__':
    fname = 'demo.tla'
    start_line = 1300
    end_line = 3500
    spec = main(fname, start_line, end_line)
    with open('renumbered.tla', 'w') as f:
        f.write(spec)
