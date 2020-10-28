#!/usr/bin/env python
"""Convert TLA+ to LaTeX using `tla2tex.TeX`, then extract the result.

To use this script, create a directory named `__tlacache__/.tla2tex`
in the directory where you compile your LaTeX document.

Each `tla` environment is dumped to a file that is named using the
MD5 hash of environment's contents. If the contents remain the same,
then `tla2tex.TeX` is not called again.

Garbage collection is implemented by pickling lists of file names,
and removing unused files when called with the option `--remove-outdated`.
The option `--only-included` preserves files used by LaTeX files that
are absent from the `\includeonly` command.

Assumption: The LaTeX document does not include any file named `undefined.tex`.
"""
# Copyright 2017 by California Institute of Technology
# All rights reserved. Licensed under 3-clause BSD.
#
import argparse
import filecmp
import logging
import os
import pickle
import shutil
import subprocess


TLAENV = 'tlaenv'
log = logging.getLogger(__name__)
template = '''\
\\input{{tex/preamble}}
\\begin{{document}}
\\begin{{tla}}
{spec}
\\end{{tla}}
\\end{{document}}
'''
SKIP = 2  # [pt] whitespace above and below each environment
CACHE_DIR = '__tlacache__/.tla2tex'
MEMO_FILE = 'memoization_file_names.pickle'
OLD_MEMO_FILE = 'memoization_file_names_old.pickle'
MEMO_INCLUDEONLY = os.path.join(CACHE_DIR, 'included.pickle')


def main():
    """Entry point."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    # args
    fname = 'tla2tex_input.tex'
    fin, fout, clean, fnames = _parse_args()
    if clean:
        _collect_garbage(fnames)
        return
    # memoization file
    base, _ = os.path.splitext(fout)
    old = '{base}_old.tla'.format(base=base)
    if _is_unchanged(fin, fout, old):
        _record_file_name(fout, old)
        return
    with open(fin, 'r') as f:
        s = f.read()
    call_tla2tex(s, fname)
    lines = _load_tex(fname)
    _dump_tex(lines, fout)
    # update the copy, after successful conversion
    shutil.copy(fin, old)
    _record_file_name(fout, old)


def _record_file_name(fout, old):
    memo, old_memo = _memo_file_names()
    if os.path.isfile(memo):
        with open(memo, 'rb') as f:
            p = pickle.load(f)
    else:
        p = set()
    p.add(fout)
    p.add(old)
    with open(memo, 'wb') as f:
        pickle.dump(p, f)


def _parse_args():
    """Return input and output file names."""
    p = argparse.ArgumentParser()
    p.add_argument('-i', '--input', type=str,
                   help='input file')
    p.add_argument('-o', '--output', type=str,
                   help='output file')
    p.add_argument('--remove-outdated', action='store_true',
                   help='delete unused memoization files')
    p.add_argument('--only-included', type=str,
                   help='restrict deletion to memo for these TeX files')
    args = p.parse_args()
    fin = args.input
    fout = args.output
    clean = args.remove_outdated
    fnames = _split_included_file_names(args.only_included)
    log.info('\ncoverting using `tla2tex.TeX`...')
    log.info('input file: {f}'.format(f=fin))
    log.info('output file: {f}'.format(f=fout))
    return fin, fout, clean, fnames


def _split_included_file_names(only_included):
    # `\includeonly` absent from document ?
    if only_included == 'undefined':
        only_included = None
    if only_included is None:
        return None
    # A trailing comma as in `\includeonly{./tex/foo.tex,}`
    # causes the empty string to be included by `str.split`.
    paths = [p for p in only_included.split(',') if p != '']
    fnames = [os.path.split(p)[1] for p in paths]
    return fnames


def _is_unchanged(fin, fout, old):
    """Return `True` if environment didn't change."""
    # assertions about input file
    assert os.path.isfile(fin), fin
    _, ext = os.path.splitext(fin)
    assert ext == '.tla', ext
    # unchanged ?
    if (  # skip if output exists and new input matches old input
            os.path.isfile(fout) and
            os.path.isfile(old) and
            filecmp.cmp(fin, old)):
        log.info((
            'TLA+ file `{fin}` unchanged. '
            'Returning.').format(fin=fin))
        return True
    return False


def call_tla2tex(s, fname):
    """Dump string `s` to `fname` and call `tla2tex.TeX`."""
    _assert_preamble_exists()
    # dump dummy module
    s = template.format(spec=s)
    with open(fname, 'w') as f:
        f.write(s)
    cmd = [  # shade selected from within the document
        TLAENV,
        # TODO: call tla2tex.TeX directly, using environment variables
        '-latexCommand', 'xelatex',
        fname]
    r = subprocess.call(cmd)
    if r != 0:
        raise RuntimeError('`tla2tex.TeX` exit status != 0')
    # detect LaTeX errors during alignment
    # (`tla2tex.TeX` returns 0 in these cases)
    pdf_file = 'tlatex.pdf'
    if not os.path.isfile(pdf_file):
        raise RuntimeError(
            'Alignment with LaTeX failed, '
            'see `tlatex.log`.')


def _assert_preamble_exists():
    """Raise `FileNotFoundError` if no preamble file."""
    fname = './tex/preamble.tex'
    if os.path.isfile(fname):
        return
    raise FileNotFoundError(
        'File "{fname}" is missing but required. '.format(
            fname=fname))


def _load_tex(fname):
    """Load output of `tla2tex.TeX` from `fname`."""
    begin = '\\begin{tlatex}\n'
    end = '\\end{tlatex}\n'
    with open(fname, 'r') as f:
        lines = f.readlines()
    x = lines.index(begin)
    y = lines.index(end)
    # is last line whitespace ?
    if lines[y - 1].startswith('\\@pvspace{'):
        lines = lines[x:y - 1]
    else:
        print('Second to last line: {s}'.format(s=lines[y - 1]))
        lines = lines[x:y]
    return lines


def _dump_tex(lines, fout):
    """Dump `line` to file name `fout`."""
    s = (
        '\\vspace{' + str(SKIP) + '.0pt}%\n' +
        ''.join(lines) +
        '\\@pvspace{' + str(SKIP) +
            '.0pt}%\n\\end{tlatex}\\noindent%')
    with open(fout, 'w') as f:
        f.write(s)


def _collect_garbage(current_fnames):
    """Delete memoization files that are unused."""
    print('\nCollecting memoization garbage.\n')
    memo, old_memo = _memo_file_names()
    if not os.path.isfile(memo):
        print('File "{memo}" does not exist.'.format(memo=memo))
        return
    if not os.path.isfile(old_memo):
        shutil.move(memo, old_memo)
        print('File "{old_memo}" did not exist'.format(old_memo=old_memo))
        return
    # both memo and old_memo exist
    # remove files with names contained in old_memo but not in memo
    with open(memo, 'rb') as f:
        new_files = pickle.load(f)
    with open(old_memo, 'rb') as f:
        old_files = pickle.load(f)
    included = _filter_by_includeonly(old_files)
    unused = included.difference(new_files)
    _remove_unused_memoization_files(unused)
    # used memoization files
    used = old_files.difference(unused).union(new_files)
    # replace old memo
    os.remove(memo)
    with open(old_memo, 'wb') as f:
        pickle.dump(used, f)
    # new `\includeonly` files
    # restrict attention to `\includeonly` files
    with open(MEMO_INCLUDEONLY, 'wb') as f:
        pickle.dump(current_fnames, f)


def _filter_by_includeonly(old_files):
    """Return memo files that correspond to included LaTeX files."""
    if not os.path.isfile(MEMO_INCLUDEONLY):
        return old_files
    with open(MEMO_INCLUDEONLY, 'rb') as f:
        fnames = pickle.load(f)
    if fnames is None:
        return old_files
    assert '' not in fnames, fnames
    t = tuple(fnames)
    included = set()
    for path in old_files:
        _, fname = os.path.split(path)
        if fname.startswith(t):
            included.add(path)
    return included


def _remove_unused_memoization_files(unused):
    """Remove file in container `unused`."""
    if not unused:
        print('No garbage files to remove.')
        return
    extensions = {'.tla', '.tex'}
    for fname in unused:
        print('deleting unused file "{fname}"'.format(fname=fname))
        head, tail = os.path.split(fname)
        assert head == CACHE_DIR, (fname, CACHE_DIR)
        _, ext = os.path.splitext(tail)
        assert ext in extensions, (fname, ext)
        os.remove(fname)


def _memo_file_names():
    """Return names of memo and old memo pickle files."""
    memo = os.path.join(CACHE_DIR, MEMO_FILE)
    old_memo = os.path.join(CACHE_DIR, OLD_MEMO_FILE)
    return memo, old_memo


if __name__ == '__main__':
    main()
