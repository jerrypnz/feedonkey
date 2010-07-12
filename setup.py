from distutils.core import setup

setup(
    name='feedonkey',
    version='0.1',
    description='',
    author='Jerry Peng',
    author_email='pr2jerry@gmail.com',
    url='http://code.google.com/p/feedonkey/',
    scripts=['feedonkey-daemon', 'feedonkey-add'],
    packages=['feedonkey'],
    requires=['feedparser(>=4.1)'],
    license='GNU GPL v3',
    platforms='linux'
)


