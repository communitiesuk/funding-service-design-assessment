import argparse
import os
from datetime import datetime
from os.path import exists
from os.path import join

import boto3
from botocore.exceptions import ClientError
from distutils.util import strtobool


def download_single_file(
    s3_client, target_folder, object_name, aws_bucket_name
):
    file_name = object_name.split("/")[-1]
    with open(join(target_folder, file_name), "wb") as f:
        s3_client.download_fileobj(aws_bucket_name, object_name, f)


def get_list_of_all_files(s3_client, aws_bucket_name):
    try:

        bucket_contents = s3_client.list_objects(Bucket=aws_bucket_name)
        if bucket_contents["ResponseMetadata"]["HTTPStatusCode"] == 200:
            return bucket_contents["Contents"]
        else:
            raise Exception(
                "Status code from s3 call was"
                f" {bucket_contents['ResponseMetadata']['HTTPStatusCode']}"
            )

    except ClientError as e:
        print("failed to get list of files")
        print(e)
        quit(1)


def download_all_files(
    region_name,
    aws_access_key_id,
    aws_secret_access_key,
    aws_bucket_name,
    target_folder,
    do_download=False,
):
    if not exists(target_folder):
        print("Please create target directory")
        quit(0)

    downloads_dir = "aws_downloads_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    full_downloads_path = join(target_folder, downloads_dir)
    os.mkdir(full_downloads_path)
    print(f"Created output dir: {full_downloads_path}")

    s3_client = boto3.client(
        "s3",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region_name,
    )

    list_of_objects = get_list_of_all_files(s3_client, aws_bucket_name)

    print(f"Total of {len(list_of_objects)} objects to download")

    count = 0
    if do_download:
        for file in list_of_objects:
            count += 1
            key = file["Key"]
            paths = key.split("/")
            target_dir_for_file = full_downloads_path
            if not key.startswith("/") and len(paths) > 1:
                target_dir_for_file = join(full_downloads_path, paths[0])
                if not os.path.exists(target_dir_for_file):
                    os.mkdir(target_dir_for_file)

            download_single_file(
                s3_client, target_dir_for_file, key, aws_bucket_name
            )

            print(
                f"{count} - downloaded to {target_dir_for_file} :"
                f" {key.split('/')[-1]}"
            )


def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--region_name", help="Provide AWS region", required=True
    )
    parser.add_argument(
        "--aws_access_key_id", help="Provide AWS access key", required=True
    )
    parser.add_argument(
        "--aws_secret_access_key",
        help="Provide AWS secret key",
        required=True,
    )
    parser.add_argument(
        "--aws_bucket_name",
        help="Provide AWS bucket name",
        required=True,
    )
    parser.add_argument(
        "--target_folder",
        help="Provide target folder for downloads",
        required=True,
    )
    parser.add_argument(
        "--do_download",
        help=(
            "Whether to actually download files - if false will just print"
            " number of files to download and exit"
        ),
        required=True,
    )
    return parser


def main() -> None:
    parser = init_argparse()
    args = parser.parse_args()
    download_all_files(
        aws_access_key_id=args.aws_access_key_id,
        aws_bucket_name=args.aws_bucket_name,
        region_name=args.region_name,
        aws_secret_access_key=args.aws_secret_access_key,
        target_folder=args.target_folder,
        do_download=strtobool(args.do_download),
    )


if __name__ == "__main__":
    # with app.app_context():
    main()
