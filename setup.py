from setuptools import setup

version = '0.1dev'

long_description = '\n\n'.join([
    open('README.rst').read(),
    open('CREDITS.rst').read(),
    open('CHANGES.rst').read(),
    ])

install_requires = [
    'pika',
    'setuptools',
    ],

tests_require = [
    'coverage',
    'nose',
    ]

setup(name='ddsc-logging',
      version=version,
      description="DDSC library for centralized logging of distributed apps",
      long_description=long_description,
      # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[],
      keywords=[],
      author='Carsten Byrman',
      author_email='carsten.byrman@nelen-schuurmans.nl',
      url='',
      license='GPL',
      packages=['ddsc_logging'],
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      tests_require=tests_require,
      extras_require={'test': tests_require},
      entry_points={
          'console_scripts': [
          ]},
      )
