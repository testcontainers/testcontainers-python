import os

# Automatically determine the version to push to pypi
github_ref = os.environ.get('GITHUB_REF', '')
prefix = 'refs/tags/v'
if github_ref.startswith(prefix):
    version = github_ref[len(prefix):]
    with open('VERSION', 'w') as fp:
        fp.write(version)
    print(f'Wrote version {version} to VERSION file.')
else:
    print(f'Could not identify version in {github_ref}.')
