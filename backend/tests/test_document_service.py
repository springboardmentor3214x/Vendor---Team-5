from app.services.document_service import get_document_by_id, get_vendor_documents, update_document_metadata


class Document:
    def __init__(self, document_id, vendor_id, document_type, file_name="original.pdf", file_path="/original.pdf"):
        self.id = document_id
        self.vendor_id = vendor_id
        self.document_type = document_type
        self.file_name = file_name
        self.file_path = file_path


class Query:
    def __init__(self, documents):
        self.documents = documents

    def filter(self, condition):
        # SQLAlchemy predicates are not needed in these service-focused fake tests.
        return self

    def all(self):
        return self.documents

    def first(self):
        return self.documents[0] if self.documents else None


class Db:
    def __init__(self, documents):
        self.documents = documents
        self.committed = False

    def query(self, _model):
        return Query(self.documents)

    def commit(self):
        self.committed = True

    def refresh(self, _document):
        pass


def test_metadata_update_only_changes_document_type(monkeypatch):
    document = Document(1, 2, "PAN Card")
    db = Db([document])
    monkeypatch.setattr("app.services.document_service.get_document_by_id", lambda *_: document)

    updated = update_document_metadata(db, 1, "GST Certificate")

    assert updated.document_type == "GST Certificate"
    assert updated.file_name == "original.pdf"
    assert updated.file_path == "/original.pdf"
    assert db.committed is True


def test_document_queries_return_empty_or_missing_without_file_replacement():
    db = Db([])
    assert get_vendor_documents(db, 2) == []
    assert get_document_by_id(db, 1) is None
    assert update_document_metadata(db, 1, "GST Certificate") is None
