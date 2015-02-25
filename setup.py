from setuptools import setup, find_packages  # Always prefer setuptools over distutils
from codecs import open  # To use a consistent encoding

from version import __version__ as version

setup(
	name = "blockspring",
	version = version,
	description='Blockspring api wrapper',
	long_description='\n'.join(
            [
                open('README.rst', 'rb').read().decode('utf-8'),
                open('DESCRIPTION.rst', 'rb').read().decode('utf-8'),
            ]
        ),
	# The project's main homepage
	url='https://www.blockspring.com',

	# Author details
	author='Blockspring',
	author_email='paul@blockspring.com',

	# Choose your license
	license='MIT',

	# See https://pypi.python.org/pypi?%3Aaction=list_classifiers
	classifiers=[
	    # How mature is this project? Common values are
	    #   3 - Alpha
	    #   4 - Beta
	    #   5 - Production/Stable
	    'Development Status :: 5 - Production/Stable',

	    # Indicate who your project is intended for
	    'Intended Audience :: Developers',
	    'Topic :: Software Development :: Build Tools',

	    # Pick your license as you wish (should match "license" above)
	    'License :: OSI Approved :: MIT License',

	    # Specify the Python versions you support here. In particular, ensure
	    # that you indicate whether you support Python 2, Python 3 or both.
	    'Programming Language :: Python :: 2',
	    'Programming Language :: Python :: 2.6',
	    'Programming Language :: Python :: 2.7',
	    'Programming Language :: Python :: 3',
	    'Programming Language :: Python :: 3.2',
	    'Programming Language :: Python :: 3.3',
	    'Programming Language :: Python :: 3.4',
	],

	# What does your project relate to?
	keywords='blockspring function cloud api service library development',

	packages=find_packages(),

	install_requires=['requests']

)
