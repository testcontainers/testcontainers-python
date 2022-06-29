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

import json
import urllib

from testcontainers.opensearch import OpenSearchContainer


def test_docker_run_opensearch():
    version = 'latest'
    with OpenSearchContainer(f'opensearchproject/opensearch:{version}') as osearch:
        resp = urllib.request.urlopen(osearch.get_url())
        assert json.loads(resp.read().decode())['version']['number'] == version
