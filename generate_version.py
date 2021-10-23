import os

# Automatically determine the version to push to pypi
github_ref = os.environ.get('GITHUB_REF', '')
prefix = 'refs/tags/v'
if github_ref.startswith(prefix):
    version = github_ref[len(prefix):]
    with open('VERSION', 'w') as fp:
        fp.write(version)
    print('Wrote version %s to VERSION file.' % version)
else:
    raise ValueError('Could not identify version in %s.' % github_ref)
