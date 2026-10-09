"""Storage deletion is idempotent for versioned S3 delete markers."""

from types import SimpleNamespace

from botocore.exceptions import ClientError

from src.core import storage


class FakeS3:
    def __init__(self, missing=False):
        self.missing = missing
        self.deleted = 0

    def head_object(self, **kwargs):
        if self.missing:
            raise ClientError(
                {"Error": {"Code": "404", "Message": "Not Found"}}, "HeadObject"
            )
        return {}

    def delete_object(self, **kwargs):
        self.deleted += 1


def test_delete_report_does_not_create_duplicate_s3_delete_markers(monkeypatch):
    fake = FakeS3(missing=True)
    monkeypatch.setattr(
        storage,
        "get_settings",
        lambda: SimpleNamespace(
            storage_backend="s3", object_storage_bucket="private-reports"
        ),
    )
    monkeypatch.setattr(storage, "_s3_client", lambda: fake)
    storage.delete_report("synthetic-user/synthetic-report.pdf")
    assert fake.deleted == 0


def test_delete_report_removes_existing_s3_object(monkeypatch):
    fake = FakeS3()
    monkeypatch.setattr(
        storage,
        "get_settings",
        lambda: SimpleNamespace(
            storage_backend="s3", object_storage_bucket="private-reports"
        ),
    )
    monkeypatch.setattr(storage, "_s3_client", lambda: fake)
    storage.delete_report("synthetic-user/synthetic-report.pdf")
    assert fake.deleted == 1
