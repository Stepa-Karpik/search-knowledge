from dataclasses import dataclass

import re

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.models import DocumentEntityLinkModel, EntityModel, SearchDocumentModel


GROUP_TITLES = {
    "company": "Компании",
    "person": "Люди",
    "project": "Проекты",
    "finance": "Финансы",
    "city": "Города",
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
        self.session.execute(
            delete(DocumentEntityLinkModel).where(
                DocumentEntityLinkModel.document_id == document_id,
                DocumentEntityLinkModel.owner_subject_id == owner_subject_id,
            )
        )
        indexed_entities: list[EntityModel] = []
        for item in entities:
            kind = item["kind"].strip().lower()
            name = self._normalize_display_name(kind, item["name"].strip())
            if not name:
                continue
            normalized_name = self._normalize_name(name, kind=kind)
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
            elif kind == "person" and len(name.split()) > len(entity.name.split()):
                entity.name = name

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
    def _normalize_display_name(kind: str, name: str) -> str | None:
        name = " ".join(name.strip().split())
        if not name:
            return None
        if kind == "person":
            name = re.sub(
                r"^(?:арендатор|арендодатель|заказчик|исполнитель|покупатель|продавец|студент|преподаватель|директор|представитель|гражданин|гражданка)\s+",
                "",
                name,
                flags=re.IGNORECASE,
            ).strip()
            parts = name.split()
            stopwords = {"ср", "средняя", "маржа", "минимальная", "максимальная", "пакет", "бонус", "срок", "вариант"}
            if len(parts) < 2 or len(parts) > 3:
                return None
            if {part.lower() for part in parts} & stopwords:
                return None
            if any(not re.fullmatch(r"[А-ЯЁ][а-яё]{2,}", part) for part in parts):
                return None
        return name

    @staticmethod
    def _normalize_name(name: str, *, kind: str | None = None) -> str:
        parts = " ".join(name.lower().split()).split()
        if kind == "person" and len(parts) >= 2:
            return " ".join(parts[:2])
        return " ".join(parts)
