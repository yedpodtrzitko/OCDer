from __future__ import absolute_import, print_function

import sys

from ocder.ocder import check_target


def run():
    try:
        target = sys.argv[1]
    except IndexError:
        print('target not specified')
        sys.exit(-1)

    check_target(target, rewrite=True)


if __name__ == '__main__':
    run()
