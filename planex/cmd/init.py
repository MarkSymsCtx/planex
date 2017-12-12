"""
Creates or regenerates a Makefile with special planex-init comments
"""
from __future__ import print_function

import argparse
import logging
import os
import sys

import argcomplete
from pkg_resources import resource_filename

from planex.cmd.args import common_base_parser
from planex.util import setup_sigint_handler


def print_rules_path():
    """
    Print the path to Makefile.rules, which is installed in the Python
    package directory.
    """
    print(resource_filename("planex", "Makefile.rules"))


def create_makefile():
    """ Checks if a Makefile exists with special planex-init comments in it.
    If not, it creates or regenerates the Makefile while preserving its
    existing contents.
    """
    name = "Makefile"

    defaults = [".PHONY: default\n",
                "default: rpms\n",
                "DIST?=.fc21\n",
                "# FETCH_EXTRA_FLAGS=--no-package-name-check\n",
                "# DEPEND_EXTRA_FLAGS=--no-package-name-check\n"]
    firstline = "# Start generated by planex-init\n"
    autogen = "include $(shell planex-init --rules)\n"
    endline = "# End generated by planex-init\n"

    if not os.path.exists(name):
        logging.debug("Creating Makefile")
        with open(name, 'w') as makefile:
            for line in defaults:
                makefile.write(line)
            makefile.write(firstline)
            makefile.write(autogen)
            makefile.write(endline)
        return

    with open(name, 'r') as makefile:
        lines = makefile.readlines()

    try:
        start = lines.index(firstline)
        end = lines.index(endline)
        lines = lines[:start + 1] + [autogen] + lines[end:]

    except ValueError:
        logging.error("Couldn't find planex-init stanza in Makefile")

    with open(name, 'w') as makefile:
        makefile.writelines(lines)


def parse_args_or_exit(argv=None):
    """
    Parse command line options
    """
    parser = argparse.ArgumentParser(description='Download package sources',
                                     parents=[common_base_parser()])
    parser.add_argument('--rules', dest="rules",
                        action="store_true", default=False,
                        help="Print the full path to Makefile.rules")
    argcomplete.autocomplete(parser)
    return parser.parse_args(argv)


def main(argv=None):
    """
    Main entry point.
     * If run without arguments, create or update the Makefile in the
       current directory.
     * If run with --rules, return the path to the Makefile.rules file.
    """
    setup_sigint_handler()
    args = parse_args_or_exit(argv)
    logging.basicConfig(format='%(message)s', level=logging.ERROR)

    if args.rules:
        print_rules_path()
        sys.exit(0)

    create_makefile()
