import ast
import token

from asttokens import asttokens, util
import os


def check_target(pth, rewrite=False):
    if os.path.isdir(pth):
        check_dir(pth, rewrite=rewrite)
    elif os.path.isfile(pth):
        check_file(pth, rewrite=rewrite)
    else:
        print('unknown target: {}'.format(pth))


def check_dir(pth, rewrite):
    for root, dirs, files in os.walk(pth):
        for dir_ in dirs:
            check_dir(os.path.join(root, dir_), rewrite=rewrite)
        for file in files:
            check_file(os.path.join(root, file), rewrite=rewrite, complain=False)


def check_file(pth, rewrite, complain=True):
    if not pth.endswith('.py'):
        if complain:
            print('{} is not .py file'.format(pth))
        return

    try:
        ocd_check(pth, rewrite)
    except SyntaxError:
        print('skipping {}'.format(pth))


def ocd_check(pth, rewrite=False):
    def note(node):
        print('{}, line {}\n{}\n'.format(pth, node.lineno, atok.get_text(node)))

    with open(pth, 'rb') as f:
        source_text = ''.join(f.readlines())

    file_valid = True
    atok = asttokens.ASTTokens(source_text, parse=True)
    for node in ast.walk(atok._tree):
        if isinstance(node, (ast.Dict, ast.List, ast.Tuple, ast.Set)):
            tokens = list(atok.get_tokens(node, include_extra=True))[::-1]
            valid, changes = is_node_ok(tokens, rewrite)
            if not valid:
                file_valid = False
                if not rewrite:
                    note(node)
                else:
                    for changeset in changes:
                        util.replace(source_text, changeset)

    if rewrite and not file_valid:
        with open('{}2'.format(pth), 'wb') as f:
            f.write(source_text)


def is_node_ok(tokens, rewrite=False):
    """
    - walk nodes in reverse order until a last valid element is found
    - if comma was found in the meantime, it's ok
    """
    #                    util.replace

    index = 1
    valid = False
    multiline = False
    changes = []

    while True:
        pointed = tokens[index]

        # newline or move one token further
        if pointed.type == 54 and '\n' in pointed.string:
            multiline = True
            index += 1
            continue

        # comment, move one token further
        if pointed.type == token.N_TOKENS and pointed.string.startswith('#'):
            index += 1
            continue

        if pointed.type == token.OP and pointed.string == ',':
            valid = True
            break

        if not valid and multiline and rewrite:
            changes.append(
                [pointed.startpos, pointed.endpos, '{},'.format(pointed.string)]
            )

        break

    if not multiline:
        return True, changes
    return valid, changes
