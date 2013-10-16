from distutils.core import setup

def _install_requires():
    return [
        'Django==1.5.0',
        'django-gubbins==1.1.2'
    ]

setup(
    name='prospector-test-2',
    version='0.0.1',
    install_requires=_install_requires()
)