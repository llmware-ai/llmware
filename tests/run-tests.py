#!/usr/bin/env python 
import os
import pytest
import shutil
import subprocess
import sys

from utils import Logger


class RunTests:
    # Initialize and grab the folder paths for the llmware and llmware-packaging repos
    def __init__(self):
        tests_folder = os.path.dirname(os.path.realpath(__file__))
        self.repo_root = os.path.abspath(os.path.join(tests_folder, ".."))
        self.logger = Logger()

    # Ensure the latest llmware module is installed locally
    def update_llmware_install(self):
        self.logger.log("Updating llmware installation...")
        try:
            self.run_command("pip uninstall llmware -y", self.repo_root)
            self.run_command("pip install .", self.repo_root)
        except Exception as e:
            self.logger.log(f"Error updating llmware: {e}", level="error")
            sys.exit(1)

    # Clean the environment to start from a fresh state
    def clean_the_environment(self):
        self.logger.log("Cleaning the environment...")

        # Remove the default llmware data folders
        self.remove_folder(os.path.join(os.environ["HOME"], "llmware_data"))
        self.remove_folder(os.path.join(os.environ["HOME"], "llmware_data_custom"))

        # Reset MongoDB
        try:
            self.logger.log("Resetting MongoDB (dropping the 'llmware' database)...")
            from llmware.resources import MongoDBManager
            MongoDBManager().client.drop_database("llmware")
        except Exception as e:
            self.logger.log(f"Error resetting MongoDB: {e}", level="error")
            sys.exit(1)

        # Reset Milvus collections
        try:
            self.logger.log("Resetting Milvus (dropping all collections)...")
            from llmware.configs import LLMWareConfig
            from pymilvus import connections, utility
            connections.connect("default", host=os.environ.get('MILVUS_HOST', 'localhost'), port=19530)
            for collection in utility.list_collections():
                utility.drop_collection(collection)
            self.logger.log("All Milvus collections dropped successfully.")
        except Exception as e:
            self.logger.log(f"Error resetting Milvus: {e}", level="error")
            sys.exit(1)

    # Helper function to remove a folder if it exists
    def remove_folder(self, folder_path):
        if os.path.exists(folder_path):
            try:
                self.logger.log(f"Removing folder: {folder_path}")
                shutil.rmtree(folder_path)
            except Exception as e:
                self.logger.log(f"Error removing folder {folder_path}: {e}", level="error")
        else:
            self.logger.log(f"Folder not found: {folder_path}")

    # Run a system command in the given directory, wait for it to complete, and log the output
    def run_command(self, command, working_dir):
        self.logger.log(f"Running command '{command}' in '{working_dir}'...")
        command_array = command.split(" ")
        try:
            process = subprocess.Popen(command_array, cwd=working_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            if stdout:
                self.logger.log(stdout.decode('utf-8'))
            if stderr:
                self.logger.log(stderr.decode('utf-8'), level="error")
            if process.returncode != 0:
                raise subprocess.CalledProcessError(process.returncode, command)
        except subprocess.CalledProcessError as e:
            self.logger.log(f"Command '{command}' failed with error: {e}", level="error")
            sys.exit(1)
        except Exception as e:
            self.logger.log(f"An unexpected error occurred while running '{command}': {e}", level="error")
            sys.exit(1)


if __name__ == "__main__":
    test_runner = RunTests()

    # Update and clean environment before running tests
    test_runner.update_llmware_install()
    test_runner.clean_the_environment()

    # Run the tests with pytest
    try:
        pytest.main(sys.argv[1:])
    except Exception as e:
        test_runner.logger.log(f"Error running tests: {e}", level="error")
        sys.exit(1)
