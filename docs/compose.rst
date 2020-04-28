Docker compose support
======================

Allows to spin up services configured via docker-compose.yml

Example docker-compose.yml for grid
-----------------------------------

::

    hub:
      image: selenium/hub
    ports:
      - "4444:4444"
    firefox:
      image: selenium/node-firefox
      links:
        - hub
      expose:
        - "5555"
    chrome:
      image: selenium/node-chrome
      links:
        - hub
      expose:
        - "5555"

Code
----

::

    compose = DockerCompose("/home/project", pull=True)
    with compose:
        host = compose.get_service_host("hub", 4444)
        port = compose.get_service_port("hub", 4444)
        driver = webdriver.Remote(
            command_executor=("http://{}:{}/wd/hub".format(host,port)),
            desired_capabilities=CHROME)
        driver.get("http://automation-remarks.com")

