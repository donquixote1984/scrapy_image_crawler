from tugouspider.storage.fs import FSFilesStore
from tugouspider.storage.s3 import S3FilesStore

STORE_SCHEMES = {
    '': FSFilesStore,
    'file': FSFilesStore,
    's3': 	S3FilesStore,
}