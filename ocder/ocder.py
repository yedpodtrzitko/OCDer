from __future__ import print_function

import ast
import codecs
import logging
import os
import token
from functools import partial
from multiprocessing import Pool

from asttokens import asttokens, util

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.WARNING)

log = logging.getLogger(__name__)

verbosity = {
    0: logging.WARNING,
    1: logging.INFO,
    2: logging.DEBUG,
}


def check_target(pth, fix=False, jobs=1, verbose=0):
    """
    Main function performing check on chosen path.

    :param pth: target file/directory to check
    :param fix: check-only or fix
    :param jobs: number of workers
    :param verbose: show extra information
    """
    log.setLevel(verbosity.get(min(max(verbose, 0), 2)))

    log.info('collecting files')
    targets = collect_targets(pth)

    log.info('starting check; workers: {}'.format(jobs))
    pool = Pool(jobs)
    # .get(9999999) fixes workers capturing Ctrl+C
    pool.map_async(partial(check_file, fix), targets).get(9999999)


def collect_targets(pth):
    """
    Collect and return all files in chosen path.
    """
    targets = []
    if os.path.isdir(pth):
        for root, dirs, files in os.walk(pth):
            for dir_ in dirs:
                targets += collect_targets(os.path.join(root, dir_))
            for file_ in files:
                if file_.endswith('.py'):
                    targets.append(os.path.join(root, file_))
    elif os.path.isfile(pth):
        if pth.endswith('.py'):
            targets.append(pth)
    else:
        raise ValueError('unknown target: {}'.format(pth))

    return targets


def check_file(fix, pth):
    """
    OCD-check a single file.
    """
    try:
        ocd_check(pth, fix)
    except Exception as e:
        log.error('skipping {}\n - {}'.format(pth, e))


def ocd_check(pth, fix=False):
    """
    Perform OCD-check on a single file.

    File is expected to be utf-8.

    :param pth: filepath to be checked.
    :param fix: if false, file won't be modified, only report the issues.
    """
    log.info('checking {}'.format(pth))
    with codecs.open(pth, encoding='utf-8') as f:
        lines = f.readlines()

    if not lines:
        return

    header = ''
    if '# -*- coding:' in lines[0]:
        header = lines[0]
        lines = lines[1:]

    source_text = u''.join(lines)
    atok = asttokens.ASTTokens(source_text, parse=True)
    changeset = set()

    for node in ast.walk(atok._tree):
        if isinstance(node, (ast.Dict, ast.List, ast.Tuple, ast.Set)):
            tokens = list(atok.get_tokens(node, include_extra=True))[::-1]
            if not check_node(tokens, changeset):
                if not fix:
                    log.error('OCD node:\n{}, line {}\n{}\n'.format(pth, node.lineno, atok.get_text(node)))
                else:
                    log.info('fixing {}'.format(pth))

    print('fix changeset', fix, changeset)
    if fix and changeset:
        source_text = util.replace(source_text, [(change, change, ',') for change in changeset])
        with codecs.open('%s' % pth, 'wb', encoding='utf-8') as f:
            f.write(header + source_text)


def check_node(tokens, changes):
    """
    Check if AST node is properly trailed by comma.
    Only multiline collections are checked.

    Approach:
    - walk tokens in AST node in reversal order
    - if no newline is found, comma not required
    - if no content is found, comma not required
    - if comma isn't found before any content token, comma required

    :param tokens: tokens contained in AST node
    :return: true if node is comma-trailed properly
    """
    index = 0
    valid = False
    multiline = False
    found_content = False

    last_index = len(tokens) - 1

    while True:
        pointed = tokens[index]

        log.debug('pointed node: {}'.format(pointed))

        # first node reached, could be empty
        if index == last_index:
            log.debug('node is very last')
            valid = True
            break

        # newline, move one token further
        if pointed.type == 54 and '\n' in pointed.string:
            log.debug('node is newline')
            multiline = True
            index += 1
            print(11)
            continue

        # comment, move one token further
        if pointed.type == token.N_TOKENS and pointed.string.startswith('#'):
            log.debug('node is comment')
            index += 1
            print(12)
            continue

        # we got comma before anything else, valid
        if pointed.type == token.OP and pointed.string == ',':
            log.debug('node is comma')
            valid = True
            break

        if not valid and multiline:
            log.debug('node is not anything above, error and oout')
            break
        else:
            log.debug('found a node before comma, probably not valid')
            found_content = True
            index += 1
            # we dont know if it's multiline yet
            continue

    if not multiline:
        return True

    valid = not found_content and valid
    if not valid:
        changes.add(tokens[0].endpos)
    return valid
