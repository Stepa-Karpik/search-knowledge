from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_indexed_document_can_be_found():
    client.post('/api/v1/index', json={'document_id': 'doc_1', 'owner_subject_id': 'usr_1', 'text': 'договор аренды депозит 2000 евро'})
    response = client.get('/api/v1/search', params={'owner_subject_id': 'usr_1', 'q': 'депозит 2000 евро'})
    assert response.status_code == 200
    assert response.json()[0]['document_id'] == 'doc_1'
