import urllib3
from azure.core.pipeline.transport._requests_basic import RequestsTransport
from azure.keyvault.secrets import SecretClient

from testcontainers.lowkeyvault import LowkeyVaultContainer


def basic_example():
    with LowkeyVaultContainer() as lowkey_vault_container:
        # get connection details
        connection_url = lowkey_vault_container.get_connection_url()
        print(f"Lowkey Vault is running: {connection_url}")
        token = lowkey_vault_container.get_token()
        print("Obtained token")
        # prepare a transport ignoring self-signed certificate issues
        transport = RequestsTransport(connection_verify=False)
        # make sure to turn off challenge resource verification
        secret_client: SecretClient = SecretClient(
            vault_url=connection_url, credential=token, verify_challenge_resource=False, transport=transport
        )

        # set a secret
        secret_client.set_secret(name="test-secret", value="a secret message")
        print("The secret has been set.")

        # get the value of the secret
        actual: str = secret_client.get_secret(name="test-secret").value
        print(f"The secret has been retrieved with value: '{actual}'")

        # close the secret client
        secret_client.close()


if __name__ == "__main__":
    # ignore cert errors
    urllib3.disable_warnings()
    # run the code
    basic_example()
