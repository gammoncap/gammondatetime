from setuptools import setup

setup(
    name='gammondatetime',
    version='1.0',
    packages=['gammon_datetime'],
    install_requires=[
        'python-dateutil==2.8.2',
        'pytz==2021.1',
        'numpy==1.21.0'
      ],
    url='https://github.com/gammoncap/gammondatetime',
    license='MIT',
    author='Larry Richards',
    author_email='lrichards@gammoncap.com',
    description='a time zone aware general purpose datetime object'
)
