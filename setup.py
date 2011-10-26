from setuptools import setup, find_packages
import sys, os

version = '0.0'

setup(name='tornado-bayes',
      version=version,
      description="",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='bayes',
      author='Mykola Kharechko',
      author_email='crchemist@gmail.com',
      url='',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'tornadotools'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
