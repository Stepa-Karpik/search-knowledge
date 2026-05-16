from collections.abc import Generator
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import Session,sessionmaker
from app.models import Base
DATABASE_URL=os.getenv('SEARCH_DATABASE_URL','sqlite+pysqlite:///./search.db'); engine=create_engine(DATABASE_URL); SessionLocal=sessionmaker(engine)
if DATABASE_URL.startswith('sqlite'): Base.metadata.create_all(engine)
def get_session()->Generator[Session,None,None]:
    with SessionLocal() as session: yield session
