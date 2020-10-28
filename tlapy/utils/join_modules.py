#!/usr/bin/env python
"""Concatenate PDF files of TLA+ modules."""
# Copyright 2017 by California Institute of Technology
# All rights reserved. Licensed under 3-clause BSD.
#
import argparse
import os
import shutil
import subprocess

from PyPDF2 import PdfFileReader


START = r'''
\documentclass[letter]{article}
\usepackage{pdfpages}
\usepackage{hyperref}
\usepackage{verbatim}
\usepackage{tocloft}
\usepackage{tlamath}
\renewcommand\cftsecdotsep{\cftdotsep}
%\pagenumbering{gobble}
\begin{document}
'''
MIDDLE = r'''
\maketitle
'''
MIDDLE_2 = r'''
\tableofcontents
\newpage
\verbatiminput{./LICENSE}
\newpage
'''
END = r'''
\end{document}
'''
MERGED_FILE = 'merged_tla_modules.pdf'
AUXDIR = '__tlacache__/.aux'
LICENSE = 'LICENSE'
DEFAULT_TITLE = r'TLA\textsuperscript{+} modules'


def join_modules():
    paths, author_name, title_str, date_str, abstract = parse_args()
    lines = list()
    for path in paths:
        stem, fname = os.path.split(path)
        assert not stem, stem  # relative path
        name, ext = os.path.splitext(fname)
        assert ext == '.pdf', path
        # front matter
        title = name.replace('_', r'\_')
        pdf = PdfFileReader(open(path, 'rb'))
        page_count = pdf.getNumPages()
        if page_count > 1:
            include_rest = '\includepdf[pages=2-]{' + fname + '}'
        else:
            include_rest = ''
        more_lines = [
            '\includepdf[pages=1,pagecommand={\phantomsection ' +
            '\\addcontentsline{toc}{section}{' + title +
            '} }]{' + fname + '}',
            include_rest]
        lines.extend(more_lines)
        # copy file to aux dir
        target = os.path.join(AUXDIR, fname)
        print(target)
        shutil.copy(path, target)
    if os.path.isfile(LICENSE):
        target = os.path.join(AUXDIR, LICENSE)
        shutil.copy(LICENSE, target)
    if os.path.isfile(abstract):
        target = os.path.join(AUXDIR, abstract)
        shutil.copy(abstract, target)
    if title_str is None:
        title_str = DEFAULT_TITLE
    title = r'\title{' + title_str + '}'
    if author_name is None:
        author = ''
    else:
        author = r'\author{' + author_name + '}\n'
    if date_str is None:
        date = ''
    else:
        date = r'\date{' + date_str + '}\n'
    if abstract is None:
        abstract = ''
    else:
        abstract = (r'\begin{abstract}\input{' + abstract +
            r'} \end{abstract}')
    latex = (
        START + title + date + author + MIDDLE + abstract +
        MIDDLE_2 + '\n'.join(lines) + END)
    # typeset using XeLaTeX
    name, ext = os.path.splitext(MERGED_FILE)
    assert ext == '.pdf', MERGED_FILE
    fname = name + '.tex'
    path = os.path.join(AUXDIR, fname)
    with open(path, 'w') as f:
        f.write(latex)
    cmd = ['xelatex', '--interaction=nonstopmode', fname]
    subprocess.call(cmd, cwd=AUXDIR)
    # copy merged PDF to current dir
    path = os.path.join(AUXDIR, MERGED_FILE)  # merged PDF
    shutil.copy(path, MERGED_FILE)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('files', nargs='+',
                   help='file names')
    p.add_argument('-a', '--author', type=str,
                   help='Document author')
    p.add_argument('--title', type=str,
                   help='Document title')
    p.add_argument('--date', type=str,
                   help='Document date')
    p.add_argument('--abstract', type=str,
                   help='Document abstract')
    args = p.parse_args()
    return (
        args.files, args.author, args.title,
        args.date, args.abstract)


if __name__ == '__main__':
    join_modules()
