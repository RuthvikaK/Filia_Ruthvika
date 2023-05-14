import pytest
from app import app, db, bcrypt
from app.models import FiliaUser
from flask import url_for

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            # Create test db and add a test user
            db.create_all()
            hashed_password = bcrypt.generate_password_hash('testpassword').decode()
            user = FiliaUser(username='testuser', email='test@example.com', password=hashed_password)
            db.session.add(user)
            db.session.commit()
        yield client
    # Teardown after test
    db.session.remove()
    db.drop_all()

def test_reset_password(client):
    # Access reset password page
    res = client.get('/reset_password_page')
    assert res.status_code == 200

    # Test reset password with non-existent user
    res = client.post('/reset_password', data={
        'email_or_username': 'nonexistent',
        'password': 'newpassword',
        'confirmPassword': 'newpassword'
    }, follow_redirects=True)
    assert res.status_code == 400
    assert b'User not found.' in res.data

    # Test reset password with non-matching passwords
    res = client.post('/reset_password', data={
        'email_or_username': 'testuser',
        'password': 'newpassword',
        'confirmPassword': 'differentpassword'
    }, follow_redirects=True)
    assert res.status_code == 400
    assert b'The passwords do not match.' in res.data

    # Reset password for the test user
    res = client.post('/reset_password', data={
        'email_or_username': 'testuser',
        'password': 'newpassword',
        'confirmPassword': 'newpassword'
    }, follow_redirects=True)

    assert res.status_code == 200
    assert b'Password Reset Successful' in res.data

    # Test login with old password (should fail)
    res = client.post('/login', data={
        'username': 'testuser',
        'password': 'testpassword'
    }, follow_redirects=True)
    assert res.status_code == 401  # Assuming a 401 Unauthorized status code on failed login

    # Test login with new password (should succeed)
    res = client.post('/login', data={
        'username': 'testuser',
        'password': 'newpassword'
    }, follow_redirects=True)

    assert res.status_code == 200
    
