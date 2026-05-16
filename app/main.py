from dataclasses import asdict
from typing import Annotated
from fastapi import Depends,FastAPI,status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db import get_session
from app.repositories import SearchRepository
app=FastAPI(title='search-knowledge'); SessionDep=Annotated[Session,Depends(get_session)]
class IndexCreate(BaseModel): document_id:str; owner_subject_id:str; text:str
@app.get('/healthz')
def healthz(): return {'status':'ok','service':'search-knowledge'}
@app.post('/api/v1/index',status_code=status.HTTP_201_CREATED)
def index_document(payload:IndexCreate,session:SessionDep):
    doc=SearchRepository(session).index_document(**payload.model_dump()); return {'document_id':doc.document_id,'owner_subject_id':doc.owner_subject_id,'text':doc.text}
@app.get('/api/v1/search')
def search(owner_subject_id:str,q:str,session:SessionDep): return [asdict(hit) for hit in SearchRepository(session).search(owner_subject_id=owner_subject_id,query=q)]
