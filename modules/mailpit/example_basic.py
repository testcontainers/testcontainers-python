import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests

from testcontainers.mailpit import MailpitContainer


def basic_example():
    with MailpitContainer() as mailpit:
        # Get SMTP and API endpoints
        smtp_host = mailpit.get_container_host_ip()
        smtp_port = mailpit.get_exposed_smtp_port()
        api_url = mailpit.get_base_api_url()

        # Create email message
        msg = MIMEMultipart()
        msg["From"] = "sender@example.com"
        msg["To"] = "recipient@example.com"
        msg["Subject"] = "Test Email"

        body = "This is a test email sent to Mailpit."
        msg.attach(MIMEText(body, "plain"))

        # Send email using SMTP
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.send_message(msg)
            print("Email sent successfully")

        # Wait for email to be processed
        time.sleep(1)

        # Check received emails using API
        response = requests.get(f"{api_url}/api/v1/messages")
        messages = response.json()

        print("\nReceived emails:")
        for message in messages["messages"]:
            print(f"From: {message['From']['Address']}")
            print(f"To: {message['To'][0]['Address']}")
            print(f"Subject: {message['Subject']}")
            print(f"Body: {message['Text']}")
            print("---")

        # Get specific email details
        if messages["messages"]:
            first_message = messages["messages"][0]
            message_id = first_message["ID"]

            response = requests.get(f"{api_url}/api/v1/messages/{message_id}")
            message_details = response.json()

            print("\nDetailed message info:")
            print(f"Size: {message_details['Size']} bytes")
            print(f"Created: {message_details['Created']}")
            print(f"Attachments: {len(message_details['Attachments'])}")


if __name__ == "__main__":
    basic_example()
