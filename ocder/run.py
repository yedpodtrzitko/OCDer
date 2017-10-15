#!/usr/bin/env python
from __future__ import absolute_import, print_function

import click

from ocder.ocder import check_target


@click.command()
@click.option('-j', '--jobs', default=1, help='Number of parallel jobs.')
@click.option('-f', '--fix', is_flag=True, help='Save fixes into checked files.')
@click.option('-v', '--verbose', count=True, help='Set verbosity level')
@click.argument('target')
def run(jobs, fix, target, verbose):
    """OCDer entry point."""
    check_target(target, fix, jobs, verbose)


if __name__ == '__main__':
    run()
