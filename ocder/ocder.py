from __future__ import print_function

import logging
import ast
import codecs
from functools import partial
import token

from asttokens import asttokens, util
import os

from multiprocessing import Pool

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.WARNING)

import signal

log = logging.getLogger(__name__)


def initializer():
    """Ignore CTRL+C in the worker process -> working Ctrl+C"""
    signal.signal(signal.SIGINT, signal.SIG_IGN)


def check_target(pth, fix=False, jobs=1, verbose=False):
    if verbose:
        log.setLevel(logging.INFO)

    log.info('collecting files')
    targets = collect_targets(pth)

    log.info('starting check; workers: {}'.format(jobs))
    pool = Pool(jobs, initializer=initializer)
    pool.map_async(partial(check_file, fix), targets).get(9999999)


def collect_targets(pth):
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
    try:
        ocd_check(pth, fix)
    except Exception as e:
        log.error('skipping {}\n - {}'.format(pth, e))


def ocd_check(pth, fix=False):
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
    file_valid = True
    atok = asttokens.ASTTokens(source_text, parse=True)
    changeset = set()

    for node in ast.walk(atok._tree):
        if isinstance(node, (ast.Dict, ast.List, ast.Tuple, ast.Set)):
            tokens = list(atok.get_tokens(node, include_extra=True))[::-1]
            file_valid, changes = check_token(tokens, fix)
            if not fix and not file_valid:
                log.error('OCD node:\n{}, line {}\n{}\n'.format(pth, node.lineno, atok.get_text(node)))
            elif fix and not file_valid:
                log.info('fixing {}'.format(pth))
                changeset.update(changes)

    if fix and not file_valid:
        source_text = util.replace(source_text, changeset)
        with codecs.open('%s' % pth, 'wb', encoding='utf-8') as f:
            f.write(header + source_text)


def check_token(tokens, fix=False):
    """
    - walk nodes in reverse order until
    - if comma is found in the meantime until
    """
    index = 1
    valid = False
    multiline = False
    changes = []

    last_index = len(tokens) - 1

    while True:
        pointed = tokens[index]
        # newline, move one token further
        if pointed.type == 54 and '\n' in pointed.string:
            multiline = True
            index += 1
            continue

        # comment, move one token further
        if pointed.type == token.N_TOKENS and pointed.string.startswith('#'):
            index += 1
            continue

        # we got comma before anything else, valid
        if pointed.type == token.OP and pointed.string == ',':
            valid = True
            break

        # it's empty, dont do anything
        if index == last_index:
            valid = True
            break

        if not valid and multiline and fix:
            changes.append(
                (pointed.endpos, pointed.endpos, ','),
            )
            break

        break

    if not multiline:
        return True, []
    return valid, changes
