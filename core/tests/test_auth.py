import json
import pytest

from testcontainers.core.auth import parse_docker_auth_config, DockerAuthInfo


def test_parse_docker_auth_config_encoded():
    auth_config_json = '{"auths":{"https://index.docker.io/v1/":{"auth":"dXNlcm5hbWU6cGFzc3dvcmQ="}}}'
    auth_info = parse_docker_auth_config(auth_config_json)
    assert len(auth_info) == 1
    assert auth_info[0] == DockerAuthInfo(
        registry="https://index.docker.io/v1/",
        username="username",
        password="password",
    )


def test_parse_docker_auth_config_cred_helpers():
    auth_dict = {"credHelpers": {"<aws_account_id>.dkr.ecr.<region>.amazonaws.com": "ecr-login"}}
    auth_config_json = json.dumps(auth_dict)
    assert parse_docker_auth_config(auth_config_json) is None


def test_parse_docker_auth_config_store():
    auth_dict = {"credsStore": "ecr-login"}
    auth_config_json = json.dumps(auth_dict)
    assert parse_docker_auth_config(auth_config_json) is None


def test_parse_docker_auth_config_encoded_multiple():
    auth_dict = {
        "auths": {
            "localhost:5000": {"auth": "dXNlcjE6cGFzczE=="},
            "https://example.com": {"auth": "dXNlcl9uZXc6cGFzc19uZXc=="},
            "example2.com": {"auth": "YWJjOjEyMw==="},
        }
    }
    auth_config_json = json.dumps(auth_dict)
    auth_info = parse_docker_auth_config(auth_config_json)
    assert len(auth_info) == 3
    assert auth_info[0] == DockerAuthInfo(
        registry="localhost:5000",
        username="user1",
        password="pass1",
    )
    assert auth_info[1] == DockerAuthInfo(
        registry="https://example.com",
        username="user_new",
        password="pass_new",
    )
    assert auth_info[2] == DockerAuthInfo(
        registry="example2.com",
        username="abc",
        password="123",
    )


def test_parse_docker_auth_config_unknown():
    auth_config_str = '{"key": "value"}'
    assert parse_docker_auth_config(auth_config_str) is None


def test_parse_docker_auth_config_error():
    auth_config_str = "bad//string"
    with pytest.raises(ValueError):
        parse_docker_auth_config(auth_config_str)
