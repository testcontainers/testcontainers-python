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
"""
testcontainers.community.influxdb provides means to spawn an InfluxDB instance within a Docker container.

- The InfluxDbContainer provides the common mechanism to spawn an InfluxDB container.
  You are not likely to use this module directly.
- Import the InfluxDb1Container class to spawn a container for an InfluxDB 1.x instance
- Import the InfluxDb2Container class to spawn a container for an InfluxDB 2.x instance

The 2 containers are separated in different modules for 2 reasons:
- because the Docker images are not designed to be used in the same way
- because the InfluxDB clients are different for 1.x and 2.x versions,
  so you won't have to install dependencies that you do not need
"""

from .base import InfluxDbContainer
from .version1 import InfluxDb1Container
from .version2 import InfluxDb2Container

__all__ = ["InfluxDb1Container", "InfluxDb2Container", "InfluxDbContainer"]
