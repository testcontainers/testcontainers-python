from datetime import timedelta
from unittest.mock import MagicMock, Mock

import pytest

from testcontainers.core.policies import (AlwaysPullPolicy, DefaultPullPolicy,
                                          ImagePullPolicy, MaxAgePullPolicy)
from testcontainers.core.policies._cache import _LocalImagesCache


def test_default_pull_policy_cached_image():
    ImagePullPolicy.IMAGES_CACHE = MagicMock(spec=_LocalImagesCache)
    fake_cache = {'redis:latest': Mock()}
    ImagePullPolicy.IMAGES_CACHE.images_cache = fake_cache
    ImagePullPolicy.IMAGES_CACHE.__getitem__ = lambda self, item: fake_cache.__getitem__(item)

    policy = DefaultPullPolicy()
    assert not policy.should_pull('redis:latest')


def test_default_pull_policy_cache_refresh():
    ImagePullPolicy.IMAGES_CACHE = MagicMock(spec=_LocalImagesCache)
    fake_cache = {}
    ImagePullPolicy.IMAGES_CACHE.images_cache = fake_cache
    ImagePullPolicy.IMAGES_CACHE.__getitem__ = lambda self, item: fake_cache.__getitem__(item)
    ImagePullPolicy.IMAGES_CACHE.refresh.return_value = Mock()

    policy = DefaultPullPolicy()
    assert not policy.should_pull('redis:latest')


def test_default_pull_policy_uncached():
    ImagePullPolicy.IMAGES_CACHE = MagicMock(spec=_LocalImagesCache)
    fake_cache = {}
    ImagePullPolicy.IMAGES_CACHE.images_cache = fake_cache
    ImagePullPolicy.IMAGES_CACHE.__getitem__ = lambda self, item: fake_cache.__getitem__(item)
    ImagePullPolicy.IMAGES_CACHE.refresh.return_value = None

    policy = DefaultPullPolicy()
    assert policy.should_pull('redis:latest')


def test_always_pull_policy_cached_image():
    ImagePullPolicy.IMAGES_CACHE = MagicMock(spec=_LocalImagesCache)
    fake_cache = {'redis:latest': Mock()}
    ImagePullPolicy.IMAGES_CACHE.images_cache = fake_cache
    ImagePullPolicy.IMAGES_CACHE.__getitem__ = lambda self, item: fake_cache.__getitem__(item)

    policy = AlwaysPullPolicy()
    assert policy.should_pull('redis:latest')


def test_always_pull_policy_cache_refresh():
    ImagePullPolicy.IMAGES_CACHE = MagicMock(spec=_LocalImagesCache)
    fake_cache = {}
    ImagePullPolicy.IMAGES_CACHE.images_cache = fake_cache
    ImagePullPolicy.IMAGES_CACHE.__getitem__ = lambda self, item: fake_cache.__getitem__(item)
    ImagePullPolicy.IMAGES_CACHE.refresh.return_value = Mock()

    policy = AlwaysPullPolicy()
    assert policy.should_pull('redis:latest')


def test_always_pull_policy_uncached():
    ImagePullPolicy.IMAGES_CACHE = MagicMock(spec=_LocalImagesCache)
    fake_cache = {}
    ImagePullPolicy.IMAGES_CACHE.images_cache = fake_cache
    ImagePullPolicy.IMAGES_CACHE.__getitem__ = lambda self, item: fake_cache.__getitem__(item)
    ImagePullPolicy.IMAGES_CACHE.refresh.return_value = None

    policy = AlwaysPullPolicy()
    assert policy.should_pull('redis:latest')


@pytest.mark.freeze_time('2022-08-20')
def test_maxage_pull_policy_cached_image_recent():
    ImagePullPolicy.IMAGES_CACHE = MagicMock(spec=_LocalImagesCache)
    mock_image = Mock()
    mock_image.attrs = {'Created': '2022-08-19T02:34:26.413324739Z'}
    fake_cache = {'redis:latest': mock_image}
    ImagePullPolicy.IMAGES_CACHE.images_cache = fake_cache
    ImagePullPolicy.IMAGES_CACHE.__getitem__ = lambda self, item: fake_cache.__getitem__(item)

    policy = MaxAgePullPolicy(timedelta(days=30))
    assert not policy.should_pull('redis:latest')


@pytest.mark.freeze_time('2022-08-20')
def test_maxage_pull_policy_cache_refresh_not_old_enough():
    ImagePullPolicy.IMAGES_CACHE = MagicMock(spec=_LocalImagesCache)
    fake_cache = {}
    ImagePullPolicy.IMAGES_CACHE.images_cache = fake_cache
    ImagePullPolicy.IMAGES_CACHE.__getitem__ = lambda self, item: fake_cache.__getitem__(item)
    mock_image = Mock()
    mock_image.attrs = {'Created': '2022-08-19T02:34:26.413324739Z'}
    ImagePullPolicy.IMAGES_CACHE.refresh.return_value = mock_image

    policy = MaxAgePullPolicy(timedelta(days=30))
    assert not policy.should_pull('redis:latest')


@pytest.mark.freeze_time('2022-08-20')
def test_maxage_pull_policy_cache_refresh_too_old():
    ImagePullPolicy.IMAGES_CACHE = MagicMock(spec=_LocalImagesCache)
    fake_cache = {}
    ImagePullPolicy.IMAGES_CACHE.images_cache = fake_cache
    ImagePullPolicy.IMAGES_CACHE.__getitem__ = lambda self, item: fake_cache.__getitem__(item)
    mock_image = Mock()
    mock_image.attrs = {'Created': '2022-06-19T02:34:26.413324739Z'}
    ImagePullPolicy.IMAGES_CACHE.refresh.return_value = mock_image

    policy = MaxAgePullPolicy(timedelta(days=30))
    assert policy.should_pull('redis:latest')


def test_maxage_pull_policy_uncached():
    ImagePullPolicy.IMAGES_CACHE = MagicMock(spec=_LocalImagesCache)
    fake_cache = {}
    ImagePullPolicy.IMAGES_CACHE.images_cache = fake_cache
    ImagePullPolicy.IMAGES_CACHE.__getitem__ = lambda self, item: fake_cache.__getitem__(item)
    ImagePullPolicy.IMAGES_CACHE.refresh.return_value = None

    policy = MaxAgePullPolicy(timedelta(days=30))
    assert policy.should_pull('redis:latest')
