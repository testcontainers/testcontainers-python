import base64
import os

import urllib3
from azure.core.pipeline.transport._requests_basic import RequestsTransport
from azure.identity import DefaultAzureCredential
from azure.keyvault.certificates import CertificateClient, CertificatePolicy
from azure.keyvault.keys import KeyClient, KeyOperation
from azure.keyvault.keys.crypto import CryptographyClient, EncryptionAlgorithm, EncryptResult, DecryptResult
from azure.keyvault.secrets import SecretClient
from cryptography import x509
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePrivateKey
from cryptography.hazmat.primitives.serialization.pkcs12 import load_key_and_certificates

API_VERSION = "7.6"


def hello_secrets_from_an_external_container():
    """
    Entry point function for a custom Docker container to test connectivity
    and "secrets" functionality with Lowkey Vault.

    This function is designed to run inside a separate container within the
    same Docker network as a Lowkey Vault instance.
    """
    vault_url = os.environ["CONNECTION_URL"]
    secret_message = os.environ["SECRET_VALUE"]
    secret_name = os.environ["SECRET_NAME"]
    # test secrets API to see that the container works
    secret_client = None
    try:
        # ignore SSL errors because we are using a self-signed certificate
        transport_secrets = RequestsTransport(connection_verify=False)
        # create the client we need
        secret_client = SecretClient(
            vault_url=vault_url,
            credential=DefaultAzureCredential(),
            verify_challenge_resource=False,
            transport=transport_secrets,
            api_version=API_VERSION,
        )
        # set the result as a secret
        secret_client.set_secret(name=secret_name, value=secret_message)
        # get back the value
        actual = secret_client.get_secret(name=secret_name).value

        # verify the result
        assert actual == secret_message
        print("Lowkey Vault Container created.")
    except Exception as e:
        print(f"Something went wrong : {e}")
    finally:
        # close client
        if secret_client is not None:
            secret_client.close()


def hello_keys_from_an_external_container():
    """
    Entry point function for a custom Docker container to test connectivity
    and "keys" functionality with Lowkey Vault.

    This function is designed to run inside a separate container within the
    same Docker network as a Lowkey Vault instance.
    """
    vault_url = os.environ["CONNECTION_URL"]
    secret_message = os.environ["SECRET_VALUE"]
    key_name = os.environ["KEY_NAME"]
    # test key API to see that the container works
    key_client = None
    crypto_client = None
    try:
        # ignore SSL errors because we are using a self-signed certificate
        transport_keys = RequestsTransport(connection_verify=False)
        transport_crypto = RequestsTransport(connection_verify=False)
        # create the clients we need
        key_client = KeyClient(
            vault_url=vault_url,
            credential=DefaultAzureCredential(),
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
            credential=DefaultAzureCredential(),
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

        # verify the result
        assert decrypted_text == secret_message
        print("Lowkey Vault Container created.")
    except Exception as e:
        print(f"Something went wrong : {e}")
    finally:
        # close clients
        if key_client is not None:
            key_client.close()
        if crypto_client is not None:
            crypto_client.close()


def hello_certificates_from_an_external_container():
    """
    Entry point function for a custom Docker container to test connectivity
    and "certificates" functionality with Lowkey Vault.

    This function is designed to run inside a separate container within the
    same Docker network as a Lowkey Vault instance.
    """
    vault_url = os.environ["CONNECTION_URL"]
    cert_name = os.environ["CERT_NAME"]
    # test certificates API to see that the container works
    certificate_client = None
    secret_client = None
    try:
        # ignore SSL errors because we are using a self-signed certificate
        transport_certs = RequestsTransport(connection_verify=False)
        transport_secrets = RequestsTransport(connection_verify=False)
        # create the clients we need
        certificate_client = CertificateClient(
            vault_url=vault_url,
            credential=DefaultAzureCredential(),
            verify_challenge_resource=False,
            transport=transport_certs,
            api_version=API_VERSION,
        )
        secret_client = SecretClient(
            vault_url=vault_url,
            credential=DefaultAzureCredential(),
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

        # verify the result
        assert subject_name == x509_cert.subject.rdns[0].rfc4514_string()
        assert "secp256r1" == ec_key.curve.name

        print("Lowkey Vault Container created.")
    except Exception as e:
        print(f"Something went wrong : {e}")
    finally:
        # close clients
        if certificate_client is not None:
            certificate_client.close()
        if secret_client is not None:
            secret_client.close()


if __name__ == "__main__":
    mode = os.getenv("TEST")
    # ignore cert errors
    urllib3.disable_warnings()
    if mode == "secrets":
        hello_secrets_from_an_external_container()
    elif mode == "keys":
        hello_keys_from_an_external_container()
    elif mode == "certificates":
        hello_certificates_from_an_external_container()
    else:
        print("The TEST env variable must be 'secrets', 'keys', or 'certificates'.")
