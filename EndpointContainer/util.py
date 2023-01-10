import tarfile
import os
from google.cloud import storage

client = storage.Client()

def get_file(bucket_name, blob_name):
    blob = client.bucket(bucket_name) \
        .blob(blob_name)
    with open(blob_name, 'wb') as read_stream:
        blob.download_to_filename(read_stream)
        read_stream.close()
    return os.path.abspath(f"./{blob_name}")

def untar (fpath):
    with tarfile.open(fpath) as tar:
        tar.extractall('./source')
        tar.close()
    return os.path.abspath('./source')