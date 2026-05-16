from fastapi import FastAPI, status
from pydantic import BaseModel

app = FastAPI(title="search-knowledge")
index: list[dict[str, str]] = []
class IndexCreate(BaseModel):
    document_id: str
    owner_subject_id: str
    text: str
@app.get('/healthz')
def healthz(): return {'status': 'ok', 'service': 'search-knowledge'}
@app.post('/api/v1/index', status_code=status.HTTP_201_CREATED)
def index_document(payload: IndexCreate):
    index.append(payload.model_dump())
    return payload.model_dump()
@app.get('/api/v1/search')
def search(owner_subject_id: str, q: str):
    tokens = set(q.lower().split())
    hits = []
    for item in index:
        if item['owner_subject_id'] != owner_subject_id:
            continue
        score = len(tokens & set(item['text'].lower().split()))
        if score:
            hits.append({'document_id': item['document_id'], 'score': score})
    return sorted(hits, key=lambda x: x['score'], reverse=True)
