from dataclasses import asdict
from typing import Annotated
from fastapi import Depends,FastAPI,status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db import get_session
from app.repositories import SearchRepository
app=FastAPI(title='search-knowledge'); SessionDep=Annotated[Session,Depends(get_session)]
class IndexCreate(BaseModel): document_id:str; owner_subject_id:str; text:str
class EntityCreate(BaseModel): kind:str; name:str
class EntityIndexCreate(BaseModel): document_id:str; owner_subject_id:str; entities:list[EntityCreate]
@app.get('/healthz')
def healthz(): return {'status':'ok','service':'search-knowledge'}
@app.post('/api/v1/index',status_code=status.HTTP_201_CREATED)
def index_document(payload:IndexCreate,session:SessionDep):
    doc=SearchRepository(session).index_document(**payload.model_dump()); return {'document_id':doc.document_id,'owner_subject_id':doc.owner_subject_id,'text':doc.text}
@app.get('/api/v1/search')
def search(owner_subject_id:str,q:str,session:SessionDep): return [asdict(hit) for hit in SearchRepository(session).search(owner_subject_id=owner_subject_id,query=q)]
@app.post('/api/v1/entities/index',status_code=status.HTTP_201_CREATED)
def index_entities(payload:EntityIndexCreate,session:SessionDep):
    entities=SearchRepository(session).index_entities(
        document_id=payload.document_id,
        owner_subject_id=payload.owner_subject_id,
        entities=[entity.model_dump() for entity in payload.entities],
    )
    return [{'kind':entity.kind,'name':entity.name} for entity in entities]
@app.get('/api/v1/groups')
def groups(owner_subject_id:str,session:SessionDep): return SearchRepository(session).list_groups(owner_subject_id=owner_subject_id)
