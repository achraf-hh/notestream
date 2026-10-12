from eval.corpus.ingest import plan_uploads
from eval.corpus.manifest import Paper
from eval.corpus.state import corpus_mismatch

PAPERS = (
    Paper(id="gfs", title="GFS", url="https://example.org/gfs.pdf", sha256="0"),
    Paper(id="raft", title="Raft", url="https://example.org/raft.pdf", sha256="0"),
)


def test_empty_course_uploads_every_paper():
    found, missing, warnings = plan_uploads(PAPERS, on_server=[])

    assert found == {}
    assert [paper.id for paper in missing] == ["gfs", "raft"]
    assert warnings == []


def test_paper_already_on_the_server_is_recorded_not_uploaded_again():
    # The client timed out, but the server finished the upload: gfs exists, yet state lacks it.
    found, missing, _ = plan_uploads(PAPERS, on_server=[{"id": 7, "filename": "gfs.pdf"}])

    assert found == {"gfs": 7}
    assert [paper.id for paper in missing] == ["raft"]


def test_duplicate_copies_are_reported_and_the_oldest_is_kept():
    on_server = [{"id": 9, "filename": "gfs.pdf"}, {"id": 4, "filename": "gfs.pdf"}]

    found, _, warnings = plan_uploads(PAPERS, on_server)

    assert found["gfs"] == 4
    assert len(warnings) == 1


def test_documents_outside_the_manifest_are_ignored():
    found, missing, warnings = plan_uploads(PAPERS, on_server=[{"id": 1, "filename": "notes.pdf"}])

    assert found == {}
    assert len(missing) == 2
    assert warnings == []


def test_corpus_versions_must_match():
    assert corpus_mismatch({}, "v0") is None
    assert corpus_mismatch({"corpus_version": "v0"}, "v0") is None
    assert "v0" in corpus_mismatch({"corpus_version": "v0"}, "v1")
