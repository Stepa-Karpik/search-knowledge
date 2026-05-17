from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_entities_can_be_indexed_and_read_back_as_groups():
    response = client.post(
        "/api/v1/entities/index",
        json={
            "document_id": "doc_api_1",
            "owner_subject_id": "usr_api_1",
            "entities": [{"kind": "company", "name": "Acme"}],
        },
    )
    assert response.status_code == 201

    groups = client.get("/api/v1/groups", params={"owner_subject_id": "usr_api_1"})
    assert groups.status_code == 200
    assert groups.json() == [
        {"kind": "company", "title": "Компании", "items": [{"name": "Acme", "document_count": 1}]}
    ]
