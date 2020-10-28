#!/usr/bin/env python
"""Replace pairs of backticks `...` with `...'.

This replacement converts inline Markdown code blocks to TLA inline code blocks.
"""
# TODO: consider converting also multi-line Markdown code blocks that are
#       delimited by ```.
import argparse


def main(fname):
    """Replace even backticks (`\\``) with `'`."""
    with open(fname, 'r') as f:
        s = f.read()
    new_s = ''
    n = 0
    for c in s:
        char = c
        if c == '`':
            n += 1
        if c == '`' and n % 2 == 0:
            char = "'"
        new_s += char
    print(new_s)


def _parse_args():
    """Return file name from command line arguments."""
    p = argparse.ArgumentParser()
    p.add_argument('-i', '--input', type=str,
                   help='input TLA+ file')
    args = p.parse_args()
    return args.input


def _test():
    fname = 'TestCodeBlockConversion.tla'
    return fname


if __name__ == '__main__':
    fname = _parse_args()
    main(fname)
