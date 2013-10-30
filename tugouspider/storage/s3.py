import rfc822
class S3FilesStore(object):

    AWS_ACCESS_KEY_ID = None
    AWS_SECRET_ACCESS_KEY = None

    POLICY = 'public-read'
    HEADERS = {
        'Cache-Control': 'max-age=172800',
    }

    def __init__(self, uri):
        assert uri.startswith('s3://')
        self.bucket, self.prefix = uri[5:].split('/', 1)

    def stat_file(self, key, info):
        def _onsuccess(boto_key):
            checksum = boto_key.etag.strip('"')
            last_modified = boto_key.last_modified
            modified_tuple = rfc822.parsedate_tz(last_modified)
            modified_stamp = int(rfc822.mktime_tz(modified_tuple))
            return {'checksum': checksum, 'last_modified': modified_stamp}

        return self._get_boto_key(key).addCallback(_onsuccess)

    def _get_boto_bucket(self):
        from boto.s3.connection import S3Connection
        # disable ssl (is_secure=False) because of this python bug:
        # http://bugs.python.org/issue5103
        c = S3Connection(self.AWS_ACCESS_KEY_ID, self.AWS_SECRET_ACCESS_KEY, is_secure=False)
        return c.get_bucket(self.bucket, validate=False)

    def _get_boto_key(self, key):
        b = self._get_boto_bucket()
        key_name = '%s%s' % (self.prefix, key)
        return threads.deferToThread(b.get_key, key_name)

    def persist_file(self, key, buf, info, meta=None, headers=None):
        """Upload file to S3 storage"""
        b = self._get_boto_bucket()
        key_name = '%s%s' % (self.prefix, key)
        k = b.new_key(key_name)
        if meta:
            for metakey, metavalue in meta.iteritems():
                k.set_metadata(metakey, str(metavalue))
        h = self.HEADERS.copy()
        if headers:
            h.update(headers)
        buf.seek(0)
        return threads.deferToThread(k.set_contents_from_string, buf.getvalue(),
                                     headers=h, policy=self.POLICY)

