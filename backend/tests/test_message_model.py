from datetime import datetime, timedelta
import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.user import User
from app.models.communication import Communication
from app.models.discussion import Discussion
from app.models.message import Message, RelatedEntityType


@pytest.fixture
def in_memory_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    try:
        yield db, engine
    finally:
        db.close()


def test_message_table_schema_and_indexes(in_memory_db):
    db, engine = in_memory_db
    inspector = inspect(engine)
    
    assert "messages" in inspector.get_table_names()
    columns = {col["name"]: col for col in inspector.get_columns("messages")}
    
    assert "id" in columns
    assert "sender_id" in columns
    assert "receiver_id" in columns
    assert "content" in columns
    assert "related_entity_type" in columns
    assert "related_entity_id" in columns
    assert "is_read" in columns
    assert "created_at" in columns
    assert "read_at" in columns
    
    indexes = {idx["name"]: idx for idx in inspector.get_indexes("messages")}
    assert "ix_messages_sender_id_created_at" in indexes
    assert indexes["ix_messages_sender_id_created_at"]["column_names"] == ["sender_id", "created_at"]
    
    assert "ix_messages_receiver_id_is_read_created_at" in indexes
    assert indexes["ix_messages_receiver_id_is_read_created_at"]["column_names"] == ["receiver_id", "is_read", "created_at"]


def test_message_creation_and_query(in_memory_db):
    db, _ = in_memory_db
    
    u1 = User(full_name="Alice", email="alice@example.com", hashed_password="pw", role="Administrator")
    u2 = User(full_name="Bob", email="bob@example.com", hashed_password="pw", role="Procurement Manager")
    db.add_all([u1, u2])
    db.commit()
    
    msg1 = Message(
        sender_id=u1.id,
        receiver_id=u2.id,
        content="Hello Bob, please review the contract.",
        related_entity_type=RelatedEntityType.CONTRACT,
        related_entity_id=101,
        is_read=False,
    )
    db.add(msg1)
    db.commit()
    db.refresh(msg1)
    
    assert msg1.id is not None
    assert msg1.sender_id == u1.id
    assert msg1.receiver_id == u2.id
    assert msg1.content == "Hello Bob, please review the contract."
    assert msg1.related_entity_type == RelatedEntityType.CONTRACT
    assert msg1.related_entity_id == 101
    assert msg1.is_read is False
    assert isinstance(msg1.created_at, datetime)
    assert msg1.read_at is None

    # Test conversation query using (receiver_id, is_read, created_at) index path
    unread = (
        db.query(Message)
        .filter(Message.receiver_id == u2.id, Message.is_read == False)
        .order_by(Message.created_at.desc())
        .all()
    )
    assert len(unread) == 1
    assert unread[0].id == msg1.id


def test_existing_communication_and_discussion_models_intact(in_memory_db):
    db, engine = in_memory_db
    inspector = inspect(engine)
    
    assert "communications" in inspector.get_table_names()
    assert "discussions" in inspector.get_table_names()
    
    u1 = User(full_name="Admin", email="admin_test@example.com", hashed_password="pw")
    db.add(u1)
    db.commit()
    
    comm = Communication(sender_id=u1.id, message="Legacy comm message")
    disc = Discussion(title="Legacy Discussion", created_by_id=u1.id)
    db.add_all([comm, disc])
    db.commit()
    
    assert comm.id is not None
    assert disc.id is not None


def test_demo_seed_messages(in_memory_db):
    db, _ = in_memory_db
    u1 = User(full_name="Admin", email="admin@vendoriq.com", hashed_password="pw")
    u2 = User(full_name="PM", email="pm.manager@vendoriq.com", hashed_password="pw")
    u3 = User(full_name="Vendor", email="vendor.contact@samplesupplies.com", hashed_password="pw")
    db.add_all([u1, u2, u3])
    db.commit()

    demo_msgs = [
        Message(sender_id=u1.id, receiver_id=u2.id, content="Check PR", related_entity_type=RelatedEntityType.PROCUREMENT_REQUEST, related_entity_id=1),
        Message(sender_id=u2.id, receiver_id=u3.id, content="Check PO", related_entity_type=RelatedEntityType.PURCHASE_ORDER, related_entity_id=2),
        Message(sender_id=u3.id, receiver_id=u2.id, content="PO update", related_entity_type=RelatedEntityType.PURCHASE_ORDER, related_entity_id=2),
        Message(sender_id=u1.id, receiver_id=u3.id, content="Contract ISO", related_entity_type=RelatedEntityType.CONTRACT, related_entity_id=3),
        Message(sender_id=u3.id, receiver_id=u1.id, content="Vendor doc", related_entity_type=RelatedEntityType.VENDOR, related_entity_id=4),
        Message(sender_id=u2.id, receiver_id=u1.id, content="General chat", related_entity_type=RelatedEntityType.NONE, related_entity_id=None),
    ]
    db.add_all(demo_msgs)
    db.commit()

    assert db.query(Message).count() == 6
    types = {m.related_entity_type for m in db.query(Message).all()}
    assert types == {
        RelatedEntityType.PROCUREMENT_REQUEST,
        RelatedEntityType.PURCHASE_ORDER,
        RelatedEntityType.CONTRACT,
        RelatedEntityType.VENDOR,
        RelatedEntityType.NONE,
    }

