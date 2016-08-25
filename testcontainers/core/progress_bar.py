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

import progressbar


class ConsoleProgressBar(object):
    def __init__(self):
        self.bar = progressbar.ProgressBar(widgets=[
            'Waiting for container to be ready: ',
            ' [', progressbar.Timer(), '] ',
        ], max_value=progressbar.UnknownLength)
