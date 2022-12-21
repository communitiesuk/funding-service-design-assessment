pass

# from scripts.download_files import get_list_of_all_files,
# download_single_file, download_all_files
# import boto3, os

# aws_access_key_id="PLACEHOLDER"
# aws_secret_access_key="PLACEHOLDER"
# region_name="eu-west-2"
# aws_bucket_name = "PLACEHOLDER"

# s3_client = boto3.client("s3",
#                 aws_access_key_id=aws_access_key_id,
#                 aws_secret_access_key=aws_secret_access_key,
#                 region_name=region_name
#             )

# def test_list_files():
#     bucket_contents = get_list_of_all_files(s3_client,
# aws_bucket_name=aws_bucket_name)

#     assert len(bucket_contents) > 0, "Expected some files"
#     # for item in bucket_contents:
#     #     print(item)


# def test_download_file_no_prefix():
#     object_name = "/Book1.csv"
#     target_dir = "/Users/sarahsloan/tmp_downloads"
#     download_single_file(s3_client, target_dir, object_name, aws_bucket_name)
#     assert os.path.exists(os.path.join(target_dir, "Book1.csv"))

# def test_download_file_with_prefix():
#     object_name = "0c64f044-e084-4041-8210-df825ab4b48a/sample1.doc"
#     target_dir = "/Users/sarahsloan/tmp_downloads"
#     download_single_file(s3_client, target_dir, object_name, aws_bucket_name)
#     assert os.path.exists(os.path.join(target_dir, "sample1.doc"))

# # def test_download_all_files():
# #     download_all_files(
# #                 aws_access_key_id=aws_access_key_id,
# #                 aws_secret_access_key=aws_secret_access_key,
# #                 region_name=region_name,
# #                 aws_bucket_name=aws_bucket_name,
# #                 target_folder= "/Users/sarahsloan/tmp_downloads",
# #                 do_download= False)
