"""Uploads a file to the GCS bucket."""

import os
import logging

from google.cloud import storage

logger = logging.getLogger(__name__)

GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
GCP_PROJECT = os.getenv("GCP_PROJECT")
BUCKET_NAME = os.getenv("BUCKET_NAME")


if __name__ == "__main__":
    storage_client = storage.Client(project=GCP_PROJECT).from_service_account_json(
        GOOGLE_APPLICATION_CREDENTIALS
    )

    bucket = storage_client.get_bucket(BUCKET_NAME)
    output = os.path.abspath('output/')

    # folder_suffixes
    month = []
    for m in month:
        folder_name = f"{m}"
        prefix = f"{folder_name}"

        files = os.listdir(f"batches/{folder_name}")

        for f in files:
            print(f"Uploading ...\n {f}")
            blob = bucket.blob(f"{prefix}/{f}")
            blob.upload_from_filename(f"{output}/batches/{folder_name}/{f}", content_type='application/x-gzip')
