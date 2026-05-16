from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.models import Base
from app.repositories import SearchRepository

def test_index_persists_and_searches():
    engine=create_engine('sqlite+pysqlite:///:memory:'); Base.metadata.create_all(engine); repo=SearchRepository(Session(engine))
    repo.index_document(document_id='doc_1',owner_subject_id='usr_1',text='договор аренды депозит 2000 евро')
    assert repo.search(owner_subject_id='usr_1',query='депозит 2000 евро')[0].document_id=='doc_1'
