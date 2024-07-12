import base64 as base64
import json as json
from collections import namedtuple
from logging import warning
from typing import Optional

DockerAuthInfo = namedtuple("DockerAuthInfo", ["registry", "username", "password"])

_AUTH_WARNINGS = {
    "credHelpers": "DOCKER_AUTH_CONFIG is experimental, credHelpers not supported yet",
    "credsStore": "DOCKER_AUTH_CONFIG is experimental, credsStore not supported yet",
}


def parse_docker_auth_config_encoded(auth_config_dict: dict) -> list[DockerAuthInfo]:
    """
    Parse the docker auth config from a string.

    Example:
    {
        "auths": {
            "https://index.docker.io/v1/": {
                "auth": "dXNlcm5hbWU6cGFzc3dvcmQ="
            }
        }
    }
    """
    auth_info: list[DockerAuthInfo] = []

    auths = auth_config_dict.get("auths")
    for registry, auth in auths.items():
        auth_str = auth.get("auth")
        auth_str = base64.b64decode(auth_str).decode("utf-8")
        username, password = auth_str.split(":")
        auth_info.append(DockerAuthInfo(registry, username, password))

    return auth_info


def parse_docker_auth_config_cred_helpers(auth_config_dict: dict) -> None:
    """
    Parse the docker auth config from a string.

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


def parse_docker_auth_config_store(auth_config_dict: dict) -> None:
    """
    Parse the docker auth config from a string.

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
        auth_config_dict: dict = json.loads(auth_config)
        if "auths" in auth_config:
            return parse_docker_auth_config_encoded(auth_config_dict)
        elif "credHelpers" in auth_config:
            parse_docker_auth_config_cred_helpers(auth_config_dict)
        elif "credsStore" in auth_config:
            parse_docker_auth_config_store(auth_config_dict)

    except (json.JSONDecodeError, KeyError, ValueError) as exp:
        raise ValueError("Could not parse docker auth config") from exp

    return None
