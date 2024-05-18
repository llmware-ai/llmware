import os
import logging
import boto3
from botocore import UNSIGNED
from botocore.config import Config
from botocore.exceptions import ClientError

class ManualDownloader:

    def load_manuals_files(local_directory, bucket_name, over_write=False):
        """
         Downloads files from an AWS S3 bucket to a specified local directory.

         Args:
             local_directory (str): Local path to download files to.
             bucket_name (str): Name of the S3 bucket to download files from.
             over_write (bool): Whether to overwrite existing files.

         Returns:
             str: Path to the directory containing downloaded files.
         """
        # Create the local directory if it doesn't exist
        if not os.path.exists(local_directory):
            os.makedirs(local_directory, exist_ok=True)
        else:
            if not over_write:
                logging.info("Update: Directory already exists and overwrite is set to False - %s", local_directory)
                return local_directory

        # Setup the S3 client for unsigned access
        s3_client = boto3.client('s3', config=Config(signature_version=UNSIGNED))

        try:
            response = s3_client.list_objects_v2(Bucket=bucket_name)
            if 'Contents' not in response:
                raise RuntimeError("No files found in the bucket or unable to access bucket.")

            for item in response['Contents']:
                file_key = item['Key']
                file_path = os.path.join(local_directory, file_key)
                if not os.path.exists(file_path) or over_write:
                    s3_client.download_file(bucket_name, file_key, file_path)
                else:
                    logging.info("File already exists and overwrite is set to False: %s", file_path)
        except ClientError as e:
            raise RuntimeError(f"Failed to download files: {e}")
        
        return local_directory
