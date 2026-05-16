from sqlalchemy import String,Text
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column
class Base(DeclarativeBase): pass
class SearchDocumentModel(Base):
    __tablename__='search_documents'
    document_id:Mapped[str]=mapped_column(String(64),primary_key=True)
    owner_subject_id:Mapped[str]=mapped_column(String(128),index=True)
    text:Mapped[str]=mapped_column(Text)
