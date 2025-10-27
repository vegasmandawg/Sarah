# Sarah AI Mock-Based Tests

This directory contains mock-based tests for Sarah's services, designed to run quickly without external dependencies.

## Available Tests

### Memory Subsystem Tests

- `test_milvus_manager.py`: Tests Milvus operations using in-memory mocks
  - Create/insert/search conversations
  - Delete user conversations
  - Collection statistics

To run:
```bash
# Run all tests
pytest -q tests/

# Run specific test file
pytest -q tests/test_milvus_manager.py

# Run with function matching
pytest -q tests/test_milvus_manager.py::test_create_collections_and_insert_and_search
```

## Mock System Design

### Milvus Mocking (`test_milvus_manager.py`)

The test provides lightweight fakes for `pymilvus`:
- `MockCollection`: In-memory storage with basic insert/search/delete
- `MockConnections`: Connection state management
- `MockUtility`: Collection existence checks
- Fake schema objects that accept but don't validate parameters

Example usage in CI:
```yaml
name: Memory Subsystem Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - run: pip install pytest
      - run: pytest -q tests/test_milvus_manager.py
```

## Adding New Mock Tests

1. Create a test file under `tests/`
2. Import the service module directly using `importlib.util` if the path contains special characters
3. Define minimal mock classes that implement only the methods used by your code
4. Use `pytest.fixture` to inject mocks before tests run
5. Include examples in this README

## Best Practices

- Keep mocks minimal - implement only what the test needs
- Document mock behavior and limitations
- Use type hints to catch API drift
- Test error cases (e.g., connection failures)
- Don't mock what you don't own (standard library, etc)

## Roadmap

Planned mock test coverage:
- Memory Extractor (mock Persona Engine endpoints)
- Persona Engine (mock Ollama API)
- Multimodal Engine (mock FLUX.1 and ElevenLabs APIs)