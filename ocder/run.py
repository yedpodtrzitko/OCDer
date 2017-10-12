from __future__ import absolute_import, print_function

import click

from ocder.ocder import check_target


@click.command()
@click.option('--jobs', default=1, help='Number of parallel jobs.')
@click.option('--fix', is_flag=True, help='Save fixes into checked files.')
@click.option('--verbose', is_flag=True, help='Be more verbose about things.')
@click.argument('target')
def run(jobs, fix, target, verbose):
    check_target(target, fix, jobs, verbose)


if __name__ == '__main__':
    run()
