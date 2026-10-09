from src.core.file_lifecycle import (
    purge_staged_files,
    restore_staged_files,
    stage_files,
)


def test_stage_and_restore_file_on_database_failure(tmp_path):
    original = tmp_path / "report.pdf"
    original.write_bytes(b"synthetic-pdf")
    staged = stage_files([original])

    assert not original.exists()
    assert len(staged) == 1
    assert staged[0][1].exists()

    restore_staged_files(staged)
    assert original.read_bytes() == b"synthetic-pdf"
    assert not staged[0][1].exists()


def test_purge_staged_file_after_database_commit(tmp_path):
    original = tmp_path / "report.pdf"
    original.write_bytes(b"synthetic-pdf")
    staged = stage_files([original])

    purge_staged_files(staged)
    assert not original.exists()
    assert not staged[0][1].exists()


def test_missing_file_does_not_block_deletion(tmp_path):
    assert stage_files([tmp_path / "already-missing.pdf"]) == []
