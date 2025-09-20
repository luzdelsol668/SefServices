from storages.backends.s3boto3 import S3Boto3Storage

from sefservices import settings

AWS_S3_PREVIEW_URL = settings.AWS_S3_PREVIEW_URL
AWS_STORAGE_BUCKET_NAME = settings.AWS_STORAGE_BUCKET_NAME

class MediaStorage(S3Boto3Storage):
    location = 'medias'
    file_overwrite = True
    custom_domain = f'{AWS_S3_PREVIEW_URL}/{AWS_STORAGE_BUCKET_NAME}'

class StaticStorage(S3Boto3Storage):
    location = 'static'
    file_overwrite = True
    custom_domain = f'{AWS_S3_PREVIEW_URL}/{AWS_STORAGE_BUCKET_NAME}'





