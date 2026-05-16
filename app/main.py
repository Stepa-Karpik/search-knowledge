from fastapi import FastAPI

app = FastAPI(title="search-knowledge")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok", "service": "search-knowledge"}
