import pytest
from app import app
from src.models import db, FiliaUser, PhotoPost

@pytest.fixture(scope = 'module')
def test_client():
    with app.app_context():
        PhotoPost.query.delete()
        db.session.commit()
        yield app.test_client()