import pytest

from ocder.ocder import check_content

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
    '''(
        1, 2
    ), {
        3: 4
    }''',
    '''(
        1, 2
    ), {
        3: 4,
    },''',
)]


@pytest.mark.parametrize(['input_node', 'expected'], bad_nodes)
def test_bad_node(input_node, expected):
    valid, fixed_source = check_content(input_node, True)
    assert not valid
    assert fixed_source == expected


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
        },''',
    ),
]


@pytest.mark.parametrize(['input_node'], good_nodes)
def test_good_node(input_node):
    assert check_content(input_node, True)[0]
