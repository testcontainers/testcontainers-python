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
import sys
from typing import Literal, Union

if sys.version_info < (3, 11):
    from typing_extensions import NotRequired, TypedDict
else:
    from typing import NotRequired, TypedDict


class QueueProperty(TypedDict):
    DeadLetteringOnMessageExpiration: NotRequired[bool]
    DefaultMessageTimeToLive: NotRequired[str]
    DuplicateDetectionHistoryTimeWindow: NotRequired[str]
    ForwardDeadLetteredMessagesTo: NotRequired[str]
    ForwardTo: NotRequired[str]
    LockDuration: NotRequired[str]
    MaxDeliveryCount: NotRequired[int]
    RequiresDuplicateDetection: NotRequired[bool]
    RequiresSession: NotRequired[bool]


class Queue(TypedDict):
    Name: str
    Properties: NotRequired[QueueProperty]


class CorrelationFilter(TypedDict):
    ContentType: NotRequired[str]
    CorrelationId: NotRequired[str]
    Label: NotRequired[str]
    MessageId: NotRequired[str]
    ReplyTo: NotRequired[str]
    ReplyToSessionId: NotRequired[str]
    SessionId: NotRequired[str]
    To: NotRequired[str]


class CorrelationRule(TypedDict):
    FilterType: Literal["Correlation"]
    CorrelationFilter: CorrelationFilter


class SQLFilter(TypedDict):
    SqlExpression: str


class SQLAction(TypedDict):
    SqlExpression: str


class SQLRule(TypedDict):
    FilterType: Literal["Sql"]
    SqlFilter: SQLFilter
    Action: SQLAction


class Rule(TypedDict):
    Name: str
    Properties: Union[CorrelationRule, SQLRule]


class SubscriptionProperty(TypedDict):
    DeadLetteringOnMessageExpiration: NotRequired[bool]
    DefaultMessageTimeToLive: NotRequired[str]
    LockDuration: NotRequired[str]
    MaxDeliveryCount: NotRequired[int]
    ForwardDeadLetteredMessagesTo: NotRequired[str]
    ForwardTo: NotRequired[str]
    RequiresSession: NotRequired[bool]


class Subscription(TypedDict):
    Name: str
    Properties: NotRequired[SubscriptionProperty]
    Rules: list[Rule]


class Topic(TypedDict):
    Name: str
    Properties: dict[str, Union[str, bool]]
    Subscriptions: list[Subscription]


class Namespace(TypedDict):
    Name: str
    Queues: list[Queue]
    Topics: list[Topic]


class UserConfig(TypedDict):
    Namespaces: list[Namespace]
    Logging: dict[str, str]


class ServiceBusConfiguration(TypedDict):
    UserConfig: str
