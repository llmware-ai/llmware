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

Some tests in the ./models and ./prompts folder require API Keys to cloud model providers.  You can edit the test code to include your own, or update ```~/set-env.sh``` and run the following to get the environment variables loaded in your shell:

```bash
source ~/set-env.sh
```

### Running all tests

```bash
python3 ./run-tests.py
```

WARNING: This will "clean" the environment before running *_all tests_*:
- Uninstall any llmware modules locally installed
- Install the llmware module from this repo (simulating a user installing from pypi)
- Completely remove $HOME/llmware_data
- Reset Mongo and Milvus (drop all collections)
- Run ./models/test_all_generative_models.py which will pull down many GBs of model files to the test systems.  



### Only running tests from a specific folder or file

```bash
python3 ./run-tests.py library
```

```bash
python3 ./run-tests.py models/test_all_generative_models.py
```

### Including printed output while test is running

By default pytest only shows output if tests fail.  If you want see printed output for all tests add the _-s_ switch

```bash
python3 ./run-tests.py library -s
```
