import os
from typing import Optional, List
from utils.config import Config

# Google Drive
try:
    from pydrive2.auth import GoogleAuth
    from pydrive2.drive import GoogleDrive
except ImportError:
    GoogleAuth = None
    GoogleDrive = None

# Dropbox
try:
    import dropbox
    from dropbox.files import WriteMode
except ImportError:
    dropbox = None

# S3
try:
    import boto3
    from botocore.exceptions import NoCredentialsError
except ImportError:
    boto3 = None

class CloudService:
    def __init__(self, config: Config):
        self.config = config
        self.gdrive = None
        self.dropbox = None
        self.s3 = None
        self._init_gdrive()
        self._init_dropbox()
        self._init_s3()

    # Google Drive Integration
    def _init_gdrive(self):
        if GoogleAuth is None or GoogleDrive is None:
            return
        self.gauth = GoogleAuth()
        # Try to load saved client credentials
        self.gauth.LoadCredentialsFile("gdrive_creds.txt")
        if self.gauth.credentials is None:
            # Authenticate if they're not there
            self.gauth.LocalWebserverAuth()
        elif self.gauth.access_token_expired:
            # Refresh them if expired
            self.gauth.Refresh()
        else:
            # Initialize the saved creds
            self.gauth.Authorize()
        self.gauth.SaveCredentialsFile("gdrive_creds.txt")
        self.gdrive = GoogleDrive(self.gauth)

    def upload_to_gdrive(self, local_path: str, remote_folder_id: Optional[str] = None) -> Optional[str]:
        if not self.gdrive:
            return None
        file_name = os.path.basename(local_path)
        gfile = self.gdrive.CreateFile({'title': file_name, 'parents': [{"id": remote_folder_id}] if remote_folder_id else []})
        gfile.SetContentFile(local_path)
        gfile.Upload()
        return gfile['id']

    def download_from_gdrive(self, file_id: str, dest_path: str) -> bool:
        if not self.gdrive:
            return False
        gfile = self.gdrive.CreateFile({'id': file_id})
        gfile.GetContentFile(dest_path)
        return True

    # Dropbox Integration
    def _init_dropbox(self):
        if dropbox is None:
            return
        token = self.config.get('dropbox_token')
        if token:
            self.dropbox = dropbox.Dropbox(token)

    def upload_to_dropbox(self, local_path: str, remote_path: str) -> Optional[str]:
        if not self.dropbox:
            return None
        with open(local_path, "rb") as f:
            self.dropbox.files_upload(f.read(), remote_path, mode=WriteMode('overwrite'))
        return remote_path

    def download_from_dropbox(self, remote_path: str, local_path: str) -> bool:
        if not self.dropbox:
            return False
        md, res = self.dropbox.files_download(remote_path)
        with open(local_path, "wb") as f:
            f.write(res.content)
        return True

    # S3 Integration
    def _init_s3(self):
        if boto3 is None:
            return
        aws_access_key_id = self.config.get('aws_access_key_id')
        aws_secret_access_key = self.config.get('aws_secret_access_key')
        aws_region = self.config.get('aws_region', 'us-east-1')
        if aws_access_key_id and aws_secret_access_key:
            self.s3 = boto3.client(
                's3',
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name=aws_region
            )

    def upload_to_s3(self, local_path: str, bucket: str, key: str) -> Optional[str]:
        if not self.s3:
            return None
        try:
            self.s3.upload_file(local_path, bucket, key)
            return f"s3://{bucket}/{key}"
        except NoCredentialsError:
            return None

    def download_from_s3(self, bucket: str, key: str, local_path: str) -> bool:
        if not self.s3:
            return False
        try:
            self.s3.download_file(bucket, key, local_path)
            return True
        except NoCredentialsError:
            return False

    # Unified interface
    def upload_file(self, local_path: str, provider: str, remote_path_or_id: Optional[str] = None, bucket: Optional[str] = None) -> Optional[str]:
        if provider == 'gdrive':
            return self.upload_to_gdrive(local_path, remote_folder_id=remote_path_or_id)
        elif provider == 'dropbox':
            return self.upload_to_dropbox(local_path, remote_path_or_id or f"/{os.path.basename(local_path)}")
        elif provider == 's3':
            if bucket is None or remote_path_or_id is None:
                return None
            return self.upload_to_s3(local_path, bucket, remote_path_or_id)
        else:
            return None

    def download_file(self, provider: str, remote_path_or_id: str, local_path: str, bucket: Optional[str] = None) -> bool:
        if provider == 'gdrive':
            return self.download_from_gdrive(remote_path_or_id, local_path)
        elif provider == 'dropbox':
            return self.download_from_dropbox(remote_path_or_id, local_path)
        elif provider == 's3':
            if bucket is None:
                return False
            return self.download_from_s3(bucket, remote_path_or_id, local_path)
        else:
            return False

    # Backup and restore
    def backup_logbook(self, db_path: str, provider: str, remote_path_or_id: Optional[str] = None, bucket: Optional[str] = None) -> Optional[str]:
        return self.upload_file(db_path, provider, remote_path_or_id, bucket)

    def restore_logbook(self, provider: str, remote_path_or_id: str, db_path: str, bucket: Optional[str] = None) -> bool:
        return self.download_file(provider, remote_path_or_id, db_path, bucket)

    # List files (for cloud providers that support it)
    def list_gdrive_files(self, folder_id: Optional[str] = None) -> List[dict]:
        if not self.gdrive:
            return []
        query = f"'{folder_id}' in parents and trashed=false" if folder_id else "trashed=false"
        file_list = self.gdrive.ListFile({'q': query}).GetList()
        return [{"id": f['id'], "title": f['title']} for f in file_list]

    def list_dropbox_files(self, folder: str = "") -> List[dict]:
        if not self.dropbox:
            return []
        res = self.dropbox.files_list_folder(folder)
        return [{"name": entry.name, "path": entry.path_display} for entry in res.entries]

    def list_s3_files(self, bucket: str, prefix: str = "") -> List[dict]:
        if not self.s3:
            return []
        res = self.s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
        files = []
        for obj in res.get('Contents', []):
            files.append({"key": obj['Key'], "size": obj['Size']})
        return files