import pytest
from unittest.mock import Mock, patch
from pymongo import MongoClient
from datetime import datetime
from modules.mongo import (  # Adjusted import path for mongo module
    feed_stats,
    user_stats,
    usage_stats,
    save_user,
    save_stats,
    save_error,
)


@pytest.fixture(scope="module")
def mock_mongo_client():
    with patch('modules.mongo.MongoClient') as mock_client:
        yield mock_client


@pytest.fixture(scope="module")
def mock_collections():
    stats_collection_mock = Mock()
    users_collection_mock = Mock()
    error_collection_mock = Mock()

    with patch('modules.mongo.stats_collection', stats_collection_mock), \
            patch('modules.mongo.users_collection', users_collection_mock), \
            patch('modules.mongo.error_collection', error_collection_mock):
        yield stats_collection_mock, users_collection_mock, error_collection_mock


def test_feed_stats(mock_collections):
    # Create mock data for stats_collection.aggregate
    mock_data = [
        {"link": "mock_link_1", "video_title": "Mock Video 1"},
        {"link": "mock_link_2", "video_title": "Mock Video 2"},
    ]
    mock_collections[0].aggregate.return_value = mock_data

    # Test feed_stats function
    result = feed_stats()
    assert isinstance(result, str)
    assert "Mock Video 1" in result
    assert "Mock Video 2" in result


def test_user_stats(mock_collections):
    # Create mock data for users_collection.aggregate
    mock_data = [
        {"lowercase_username": "user1"},
        {"lowercase_username": "user2"},
    ]
    mock_collections[1].aggregate.return_value = mock_data

    # Test user_stats function
    result = user_stats()
    assert isinstance(result, str)
    assert "user1" in result
    assert "user2" in result


def test_usage_stats(mock_collections):
    # Create mock data for stats_collection.count_documents and users_collection.aggregate
    mock_collections[0].count_documents.return_value = 100
    mock_data = [
        {"_id": "user1", "totalStatsCount": 10},
        {"_id": "user2", "totalStatsCount": 5},
    ]
    mock_collections[1].aggregate.return_value = mock_data

    # Test usage_stats function
    result = usage_stats()
    assert isinstance(result, str)
    assert "user1: 10" in result
    assert "user2: 5" in result


def test_save_user(mock_collections):
    # Test save_user function
    save_user(Mock(id=123))
    mock_collections[1].find_one.assert_called_once()


def test_save_stats(mock_collections):
    # Test save_stats function
    save_stats(456, "mock_video_url", "Mock Video")
    mock_collections[0].insert_one.assert_called_once()


def test_save_error(mock_collections):
    # Test save_error function
    save_error(789, "mock_error_url", "Mock Error")
    mock_collections[2].insert_one.assert_called_once()
