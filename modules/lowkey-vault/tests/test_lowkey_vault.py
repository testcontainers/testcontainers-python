import base64
import logging
from pathlib import Path

from azure.core.pipeline.transport._requests_basic import RequestsTransport
from azure.keyvault.certificates import CertificateClient, CertificatePolicy
from azure.keyvault.keys import KeyClient, KeyOperation
from azure.keyvault.keys.crypto import CryptographyClient, EncryptResult, DecryptResult, EncryptionAlgorithm
from azure.keyvault.secrets import SecretClient
from cryptography import x509
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePrivateKey
from cryptography.hazmat.primitives.serialization.pkcs12 import load_key_and_certificates

from testcontainers.core.image import DockerImage
from testcontainers.core.container import DockerContainer
from testcontainers.core.network import Network
from testcontainers.core.waiting_utils import wait_for_logs
from testcontainers.lowkeyvault import LowkeyVaultContainer, NetworkType

logger = logging.getLogger(__name__)

DOCKER_FILE_PATH = ".modules/lowkeyvault/tests/external_container_sample"
IMAGE_TAG = "external_container:test"

TEST_DIR = Path(__file__).parent

API_VERSION = "7.6"


def test_docker_run_lowkey_vault_with_secrets():
    with LowkeyVaultContainer() as lowkey_vault_container:
        local_connection_url = lowkey_vault_container.get_connection_url()
        token = lowkey_vault_container.get_token()
        transport = RequestsTransport(connection_verify=False)
        secret_client: SecretClient = SecretClient(
            vault_url=local_connection_url,
            credential=token,
            verify_challenge_resource=False,
            transport=transport,
            api_version=API_VERSION,
        )
        message: str = "a secret message"
        name: str = "test-secret"

        secret_client.set_secret(name=name, value=message)
        actual: str = secret_client.get_secret(name=name).value

        # close the client
        secret_client.close()
        # verify the result
        assert actual == message


def test_docker_run_lowkey_vault_with_keys():
    with LowkeyVaultContainer() as lowkey_vault_container:
        local_connection_url = lowkey_vault_container.get_connection_url()
        token = lowkey_vault_container.get_token()
        secret_message: str = "a secret message"
        key_name: str = "rsa-key-name"
        # test key API to see that the container works
        # ignore SSL errors because we are using a self-signed certificate
        transport_keys = RequestsTransport(connection_verify=False)
        transport_crypto = RequestsTransport(connection_verify=False)
        # create the clients we need
        key_client = KeyClient(
            vault_url=local_connection_url,
            credential=token,
            verify_challenge_resource=False,
            transport=transport_keys,
            api_version=API_VERSION,
        )
        # create a new key
        key_client.create_rsa_key(
            name=key_name,
            size=2048,
            key_operations=[KeyOperation.encrypt, KeyOperation.decrypt, KeyOperation.wrap_key, KeyOperation.unwrap_key],
        )

        crypto_client = CryptographyClient(
            key=key_client.get_key(name=key_name).id,
            credential=token,
            verify_challenge_resource=False,
            transport=transport_crypto,
            api_version=API_VERSION,
        )

        # encode the text
        text_as_bytes: bytes = bytes(secret_message.encode("utf-8"))
        encrypted: EncryptResult = crypto_client.encrypt(
            algorithm=EncryptionAlgorithm.rsa_oaep_256, plaintext=text_as_bytes
        )
        cipher_text: bytes = encrypted.ciphertext

        # decode the cipher text
        decrypted: DecryptResult = crypto_client.decrypt(
            algorithm=EncryptionAlgorithm.rsa_oaep_256, ciphertext=cipher_text
        )
        decrypted_text: str = decrypted.plaintext.decode("utf-8")

        # close the clients
        key_client.close()
        crypto_client.close()
        # verify the result
        assert decrypted_text == secret_message


def test_docker_run_lowkey_vault_with_certificates():
    with LowkeyVaultContainer() as lowkey_vault_container:
        local_connection_url = lowkey_vault_container.get_connection_url()
        token = lowkey_vault_container.get_token()
        # test certificates API to see that the container works
        cert_name: str = "ec-cert-name"
        # ignore SSL errors because we are using a self-signed certificate
        transport_certs = RequestsTransport(connection_verify=False)
        transport_secrets = RequestsTransport(connection_verify=False)
        # create the clients we need
        certificate_client = CertificateClient(
            vault_url=local_connection_url,
            credential=token,
            verify_challenge_resource=False,
            transport=transport_certs,
            api_version=API_VERSION,
        )
        secret_client = SecretClient(
            vault_url=local_connection_url,
            credential=token,
            verify_challenge_resource=False,
            transport=transport_secrets,
            api_version=API_VERSION,
        )

        subject_name: str = "CN=example.com"
        policy: CertificatePolicy = CertificatePolicy(
            issuer_name="Self",
            subject=subject_name,
            key_curve_name="P-256",
            key_type="EC",
            validity_in_months=12,
            content_type="application/x-pkcs12",
        )
        certificate_client.begin_create_certificate(certificate_name=cert_name, policy=policy).wait()

        cert_value = secret_client.get_secret(name=cert_name).value

        # decode base64 secret
        decoded = base64.b64decode(cert_value)
        # open decoded secret as PKCS12 file
        pkcs12 = load_key_and_certificates(decoded, b"")

        # get the components
        ec_key: EllipticCurvePrivateKey = pkcs12[0]
        x509_cert: x509.Certificate = pkcs12[1]

        # close the clients
        secret_client.close()
        certificate_client.close()

        # verify the result
        assert subject_name == x509_cert.subject.rdns[0].rfc4514_string()
        assert "secp256r1" == ec_key.curve.name


def test_docker_run_lowkey_vault_inter_container_communication_with_secrets():
    """
    Tests inter-container communication between a Lowkey Vault container and
    a custom application container within the same Docker network using the
    secrets API.
    """
    with Network() as network:
        with LowkeyVaultContainer(container_alias="lowkey-vault").with_network(network) as lowkey_vault_container:
            network_connection_url = lowkey_vault_container.get_connection_url(network_type=NetworkType.NETWORK)
            imds_endpoint = lowkey_vault_container.get_imds_endpoint(network_type=NetworkType.NETWORK)
            token_url = lowkey_vault_container.get_token_url(network_type=NetworkType.NETWORK)
            with DockerImage(path=TEST_DIR / "samples/network_container", tag=IMAGE_TAG) as image:
                with (
                    DockerContainer(image=str(image))
                    .with_env("CONNECTION_URL", network_connection_url)
                    .with_env("AZURE_POD_IDENTITY_AUTHORITY_HOST", imds_endpoint)
                    .with_env("IMDS_ENDPOINT", imds_endpoint)
                    .with_env("IDENTITY_ENDPOINT", token_url)
                    .with_env("TEST", "secrets")
                    .with_env("SECRET_NAME", "secret-name")
                    .with_env("SECRET_VALUE", "secret-value")
                    .with_network(network)
                    .with_network_aliases("network_container")
                    .with_exposed_ports(80, 80) as container
                ):
                    wait_for_logs(container=container, predicate="Lowkey Vault Container created.")
                # make sure the container was actually created
                assert lowkey_vault_container is not None


def test_docker_run_lowkey_vault_inter_container_communication_with_keys():
    """
    Tests inter-container communication between a Lowkey Vault container and
    a custom application container within the same Docker network using the
    keys API.
    """
    with Network() as network:
        with LowkeyVaultContainer(container_alias="lowkey-vault").with_network(network) as lowkey_vault_container:
            network_connection_url = lowkey_vault_container.get_connection_url(network_type=NetworkType.NETWORK)
            imds_endpoint = lowkey_vault_container.get_imds_endpoint(network_type=NetworkType.NETWORK)
            token_url = lowkey_vault_container.get_token_url(network_type=NetworkType.NETWORK)
            with DockerImage(path=TEST_DIR / "samples/network_container", tag=IMAGE_TAG) as image:
                with (
                    DockerContainer(image=str(image))
                    .with_env("CONNECTION_URL", network_connection_url)
                    .with_env("AZURE_POD_IDENTITY_AUTHORITY_HOST", imds_endpoint)
                    .with_env("IMDS_ENDPOINT", imds_endpoint)
                    .with_env("IDENTITY_ENDPOINT", token_url)
                    .with_env("TEST", "keys")
                    .with_env("KEY_NAME", "rsa-key")
                    .with_env("SECRET_VALUE", "secret-value")
                    .with_network(network)
                    .with_network_aliases("network_container")
                    .with_exposed_ports(80, 80) as container
                ):
                    wait_for_logs(container=container, predicate="Lowkey Vault Container created.")
                # make sure the container was actually created
                assert lowkey_vault_container is not None


def test_docker_run_lowkey_vault_inter_container_communication_with_certs():
    """
    Tests inter-container communication between a Lowkey Vault container and
    a custom application container within the same Docker network using the
    certificate API.
    """
    with Network() as network:
        with LowkeyVaultContainer(container_alias="lowkey-vault").with_network(network) as lowkey_vault_container:
            network_connection_url = lowkey_vault_container.get_connection_url(network_type=NetworkType.NETWORK)
            imds_endpoint = lowkey_vault_container.get_imds_endpoint(network_type=NetworkType.NETWORK)
            token_url = lowkey_vault_container.get_token_url(network_type=NetworkType.NETWORK)
            with DockerImage(path=TEST_DIR / "samples/network_container", tag=IMAGE_TAG) as image:
                with (
                    DockerContainer(image=str(image))
                    .with_env("CONNECTION_URL", network_connection_url)
                    .with_env("AZURE_POD_IDENTITY_AUTHORITY_HOST", imds_endpoint)
                    .with_env("IMDS_ENDPOINT", imds_endpoint)
                    .with_env("IDENTITY_ENDPOINT", token_url)
                    .with_env("TEST", "certificates")
                    .with_env("CERT_NAME", "ec-cert-example-com")
                    .with_network(network)
                    .with_network_aliases("network_container")
                    .with_exposed_ports(80, 80) as container
                ):
                    wait_for_logs(container=container, predicate="Lowkey Vault Container created.")
                # make sure the container was actually created
                assert lowkey_vault_container is not None
