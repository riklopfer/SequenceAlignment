from distutils.core import setup

setup(name='YASA',
      version='0.1.9',
      description='Sequence aligners written in python',
      author='Russell Klopfer',
      author_email='russell@klopfer.us',
      url='https://github.com/riklopfer/YASA',
      packages=['yasa'],
      install_requires=[
        'repoze.lru'
      ]
      )
