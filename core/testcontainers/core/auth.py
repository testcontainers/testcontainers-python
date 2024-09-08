import base64 as base64
import json as json
from collections import namedtuple
from logging import warning
from typing import Any, Optional

DockerAuthInfo = namedtuple("DockerAuthInfo", ["registry", "username", "password"])

_AUTH_WARNINGS = {
    "credHelpers": "DOCKER_AUTH_CONFIG is experimental, credHelpers not supported yet",
    "credsStore": "DOCKER_AUTH_CONFIG is experimental, credsStore not supported yet",
}


def process_docker_auth_config_encoded(auth_config_dict: dict[str, dict[str, dict[str, Any]]]) -> list[DockerAuthInfo]:
    """
    Process the auths config.

    Example:
    {
        "auths": {
            "https://index.docker.io/v1/": {
                "auth": "dXNlcm5hbWU6cGFzc3dvcmQ="
            }
        }
    }

    Returns a list of DockerAuthInfo objects.
    """
    auth_info: list[DockerAuthInfo] = []

    auths = auth_config_dict.get("auths")
    if not auths:
        raise KeyError("No auths found in the docker auth config")

    for registry, auth in auths.items():
        auth_str = str(auth.get("auth"))
        auth_str = base64.b64decode(auth_str).decode("utf-8")
        username, password = auth_str.split(":")
        auth_info.append(DockerAuthInfo(registry, username, password))

    return auth_info


def process_docker_auth_config_cred_helpers(auth_config_dict: dict[str, Any]) -> None:
    """
    Process the credHelpers config.

    Example:
    {
        "credHelpers": {
            "<aws_account_id>.dkr.ecr.<region>.amazonaws.com": "ecr-login"
        }
    }

    This is not supported yet.
    """
    if "credHelpers" in _AUTH_WARNINGS:
        warning(_AUTH_WARNINGS.pop("credHelpers"))


def process_docker_auth_config_store(auth_config_dict: dict[str, Any]) -> None:
    """
    Process the credsStore config.

    Example:
    {
        "credsStore": "ecr-login"
    }

    This is not supported yet.
    """
    if "credsStore" in _AUTH_WARNINGS:
        warning(_AUTH_WARNINGS.pop("credsStore"))


def parse_docker_auth_config(auth_config: str) -> Optional[list[DockerAuthInfo]]:
    """Parse the docker auth config from a string and handle the different formats."""
    try:
        auth_config_dict: dict[str, Any] = json.loads(auth_config)
        if "credHelpers" in auth_config:
            process_docker_auth_config_cred_helpers(auth_config_dict)
        if "credsStore" in auth_config:
            process_docker_auth_config_store(auth_config_dict)
        if "auths" in auth_config:
            return process_docker_auth_config_encoded(auth_config_dict)

    except (json.JSONDecodeError, KeyError, ValueError) as exp:
        raise ValueError("Could not parse docker auth config") from exp

    return None
