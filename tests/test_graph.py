from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.models import Base
from app.repositories import SearchRepository


def make_repo() -> SearchRepository:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    return SearchRepository(Session(engine))


def test_index_entities_reuses_same_entity_and_links_multiple_documents():
    repo = make_repo()

    repo.index_entities(
        document_id="doc_1",
        owner_subject_id="usr_1",
        entities=[{"kind": "company", "name": "ООО Ромашка"}],
    )
    repo.index_entities(
        document_id="doc_2",
        owner_subject_id="usr_1",
        entities=[{"kind": "company", "name": "ооо ромашка"}],
    )

    entities = repo.list_entities(owner_subject_id="usr_1")
    assert len(entities) == 1
    assert entities[0].name == "ООО Ромашка"
    assert entities[0].document_count == 2


def test_list_groups_returns_entity_buckets_and_semantic_document_groups():
    repo = make_repo()

    repo.index_entities(
        document_id="doc_1",
        owner_subject_id="usr_1",
        entities=[
            {"kind": "company", "name": "ООО Ромашка"},
            {"kind": "person", "name": "Иван Петров"},
            {"kind": "topic", "name": "финансы"},
        ],
    )

    groups = repo.list_groups(owner_subject_id="usr_1")
    assert groups == [
        {"kind": "company", "title": "Компании", "items": [{"name": "ООО Ромашка", "document_count": 1}]},
        {"kind": "person", "title": "Люди", "items": [{"name": "Иван Петров", "document_count": 1}]},
        {"kind": "topic", "title": "AI-группы", "items": [{"name": "финансы", "document_count": 1}]},
    ]


def test_index_entities_replaces_stale_links_and_merges_person_roles():
    repo = make_repo()

    repo.index_entities(
        document_id='doc_1',
        owner_subject_id='usr_1',
        entities=[
            {'kind': 'person', 'name': 'Арендатор Карпов Степан'},
            {'kind': 'person', 'name': 'Карпов Степан Викторович'},
            {'kind': 'person', 'name': 'Ср Маржа Минимальная'},
            {'kind': 'city', 'name': 'Ростов-на-Дону'},
        ],
    )
    repo.index_entities(
        document_id='doc_1',
        owner_subject_id='usr_1',
        entities=[{'kind': 'person', 'name': 'Карпов Степан Викторович'}],
    )

    people = repo.list_entities(owner_subject_id='usr_1', kind='person')
    cities = repo.list_entities(owner_subject_id='usr_1', kind='city')

    assert people == [type(people[0])(kind='person', name='Карпов Степан Викторович', document_count=1)]
    assert cities == []
