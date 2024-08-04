#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
from __future__ import annotations

import os
import tempfile
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Any, NamedTuple

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import (
    NoEncryption,
)
from cryptography.x509.oid import NameOID

from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs

if TYPE_CHECKING:
    from typing_extensions import Self


class MailpitUser(NamedTuple):
    """Mailpit user for authentication

    Helper class to define a user for Mailpit authentication.

    This is just a named tuple for username and password.


    Example:

        .. doctest::

            >>> from testcontainers.mailpit import MailpitUser

            >>> users = [
            ...     MailpitUser("jane", "secret"),
            ...     MailpitUser("ron", "pass2"),
            ... ]

            >>> for user in users:
            ...     print(user.username, user.password)
            ...
            jane secret
            ron pass2

            >>> username, password = users[0]

            >>> print(username, password)
            jane secret
    """

    username: str
    password: str


class MailpitContainer(DockerContainer):
    """
    Test container for Mailpit. The example below spins up a Mailpit server

    Default configuration supports SMTP with STARTTLS and allows login with any
    user/password.

    Options:

    * ``require_tls = True`` forces the use of SSL
    * ``users = [MailpitUser("jane", "secret"), MailpitUser("ron", "pass2")]`` \
    only allows login with ``jane:secret`` or ``ron:pass2``

    Simple example:

        .. doctest::

            >>> import smtplib

            >>> from testcontainers.mailpit import MailpitContainer

            >>> with MailpitContainer() as mailpit_container:
            ...     host_ip = mailpit_container.get_container_host_ip()
            ...     host_port = mailpit_container.get_exposed_smtp_port()
            ...     server = smtplib.SMTP(
            ...         mailpit_container.get_container_host_ip(),
            ...         mailpit_container.get_exposed_smtp_port(),
            ...     )
            ...     code, _ = server.login("any", "auth")
            ...     assert code == 235  # authentication successful
            ...     # use server.sendmail(...) to send emails

    Example with auth and forced TLS:

        .. doctest::

            >>> import smtplib

            >>> from testcontainers.mailpit import MailpitContainer, MailpitUser

            >>> users = [MailpitUser("jane", "secret"), MailpitUser("ron", "pass2")]

            >>> with MailpitContainer(users=users, require_tls=True) as mailpit_container:
            ...     host_ip = mailpit_container.get_container_host_ip()
            ...     host_port = mailpit_container.get_exposed_smtp_port()
            ...     server = smtplib.SMTP_SSL(
            ...         mailpit_container.get_container_host_ip(),
            ...         mailpit_container.get_exposed_smtp_port(),
            ...     )
            ...     code, _ = server.login("jane", "secret")
            ...     assert code == 235  # authentication successful
            ...     # use server.sendmail(...) to send emails
    """

    def __init__(
        self,
        image: str = "axllent/mailpit",
        *,
        smtp_port: int = 1025,
        ui_port: int = 8025,
        users: list[MailpitUser] | None = None,
        require_tls: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(image=image, **kwargs)
        self.smtp_port = smtp_port
        self.ui_port = ui_port

        self.users = users if users is not None else []
        self.auth_accept_any = int(len(self.users) == 0)

        self.require_tls = int(require_tls)
        self.tls_key, self.tls_cert = _generate_tls_certificates()
        with tempfile.NamedTemporaryFile(delete=False) as tls_key_file:
            tls_key_file.write(self.tls_key)
            self.tls_key_file = tls_key_file.name

        with tempfile.NamedTemporaryFile(delete=False) as tls_cert_file:
            tls_cert_file.write(self.tls_cert)
            self.tls_cert_file = tls_cert_file.name

    @property
    def _users_conf(self) -> str:
        """Mailpit user configuration string

        "user:password user2:pass2 ...]
        """
        return " ".join(f"{user.username}:{user.password}" for user in self.users)

    def _configure(self) -> None:
        if self.users:
            self.with_env("MP_SMTP_AUTH", self._users_conf)
        self.with_env("MP_SMTP_AUTH_ACCEPT_ANY", str(self.auth_accept_any))

        self.with_env("MP_SMTP_REQUIRE_TLS", str(self.require_tls))

        self.with_volume_mapping(self.tls_cert_file, "/cert.pem")
        self.with_volume_mapping(self.tls_key_file, "/key.pem")
        self.with_env("MP_SMTP_TLS_CERT", "/cert.pem")
        self.with_env("MP_SMTP_TLS_KEY", "/key.pem")

        self.with_exposed_ports(self.smtp_port, self.ui_port)

    def start(self) -> Self:
        super().start()
        wait_for_logs(self, ".*accessible via.*")
        return self

    def stop(self, *args: Any, **kwargs: Any) -> None:
        super().stop(*args, **kwargs)
        os.remove(self.tls_key_file)
        os.remove(self.tls_cert_file)

    def get_exposed_smtp_port(self) -> int:
        return int(self.get_exposed_port(self.smtp_port))

    def get_exposed_ui_port(self) -> int:
        return int(self.get_exposed_port(self.ui_port))

    def get_base_api_url(self) -> str:
        return f"http://{self.get_container_host_ip()}:{self.get_exposed_ui_port()}"


class _TLSCertificates(NamedTuple):
    private_key: bytes
    certificate: bytes


def _generate_tls_certificates() -> _TLSCertificates:
    """Generate self-signed TLS certificates as bytes"""
    private_key = _generate_private_key()
    certificate = _generate_self_signed_certificate(private_key)

    private_key_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=NoEncryption(),
    )
    certificate_bytes = certificate.public_bytes(serialization.Encoding.PEM)

    return _TLSCertificates(private_key_bytes, certificate_bytes)


def _generate_private_key() -> rsa.RSAPrivateKey:
    """Generate RSA private key"""
    return rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
    )


def _generate_self_signed_certificate(
    private_key: rsa.RSAPrivateKey,
) -> x509.Certificate:
    """Generate self-signed certificate with RSA private key"""
    domain = "mydomain.com"
    subject = issuer = x509.Name(
        [
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "California"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "The Post Office"),
            x509.NameAttribute(NameOID.COMMON_NAME, domain),
        ]
    )

    return (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(timezone.utc))
        .not_valid_after(datetime.now(timezone.utc) + timedelta(days=3650))  # 10 years
        .add_extension(
            x509.SubjectAlternativeName([x509.DNSName(domain)]),
            critical=False,
        )
        .sign(private_key, hashes.SHA256())
    )
