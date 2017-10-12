from setuptools import find_packages, setup

with open('requirements.txt') as f:
    install_requires = [line for line in f if line and line[0] not in '#-']

with open('test-requirements.txt') as f:
    tests_require = [line for line in f if line and line[0] not in '#-']

setup(
    name='ocder',
    version='0.1.0',
    url='https://github.com/yedpodtrzitko/ocder',
    author='yedpodtrzitko',
    author_email='yed@vanyli.net',
    packages=find_packages(),
    install_requires=install_requires,
    tests_require=tests_require,
    entry_points={
        'console_scripts': [
            'ocder=ocder.run:run'
        ]
    }
)
