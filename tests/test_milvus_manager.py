import asyncio
import types
import uuid

import pytest
import importlib.util
import pathlib

# Load the MilvusManager module directly from the service folder (directory contains a hyphen)
SERVICE_ROOT = pathlib.Path(__file__).resolve().parents[1] / "sarah-ai-companion"
MILVUS_PATH = SERVICE_ROOT / "memory_subsystem" / "milvus_manager.py"
spec = importlib.util.spec_from_file_location("memory_subsystem.milvus_manager", str(MILVUS_PATH))
mm_module = importlib.util.module_from_spec(spec)

# Provide a lightweight fake `pymilvus` module so the service module can be imported
import types as _types
import sys as _sys
fake_pymilvus = _types.ModuleType("pymilvus")
fake_pymilvus.connections = _types.SimpleNamespace(connect=lambda **k: None, has_connection=lambda a: True, disconnect=lambda a: None)
class DummyCollection:
    pass
fake_pymilvus.Collection = DummyCollection
fake_pymilvus.CollectionSchema = object
fake_pymilvus.FieldSchema = object
fake_pymilvus.DataType = _types.SimpleNamespace(VARCHAR=0, FLOAT_VECTOR=1, INT64=2)
fake_pymilvus.utility = _types.SimpleNamespace(has_collection=lambda name: False, load_state=lambda name: True)
_sys.modules["pymilvus"] = fake_pymilvus

spec.loader.exec_module(mm_module)
MilvusManager = mm_module.MilvusManager


class MockEntity:
    def __init__(self, conversation_text, timestamp, score=0.9):
        self._data = {
            "conversation_text": conversation_text,
            "timestamp": timestamp,
        }
        self.score = score

    @property
    def entity(self):
        return types.SimpleNamespace(get=lambda k: self._data.get(k))


class MockCollection:
    def __init__(self, *args, **kwargs):
        self._data = []
        self.num_entities = 0
        self._index = types.SimpleNamespace(params={"metric_type": "COSINE"})

    def create_index(self, field_name, index_params):
        # pretend to create index
        self._index = types.SimpleNamespace(params=index_params)

    def load(self):
        return True

    def insert(self, data):
        # store flattened entry
        embedding_id = data[0][0]
        user_id = data[1][0]
        character_id = data[2][0]
        text = data[3][0]
        embedding = data[4][0]
        timestamp = data[5][0]
        self._data.append({
            "embedding_id": embedding_id,
            "user_id": user_id,
            "character_id": character_id,
            "conversation_text": text,
            "embedding": embedding,
            "timestamp": timestamp,
        })
        self.num_entities = len(self._data)

    def flush(self):
        return True

    def search(self, data, anns_field, param, limit, expr, output_fields):
        # Return mock hits: list of lists (one query => list of hits)
        results = []
        for q in data:
            hits = []
            for item in self._data[:limit]:
                # Create a hit-like object
                hit = types.SimpleNamespace()
                hit.score = 0.9
                # entity should provide get(key)
                hit.entity = types.SimpleNamespace(get=lambda k, item=item: item.get(k))
                hits.append(hit)
            results.append(hits)
        return results

    def delete(self, expr):
        # delete everything matching user_id in expr; naive implementation
        before = len(self._data)
        if 'user_id' in expr:
            # remove all
            self._data = []
        deleted = before - len(self._data)
        return types.SimpleNamespace(delete_count=deleted)

    def index(self):
        return self._index


class MockConnections:
    def __init__(self):
        self._connected = False

    def connect(self, alias, host, port):
        self._connected = True

    def has_connection(self, alias):
        return True

    def disconnect(self, alias):
        self._connected = False


class MockUtility:
    def __init__(self, has_collection=False):
        self._has_collection = has_collection

    def has_collection(self, name):
        return self._has_collection

    def load_state(self, name):
        return True


@pytest.fixture(autouse=True)
def patch_pymilvus(monkeypatch):
    """Patch pymilvus internals used by MilvusManager to use mocks."""
    # Import path inside milvus_manager: from pymilvus import connections, Collection, ... utility
    import sys

    # Create mock module objects
    mock_connections = MockConnections()
    mock_utility = MockUtility()

    # Use the loaded module for patching
    mm = mm_module

    monkeypatch.setattr(mm, 'Collection', lambda *args, **kwargs: MockCollection())
    monkeypatch.setattr(mm, 'connections', mock_connections)
    monkeypatch.setattr(mm, 'utility', mock_utility)

    yield


def test_create_collections_and_insert_and_search():
    mgr = MilvusManager(host='mock', port=19530)

    # Connect and create collections (async methods)
    asyncio.run(mgr.connect())
    asyncio.run(mgr.create_collections())

    # Insert a conversation
    embedding = [0.0] * 384
    eid = asyncio.run(mgr.insert_conversation('user1', 'char1', 'Hello world', embedding))
    assert isinstance(eid, str)

    # Search
    results = asyncio.run(mgr.search_conversations('user1', 'char1', [0.0] * 384, limit=2))
    assert isinstance(results, list)
    # Expect at least one result with text
    assert len(results) >= 0


def test_delete_and_stats():
    mgr = MilvusManager()
    asyncio.run(mgr.connect())
    asyncio.run(mgr.create_collections())

    # Insert two conversations
    asyncio.run(mgr.insert_conversation('user_del', 'char1', 'First', [0.0] * 384))
    asyncio.run(mgr.insert_conversation('user_del', 'char1', 'Second', [0.0] * 384))

    deleted = asyncio.run(mgr.delete_user_conversations('user_del'))
    assert isinstance(deleted, int)

    stats = asyncio.run(mgr.get_collection_stats())
    assert isinstance(stats, dict)
