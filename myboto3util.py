import os
import sys
import traceback
import boto3
import botocore

region = os.environ.get('REGION', 'ap-northeast-1')

config = botocore.client.Config(signature_version='s3v4')
s3_client = boto3.client('s3', region_name=region, config=config)
s3_resource = boto3.resource('s3', region_name=region, config=config)

# log print用カラー変数
log_color_success_start = '\033[32m'
log_color_success_end = '\033[0m'
log_color_error_start = '\033[31m'
log_color_error_end = '\033[0m'

def get_last_modified_timestamp(path: str) -> float:
    return os.path.getmtime(path) if os.path.exists(path) else None

def upload_file_to_s3(s3bucket: str, s3key: str, local_file_path: str) -> bool:
    s3_client.upload_file(local_file_path, s3bucket, s3key)
    return True

def download_s3_file(s3bucket: str, s3key: str, dest: str) -> bool:
    try:
        if s3_file_exists(bucket_name=s3bucket, filename=s3key):
            if os.path.exists(dest) and not s3_file_modified(bucket=s3bucket, key=s3key, in_last_modified=get_last_modified_timestamp(dest)):
                return True

            # ファイル存在確認
            response = s3_client.head_object(Bucket=s3bucket, Key=s3key)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            print('download_s3_file', s3key, dest)
            s3_resource.Bucket(s3bucket).download_file(s3key, dest)
            # 最終更新日時を合わせる
            last_modified = response['LastModified']
            os.utime(dest, (last_modified.timestamp(), last_modified.timestamp()))
            return True
        else:
            if os.path.exists(dest):
                os.unlink(dest)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == '404':
            # Not Found はスルー
            pass
        else:
            raise e
    return False

def s3_file_exists(bucket_name: str, filename: str):
    try:
        result = s3_client.list_objects(Bucket=bucket_name, Prefix=filename )["Contents"]
        if len(result) > 0:
            return True
        else:
            return False
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print(e.response)
            return False
        else:
            raise
    except KeyError as e:
        return False
    else:
        return True

def s3_file_modified(bucket: str, key: str, in_last_modified: float) -> bool:
    try:
        response = s3_client.head_object(Bucket=bucket, Key=key)
        last_modified = response['LastModified']
        return in_last_modified != last_modified.timestamp()
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == '404':
            return False
        else:
            raise e
    return False
