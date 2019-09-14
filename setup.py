from setuptools import setup

setup(
    name='dymm_api',
    packages=['dymm_api'],
    include_package_data=True,
    install_requires=[
        'flask',
        'blinker',
        'requests',
        'Flask-WTF',
        'Flask-SQLAlchemy',
        'psycopg2-binary',
        'pytz',
        'jsonschema',
        'Flask-Bcrypt',
        'Flask-JWT-Extended',
        'Flask-Mail',
        'sqlacodegen'
    ]
)
