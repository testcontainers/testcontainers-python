# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

RUN pip install azure-storage-blob==12.19.0

COPY ./netowrk_container.py netowrk_container.py
EXPOSE 80
# Define the command to run the application
CMD ["python", "netowrk_container.py"]
