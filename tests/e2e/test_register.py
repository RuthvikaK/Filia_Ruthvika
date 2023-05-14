from app import app
import pytest
from src.models import FiliaUser

def test_register(client):
    # define test data
    test_user = {
        'firstname': 'John',
        'lastname': 'Doe',
        'email': 'johndoe@example.com',
        'phone': '1234567890',
        'gender': 'Male',
        'major': 'Computer Science',
        'gradDate': '2023-05-31',
        'bio': 'I am a computer science student.',
        'username': 'johndoe',
        'password': 'password',
        'profile_path': (BytesIO(b'my file contents'), 'FiliaLogo.jpg')
    }

    # send a post request to the register route
    response = client.post('/register', data=test_user, follow_redirects=True)

    # check that the response status code is 200 OK
    assert response.status_code == 200

    # check that the new user was added to the database
    assert db.session.query(FiliaUser).filter_by(username='johndoe').first() is not None

    # check that the user is redirected to the home page
    assert b'Welcome to Filia' in response.data
