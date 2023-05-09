import argparse
import io
import pathlib
import requests
import shutil
import tempfile
import zipfile


def __main__() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--owner", default="testcontainers")
    parser.add_argument("--repo", default="testcontainers-python")
    parser.add_argument("--run", help="GitHub Action run id")
    parser.add_argument("--pr", help="GitHub PR number")
    parser.add_argument("--branch", default="main")
    parser.add_argument("--token", help="GitHub autentication token")
    args = parser.parse_args()

    # Get an access token.
    if args.token:
        token = args.token
    elif (path := pathlib.Path(".github-token")).is_file():
        token = path.read_text().strip()
    else:
        token = input("We need a GitHub access token to fetch the requirements. Please visit "
                      "https://github.com/settings/tokens/new, create a token with `public_repo` "
                      "scope, and paste it here: ").strip()
        cache = input("Do you want to cache the token in a `.github-token` file [Ny]? ")
        if cache.lower().startswith("y"):
            path.write_text(token)

    headers = {
        "Authorization": f"Bearer {token}",
    }
    base_url = f"https://api.github.com/repos/{args.owner}/{args.repo}"

    if args.run:  # Run id was specified.
        run = args.run
    elif args.pr:  # PR was specified, let's get the most recent run id.
        print(f"Fetching most recent commit for PR #{args.pr}.")
        response = requests.get(f"{base_url}/pulls/{args.pr}", headers=headers)
        response.raise_for_status()
        response = response.json()
        head_sha = response["head"]["sha"]
    else:  # Nothing was specified, let's get the most recent run id on the main branch.
        print(f"Fetching most recent commit for branch `{args.branch}`.")
        response = requests.get(f"{base_url}/branches/{args.branch}", headers=headers)
        response.raise_for_status()
        response = response.json()
        head_sha = response["commit"]["sha"]

    # List all completed runs and find the one that generated the requirements.
    response = requests.get(f"{base_url}/actions/runs", headers=headers, params={
        "head_sha": head_sha,
        "status": "success",
    })
    response.raise_for_status()
    response = response.json()

    # Get the requirements run.
    runs = [run for run in response["workflow_runs"] if
            run["path"].endswith("requirements.yml")]
    if not runs:
        raise RuntimeError("Could not find a workflow. Has the GitHub Action run completed? If you"
                           "are a first-time contributor, a contributor has to approve your changes"
                           "before Actions can run.")
    if len(runs) != 1:
        raise RuntimeError(f"Could not identify unique workflow run: {runs}")
    run = runs[0]["id"]

    # Get all the artifacts.
    print(f"fetching artifacts for run {run} ...")
    url = f"{base_url}/actions/runs/{run}/artifacts"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    response = response.json()
    artifacts = response["artifacts"]
    print(f"Discovered {len(artifacts)} artifacts.")

    # Get the content for each artifact and save it.
    for artifact in artifacts:
        name: str = artifact["name"]
        name = name.removeprefix("requirements-")
        print(f"Fetching artifact {name} ...")
        response = requests.get(artifact["archive_download_url"], headers=headers)
        response.raise_for_status()
        with zipfile.ZipFile(io.BytesIO(response.content)) as zip, \
                tempfile.TemporaryDirectory() as tempdir:
            zip.extract("requirements.txt", tempdir)
            shutil.move(pathlib.Path(tempdir) / "requirements.txt",
                        pathlib.Path("requirements") / name)

    print("Done.")


if __name__ == "__main__":
    __main__()
