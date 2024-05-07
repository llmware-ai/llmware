# Testing

## Prereqs

The tests rely on pytest and tabulate 

```bash
pip install pytest tabulate 
```

To run tests specific to a particular database or vector database requires that the resources are up and running.  

Some tests may require API Keys to particular cloud model providers.  If you would like to test that provider, then 
you can either edit the test code to include your own, or update ```~/set-env.sh``` and run the following to get 
the environment variables loaded in your shell:

```bash
source ~/set-env.sh
```

### Running all tests

```bash
python3 ./run-tests.py
```

Note: We do not currently recommend running all tests concurrently - we are updating our automation and test scope 
to improve this capability going forward.   

WARNING:  Initiating this script will "clean" the environment before running *_all tests_*:
- Uninstall any llmware modules locally installed
- Install the llmware module from this repo (simulating a user installing from pypi)
- Completely remove $HOME/llmware_data
- Reset Mongo and Milvus (drop all collections) -> not currently updated to drop Postgres and SQLITE DBs or other Vector DBs
- Run ./models/test_all_generative_models.py which will pull down many GBs of model files to the test systems.  


### Only running tests from a specific folder or file

This is our recommended testing approach, unless a PR has significant cross-module changes, and even in such cases 
it is usually more effective to run 2-3 individual tests and supplement with manual testing.  

Note:  please note that we are in the process of updating our test automation coverage suite.  We would welcome 
contributions from the community to continue to improve the automation and coverage scope of these tests.  

In addition to the formal tests, we would recommend using recent examples as well as good proxies, especially in 
targeted areas of the code base.  

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
