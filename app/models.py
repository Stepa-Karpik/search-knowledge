from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class SearchDocumentModel(Base):
    __tablename__ = "search_documents"

    document_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    owner_subject_id: Mapped[str] = mapped_column(String(128), index=True)
    text: Mapped[str] = mapped_column(Text)


class EntityModel(Base):
    __tablename__ = "entities"
    __table_args__ = (
        UniqueConstraint("owner_subject_id", "kind", "normalized_name", name="uq_entity_identity"),
    )

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    owner_subject_id: Mapped[str] = mapped_column(String(128), index=True)
    kind: Mapped[str] = mapped_column(String(64), index=True)
    name: Mapped[str] = mapped_column(String(255))
    normalized_name: Mapped[str] = mapped_column(String(255))


class DocumentEntityLinkModel(Base):
    __tablename__ = "document_entity_links"
    __table_args__ = (
        UniqueConstraint("document_id", "entity_id", name="uq_document_entity_link"),
    )

    id: Mapped[str] = mapped_column(String(192), primary_key=True)
    owner_subject_id: Mapped[str] = mapped_column(String(128), index=True)
    document_id: Mapped[str] = mapped_column(String(64), index=True)
    entity_id: Mapped[str] = mapped_column(ForeignKey("entities.id"), index=True)
