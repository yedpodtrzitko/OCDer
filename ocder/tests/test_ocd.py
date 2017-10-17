import ast

from asttokens import asttokens
import pytest

from ocder.ocder import check_node, fix_source

bad_nodes = [(
    '''{
        'complain': 2
    }''',
    '''{
        'complain': 2,
    }'''
), (
    '''{
        'complain': 1
    
    }''',
    '''{
        'complain': 1,
    
    }''',
), (
    '''{
        'complain': 3  # comment
    }''',
    '''{
        'complain': 3,  # comment
    }''',
), (
    '''{
        'complain': 3
        # comment
    }''',
    '''{
        'complain': 3,
        # comment
    }''',
), (
    '''{
        'complain': {}
    }''',
    '''{
        'complain': {},
    }''',
), (
    '''(
        'complain',
        'complain'
    )''',
    '''(
        'complain',
        'complain',
    )''',
), (
    '''{
        1, 2
    }, {
        3: 4
    }''',
    '''{
        1, 2
    }, {
        3: 4,
    }''',
)]



@pytest.mark.parametrize(['input_node', 'expected'], bad_nodes)
def test_bad_node(input_node, expected):
    atok = asttokens.ASTTokens(input_node, parse=True)
    node = atok._tree
    tokens = list(atok.get_tokens(node, include_extra=True))[::-1]
    changeset = set()
    assert not check_node(tokens, changeset, node.__class__)
    assert fix_source(input_node, changeset) == expected


good_nodes = [
    (
        '''{
            'ok': 1,
    
        }''',
    ), (
        '''{
        'ok': 2,  # commment

        }''',
    ), (
        '''{
        'ok': 3,
        # commment
        }''',
    ), (
        '''{'ok': 5}''',
    ), (
        '''('ok',)''',
    ), (
        '''{
        # valid
        }''',
    ), (
        '''{

        }''',
    ), (
        '''(
            1, 2
        ), {
            3: 4,
        }''',
    ),
]


@pytest.mark.parametrize(['input_node'], good_nodes)
def test_good_node(input_node):
    atok = asttokens.ASTTokens(input_node, parse=True)
    node = atok._tree
    tokens = list(atok.get_tokens(node, include_extra=True))[::-1]
    changeset = set()
    assert check_node(tokens, changeset, node.__class__)
    assert not changeset
