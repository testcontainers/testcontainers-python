from distutils.core import setup

setup(
    name='testcontainers',
    packages=['testcontainers'],  # this must be the same as the name above
    version='1.0',
    description='Library provides lightweight, throwaway instances of common databases, Selenium web browsers, or anything else that can run in a Docker containe',
    author='Sergey Pirogov',
    author_email='automationremarks@gmail.com',
    url='https://github.com/SergeyPirogov/testcontainers_python',  # use the URL to the github repo
    download_url='https://github.com/SergeyPirogov/testcontainers_python/tarball/1.0',  # I'll explain this in a second
    keywords=['testing', 'logging', 'docker', 'test automation'],  # arbitrary keywords
    classifiers=[],
    install_requires=['wrapt', 'progressbar2', 'docker-py'],
)
