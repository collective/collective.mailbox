from setuptools import setup, find_packages
import os

version = '1.1.3.dev0'

long_description = (
    open('README.txt').read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open('CONTRIBUTORS.txt').read()
    + '\n' +
    open('CHANGES.txt').read()
    + '\n')

setup(name='collective.mailbox',
      version=version,
      description="A MailHost that stores outgoing mail.",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Framework :: Plone :: 4.2",
        ],
      keywords='mail plone',
      author='Lennart Regebro',
      author_email='regebro@gmail.com',
      url='https://github.com/collective/collective.mailbox',
      license='CC-0',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.api',
      ],
      extras_require={'test': ['plone.app.testing', 'Products.PrintingMailHost']},
      entry_points="""
      # -*- Entry points: -*-
  	  [z3c.autoinclude.plugin]
  	  target = plone
      """,
      )
