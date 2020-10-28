#!/usr/bin/env python
"""Rewrite title and horizontal rules to fill the column width."""
import argparse
import logging
import math
import re


DEFAULT_COLUMN_WIDTH = 80
log = logging.getLogger(__name__)


def main(fname, fout, column_width):
    with open(fname, 'r') as f:
        lines = f.readlines()
    eof_newline = lines[-1].endswith('\n')
    lines = [line.rstrip('\n') for line in lines]
    new_lines = _balance_lines(lines, column_width)
    s = '\n'.join(new_lines)
    if eof_newline:
        s += '\n'
    with open(fout, 'w') as f:
        f.write(s)


def _balance_lines(lines, column_width):
    new_lines = list()
    for line in lines:
        new_line = _balance_line(line, column_width)
        _log_change(line, new_line)
        new_lines.append(new_line)
    return new_lines


def _balance_line(line, column_width):
    if 'MODULE' in line:
        return _balance_title(line, column_width)
    assert 'MODULE' not in line, line
    if '----' in line:
        return _balance_hrule(line, '-', column_width)
    if '====' in line:
        return _balance_hrule(line, '=', column_width)
    return line


def _balance_title(line, column_width):
    rt = '-----*\s*MODULE\s*([a-zA-Z0-9_]*)\s*-----*'
    m = re.match(rt, line)
    module_name, = m.groups()
    title = ' MODULE {name} '.format(name=module_name)
    n_dashes = column_width - len(title)
    half = n_dashes / 2
    n = int(math.floor(half))
    m = int(math.ceil(half))
    assert n + m == n_dashes, (n, m, n_dashes)
    assert n + m + len(title) == column_width, (
        n, m, title, column_width)
    before = '-' * n
    after = '-' * m
    new_line = before + title + after
    assert len(new_line) == column_width, (
        new_line, column_width)
    return new_line


def _balance_hrule(line, char, column_width):
    chars = set(line)
    assert chars == {char}, (chars, char)
    return column_width * char


def _log_change(line, new_line):
    if line == new_line:
        return
    msg = 'Line changed from:\n{a}\nto\n{b}\n'.format(
        a=line, b=new_line)
    log.info(msg)


def _parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('-i', '--input', type=str,
                   help='input TLA+ file')
    p.add_argument('-o', '--output', type=str,
                   help='output TLA+ file')
    p.add_argument('-w', '--column-width', type=int,
                   default=DEFAULT_COLUMN_WIDTH,
                   help='desired text width in characters')
    args = p.parse_args()
    fin = args.input
    fout = args.output
    column_width = args.column_width
    return fin, fout, column_width

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    fin, fout, column_width = _parse_args()
    main(fin, fout, column_width)
