from dataclasses import dataclass
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import SearchDocumentModel
@dataclass(slots=True)
class SearchHit: document_id:str; score:int
class SearchRepository:
    def __init__(self,session:Session): self.session=session
    def index_document(self,*,document_id:str,owner_subject_id:str,text:str):
        doc=self.session.get(SearchDocumentModel,document_id) or SearchDocumentModel(document_id=document_id,owner_subject_id=owner_subject_id,text=text)
        doc.owner_subject_id=owner_subject_id; doc.text=text; self.session.add(doc); self.session.commit(); return doc
    def search(self,*,owner_subject_id:str,query:str):
        tokens=set(query.lower().split()); hits=[]
        for doc in self.session.scalars(select(SearchDocumentModel).where(SearchDocumentModel.owner_subject_id==owner_subject_id)).all():
            score=len(tokens & set(doc.text.lower().split()))
            if score: hits.append(SearchHit(doc.document_id,score))
        return sorted(hits,key=lambda h:h.score,reverse=True)
