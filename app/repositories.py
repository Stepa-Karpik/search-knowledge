from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import DocumentEntityLinkModel, EntityModel, SearchDocumentModel


GROUP_TITLES = {
    "company": "Компании",
    "person": "Люди",
    "project": "Проекты",
    "topic": "AI-группы",
}


@dataclass(slots=True)
class SearchHit:
    document_id: str
    score: int


@dataclass(slots=True)
class EntitySummary:
    kind: str
    name: str
    document_count: int


class SearchRepository:
    def __init__(self, session: Session):
        self.session = session

    def index_document(self, *, document_id: str, owner_subject_id: str, text: str):
        doc = self.session.get(SearchDocumentModel, document_id) or SearchDocumentModel(
            document_id=document_id,
            owner_subject_id=owner_subject_id,
            text=text,
        )
        doc.owner_subject_id = owner_subject_id
        doc.text = text
        self.session.add(doc)
        self.session.commit()
        return doc

    def search(self, *, owner_subject_id: str, query: str):
        tokens = set(query.lower().split())
        hits = []
        for doc in self.session.scalars(
            select(SearchDocumentModel).where(SearchDocumentModel.owner_subject_id == owner_subject_id)
        ).all():
            score = len(tokens & set(doc.text.lower().split()))
            if score:
                hits.append(SearchHit(doc.document_id, score))
        return sorted(hits, key=lambda hit: hit.score, reverse=True)

    def index_entities(self, *, document_id: str, owner_subject_id: str, entities: list[dict[str, str]]) -> list[EntityModel]:
        indexed_entities: list[EntityModel] = []
        for item in entities:
            kind = item["kind"].strip().lower()
            name = item["name"].strip()
            normalized_name = self._normalize_name(name)
            entity_id = f"{owner_subject_id}:{kind}:{normalized_name}"
            entity = self.session.get(EntityModel, entity_id)
            if entity is None:
                entity = EntityModel(
                    id=entity_id,
                    owner_subject_id=owner_subject_id,
                    kind=kind,
                    name=name,
                    normalized_name=normalized_name,
                )
                self.session.add(entity)

            link_id = f"{document_id}:{entity_id}"
            if self.session.get(DocumentEntityLinkModel, link_id) is None:
                self.session.add(
                    DocumentEntityLinkModel(
                        id=link_id,
                        owner_subject_id=owner_subject_id,
                        document_id=document_id,
                        entity_id=entity_id,
                    )
                )
            indexed_entities.append(entity)

        self.session.commit()
        return indexed_entities

    def list_entities(self, *, owner_subject_id: str, kind: str | None = None) -> list[EntitySummary]:
        statement = (
            select(
                EntityModel.kind,
                EntityModel.name,
                func.count(DocumentEntityLinkModel.id).label("document_count"),
            )
            .join(DocumentEntityLinkModel, DocumentEntityLinkModel.entity_id == EntityModel.id)
            .where(EntityModel.owner_subject_id == owner_subject_id)
            .group_by(EntityModel.id)
            .order_by(EntityModel.kind, EntityModel.name)
        )
        if kind is not None:
            statement = statement.where(EntityModel.kind == kind)
        return [EntitySummary(kind=row.kind, name=row.name, document_count=row.document_count) for row in self.session.execute(statement)]

    def list_groups(self, *, owner_subject_id: str) -> list[dict]:
        grouped_entities: dict[str, list[dict]] = {}
        for entity in self.list_entities(owner_subject_id=owner_subject_id):
            grouped_entities.setdefault(entity.kind, []).append(
                {"name": entity.name, "document_count": entity.document_count}
            )
        return [
            {"kind": kind, "title": GROUP_TITLES.get(kind, kind.title()), "items": grouped_entities[kind]}
            for kind in GROUP_TITLES
            if kind in grouped_entities
        ]

    @staticmethod
    def _normalize_name(name: str) -> str:
        return " ".join(name.lower().split())
