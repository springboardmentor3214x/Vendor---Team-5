from app.services.activity_log_service import list_activity_logs, record_activity_log


class Query:
    def __init__(self, rows):
        self.rows = rows

    def filter(self, _condition):
        return self

    def order_by(self, _condition):
        return self

    def all(self):
        return self.rows


class Db:
    def __init__(self):
        self.added = []
        self.committed = False

    def add(self, item):
        self.added.append(item)

    def commit(self):
        self.committed = True

    def refresh(self, _item):
        pass

    def rollback(self):
        pass

    def query(self, _model):
        return Query(self.added)


def test_record_activity_log_uses_existing_columns_and_serializes_extra_context():
    db = Db()
    row = record_activity_log(db, 4, "Sent", "Communication", "message", 8, "127.0.0.1", {"subject": "Quote"})
    assert db.committed is True
    assert row.user_id == 4
    assert row.module == "Communication"
    assert '"related_entity_id": 8' in row.description
    assert list_activity_logs(db, {"user_id": 4}) == [row]
