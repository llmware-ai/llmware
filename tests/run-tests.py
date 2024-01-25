#!/usr/bin/env python 
import os
import pytest
import shutil 
import subprocess
import sys

from utils import Logger

class RunTests():

    # Grab the folders for the llmware and llmware-packaging repos.  They are assumed to live in the same parent folder
    def __init__(self):
        tests_folder = os.path.dirname(os.path.realpath(__file__))
        self.repo_root = os.path.join(tests_folder, "..")
    
    # Ensure the latest/greatest llmware module is installed locally
    def update_llmware_install(self):
        self.run_command("pip uninstall llmware -y", self.repo_root)
        self.run_command("pip install .", self.repo_root)

    # Try to start from as clean an environment as possible
    def clean_the_environment(self):
        Logger().log("Cleaning the environment...")

        # Remove the default data folder: $HOME/llmware_data
        llmware_data_dir = os.path.join(os.environ["HOME"],"llmware_data")
        llmware_data_custom_dir = os.path.join(os.environ["HOME"],"llmware_data_custom")
        Logger().log(f"Deleting {llmware_data_dir}")
        if os.path.exists(llmware_data_dir):
            shutil.rmtree(llmware_data_dir)

        if os.path.exists(llmware_data_custom_dir):
            shutil.rmtree(llmware_data_custom_dir)
            
        # Reset Mongo
        Logger().log("Resetting Mongo (deleting the llmware db)")
        from llmware.resources import MongoDBManager
        MongoDBManager().client.drop_database("llmware")

        # Reset Milvus
        Logger().log("Resetting Milvus (deleting all collections)")
        from llmware.configs import LLMWareConfig
        from pymilvus import connections, utility, FieldSchema, CollectionSchema, DataType, Collection
        connections.connect("default", host=os.environ.get('MILVUS_HOST','localhost') , port=19530)
        for collection in utility.list_collections():
            utility.drop_collection(collection)

    # Run a system command in the given dir, wait for it to complete and print the output
    def run_command(self, command, working_dir):
        Logger().log(f"Running command '{command}' in '{working_dir}'...")
        command_array = command.split(" ")
        command_output = ""
        p = subprocess.Popen(command_array, cwd=working_dir, stdout=subprocess.PIPE)
        for line in p.stdout:
            output_line = line.decode('utf8')
            command_output += output_line
            Logger().log(output_line)
        p.wait()
        Logger().log("")
        return command_output

test_runner = RunTests()
test_runner.update_llmware_install()
test_runner.clean_the_environment()
pytest.main(sys.argv[1:])