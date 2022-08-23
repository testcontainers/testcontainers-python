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

from docker.models.images import Image

from testcontainers.core.policies.base import ImagePullPolicy


class AlwaysPullPolicy(ImagePullPolicy):
    """
    An ImagePullPolicy which pulls the image even if it exists locally.
    Useful for obtaining the latest version of an image with a static tag, i.e. 'latest'
    """

    def should_pull_cached(self, image: Image) -> bool:
        return True
