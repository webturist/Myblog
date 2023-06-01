from setuptools import setup, find_packages

setup(
    name='Myblog',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'BareNecessities==0.2.8',
        'blinker==1.5',
        'click==8.1.3',
        'colorama==0.4.6',
        'Flask-Login==0.6.2',
        'Flask-Mail==0.9.1',
        'Flask==2.2.3',
        'greenlet==2.0.2',
        'importlib-metadata==6.1.0',
        'itsdangerous==2.1.2',
        'Jinja2==3.1.2',
        'Mail==2.1.0',
        'MarkupSafe==2.1.2',
        'pip==23.0.1',
        'PyJWT==2.6.0',
        'setuptools==67.6.0',
        'typing-extensions==4.5.0',
        'Werkzeug==2.2.3',
        'wheel==0.38.4',
        'zipp==3.15.0'
    ], )
