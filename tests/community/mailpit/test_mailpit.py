import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import pytest

from testcontainers.mailpit import MailpitContainer, MailpitUser

_sender = "from@example.com"
_receivers = ["to@example.com"]
_msg = MIMEMultipart("mixed")
_msg["From"] = _sender
_msg["To"] = ", ".join(_receivers)
_msg["Subject"] = "test"
_msg.attach(MIMEText("test", "plain"))
_sendmail_args = (_sender, _receivers, _msg.as_string())


def test_mailpit_basic():
    config = MailpitContainer()
    with config as mailpit:
        server = smtplib.SMTP(
            mailpit.get_container_host_ip(),
            mailpit.get_exposed_smtp_port(),
        )
        server.login("any", "auth")
        server.sendmail(*_sendmail_args)


def test_mailpit_starttls():
    config = MailpitContainer()
    with config as mailpit:
        server = smtplib.SMTP(
            mailpit.get_container_host_ip(),
            mailpit.get_exposed_smtp_port(),
        )
        server.starttls()
        server.login("any", "auth")
        server.sendmail(*_sendmail_args)


def test_mailpit_force_tls():
    config = MailpitContainer(require_tls=True)
    with config as mailpit:
        server = smtplib.SMTP_SSL(
            mailpit.get_container_host_ip(),
            mailpit.get_exposed_smtp_port(),
        )
        server.login("any", "auth")
        server.sendmail(*_sendmail_args)


def test_mailpit_basic_with_users_pass_auth():
    users = [MailpitUser("user", "password")]
    config = MailpitContainer(users=users)
    with config as mailpit:
        server = smtplib.SMTP(
            mailpit.get_container_host_ip(),
            mailpit.get_exposed_smtp_port(),
        )
        server.login(mailpit.users[0].username, mailpit.users[0].password)
        server.sendmail(*_sendmail_args)


def test_mailpit_basic_with_users_fail_auth():
    users = [MailpitUser("user", "password")]
    config = MailpitContainer(users=users)
    with pytest.raises(smtplib.SMTPAuthenticationError):
        with config as mailpit:
            server = smtplib.SMTP(
                mailpit.get_container_host_ip(),
                mailpit.get_exposed_smtp_port(),
            )
            server.login("not", "good")


def test_mailpit_starttls_with_users_pass_auth():
    users = [MailpitUser("user", "password")]
    config = MailpitContainer(users=users)
    with config as mailpit:
        server = smtplib.SMTP(
            mailpit.get_container_host_ip(),
            mailpit.get_exposed_smtp_port(),
        )
        server.starttls()
        server.login(mailpit.users[0].username, mailpit.users[0].password)
        server.sendmail(*_sendmail_args)


def test_mailpit_starttls_with_users_fail_auth():
    users = [MailpitUser("user", "password")]
    config = MailpitContainer(users=users)
    with pytest.raises(smtplib.SMTPAuthenticationError):
        with config as mailpit:
            server = smtplib.SMTP(
                mailpit.get_container_host_ip(),
                mailpit.get_exposed_smtp_port(),
            )
            server.starttls()
            server.login("not", "good")


def test_mailpit_force_tls_with_users_pass_auth():
    users = [MailpitUser("user", "password")]
    config = MailpitContainer(users=users, require_tls=True)
    with config as mailpit:
        server = smtplib.SMTP_SSL(
            mailpit.get_container_host_ip(),
            mailpit.get_exposed_smtp_port(),
        )
        server.login(mailpit.users[0].username, mailpit.users[0].password)
        server.sendmail(*_sendmail_args)


def test_mailpit_force_tls_with_users_fail_auth():
    users = [MailpitUser("user", "password")]
    config = MailpitContainer(users=users, require_tls=True)
    with pytest.raises(smtplib.SMTPAuthenticationError):
        with config as mailpit:
            server = smtplib.SMTP_SSL(
                mailpit.get_container_host_ip(),
                mailpit.get_exposed_smtp_port(),
            )
            server.login("not", "good")
