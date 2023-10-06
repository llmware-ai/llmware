# Testing

## Prereqs

The tests rely on pytest, tabulate and sentence-transformers

```bash
pip install pytest tabulate sentence-transformers
```

Mongo and Milvus are expected to be already running. From the root of this repo:

```bash
docker compose up -d
```

### Running all tests

```bash
./run-tests.sh
```

WARNING: This will "clean" the environment before running all tests:
- Uninstall any llmware modules locally installed
- Install the llmware module from this repo (simulating a user installing from pypi)
- Completely remove $HOME/llmware_data
- Reset Mongo and Milvus (drop all collections)

### Only running tests from a specific folder or file

```bash
./run-tests.sh tests/library
```

```bash
./run-tests.sh tests/models/test_all_generative_models.py
```

### Including printed output while test is running

By default pytest only shows output if tests fail.  If you want see printed output for all tests add the _-s_ switch

```bash
./run-tests.sh library -s
```
