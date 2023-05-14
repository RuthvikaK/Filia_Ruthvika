import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_search(client):
    # Test GET request to /search
    response = client.get('/search')
    assert response.status_code == 200
    assert b'Search' in response.data

    # Test POST request with a search query
    search_query = 'example query'
    response = client.post('/search', data={'search_query': search_query})
    assert response.status_code == 200
    assert search_query.encode() in response.data