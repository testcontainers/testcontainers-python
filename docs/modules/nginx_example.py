import json
import os
from pathlib import Path

import requests

from testcontainers.nginx import NginxContainer


def basic_example():
    with NginxContainer() as nginx:
        # Get connection parameters
        host = nginx.get_container_host_ip()
        port = nginx.get_exposed_port(nginx.port)
        nginx_url = f"http://{host}:{port}"
        print(f"Nginx URL: {nginx_url}")

        # Create test HTML file
        test_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Page</title>
        </head>
        <body>
            <h1>Hello from Nginx!</h1>
            <p>This is a test page.</p>
        </body>
        </html>
        """

        # Create test directory and file
        test_dir = Path("/tmp/nginx_test")
        test_dir.mkdir(exist_ok=True)
        test_file = test_dir / "index.html"
        test_file.write_text(test_html)

        # Copy test file to container
        nginx.get_container().copy_to_container(test_file, "/usr/share/nginx/html/")
        print("Copied test file to container")

        # Test basic HTTP request
        response = requests.get(nginx_url)
        print(f"\nBasic request status: {response.status_code}")
        print(f"Content type: {response.headers.get('content-type')}")
        print(f"Content length: {response.headers.get('content-length')}")

        # Test HEAD request
        head_response = requests.head(nginx_url)
        print("\nHEAD request headers:")
        print(json.dumps(dict(head_response.headers), indent=2))

        # Create test configuration
        test_config = """
        server {
            listen 80;
            server_name test.local;

            location /test {
                return 200 'Test location';
            }

            location /redirect {
                return 301 /test;
            }

            location /error {
                return 404 'Not Found';
            }
        }
        """

        # Write and copy configuration
        config_file = test_dir / "test.conf"
        config_file.write_text(test_config)
        nginx.get_container().copy_to_container(config_file, "/etc/nginx/conf.d/")
        print("\nCopied test configuration")

        # Reload Nginx configuration
        nginx.get_container().exec_run("nginx -s reload")
        print("Reloaded Nginx configuration")

        # Test custom location
        test_response = requests.get(f"{nginx_url}/test")
        print(f"\nTest location response: {test_response.text}")

        # Test redirect
        redirect_response = requests.get(f"{nginx_url}/redirect", allow_redirects=False)
        print(f"\nRedirect status: {redirect_response.status_code}")
        print(f"Redirect location: {redirect_response.headers.get('location')}")

        # Test error
        error_response = requests.get(f"{nginx_url}/error")
        print(f"\nError status: {error_response.status_code}")
        print(f"Error response: {error_response.text}")

        # Get Nginx version
        version_response = requests.get(nginx_url)
        server = version_response.headers.get("server")
        print(f"\nNginx version: {server}")

        # Test with different HTTP methods
        methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        print("\nHTTP method tests:")
        for method in methods:
            response = requests.request(method, nginx_url)
            print(f"{method}: {response.status_code}")

        # Clean up
        os.remove(test_file)
        os.remove(config_file)
        os.rmdir(test_dir)


if __name__ == "__main__":
    basic_example()
