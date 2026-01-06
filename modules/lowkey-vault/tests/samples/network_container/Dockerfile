# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Install dependencies and create a dummy key file for the authentication to work
RUN \
    pip install azure-keyvault-certificates==4.10.0 && \
    pip install azure-keyvault-secrets==4.10.0 && \
    pip install azure-keyvault-keys==4.11.0 && \
    pip install cryptography==46.0.3 && \
    pip install azure-identity==1.25.1 && \
    mkdir -p /var/opt/azcmagent/tokens/ && \
    touch /var/opt/azcmagent/tokens/assumed-identity.key

COPY ./netowrk_container.py netowrk_container.py
EXPOSE 80
# Define the command to run the application
CMD ["python", "netowrk_container.py"]
