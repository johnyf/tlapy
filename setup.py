"""Installation script."""
from setuptools import setup


name = 'tlapy'
description = (
    'Python tools for working with TLA+ specifications.')
README = 'README.md'
long_description = open(README).read()
url = 'https://github.com/johnyf/{name}'.format(name=name)
VERSION_FILE = '{name}/_version.py'.format(name=name)
MAJOR = 0
MINOR = 0
MICRO = 1
version = '{major}.{minor}.{micro}'.format(
    major=MAJOR, minor=MINOR, micro=MICRO)
s = (
    '# This file was generated from setup.py\n'
    "version = '{version}'\n").format(version=version)
install_requires = [
    'networkx >= 2.0',
    'PyPDF2 >= 1.26.0',  # `tlapy.utils.join_modules`
    'tla >= 0.0.1',  # `tlapy.proof_graph`
    ]
tests_require = ['nose']
classifiers = [
    'Development Status :: 2 - Pre-Alpha',
    'Intended Audience :: Developers',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Topic :: Scientific/Engineering',
    'Topic :: Utilities',
    ]
keywords = [
    'TLA+', 'TLA', 'temporal logic of actions',
    'formal', 'specification',
    'utilities', 'LaTeX', 'proof renumbering',
    'plotting', 'proofs',
    ]


def run_setup():
    with open(VERSION_FILE, 'w') as f:
        f.write(s)
    setup(
        name=name,
        version=version,
        description=description,
        long_description=long_description,
        long_description_content_type='text/markdown',
        author='Ioannis Filippidis',
        author_email='jfilippidis@gmail.com',
        url=url,
        license='BSD',
        install_requires=install_requires,
        tests_require=tests_require,
        packages=[name],
        package_dir={name: name},
        classifiers=classifiers,
        keywords=keywords)


if __name__ == '__main__':
    run_setup()
