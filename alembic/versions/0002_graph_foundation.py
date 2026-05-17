from alembic import op
import sqlalchemy as sa

revision = "0002_graph_foundation"
down_revision = "0001_initial_search"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "entities",
        sa.Column("id", sa.String(128), primary_key=True),
        sa.Column("owner_subject_id", sa.String(128), nullable=False),
        sa.Column("kind", sa.String(64), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("normalized_name", sa.String(255), nullable=False),
        sa.UniqueConstraint("owner_subject_id", "kind", "normalized_name", name="uq_entity_identity"),
    )
    op.create_index("ix_entities_owner_subject_id", "entities", ["owner_subject_id"])
    op.create_index("ix_entities_kind", "entities", ["kind"])
    op.create_table(
        "document_entity_links",
        sa.Column("id", sa.String(192), primary_key=True),
        sa.Column("owner_subject_id", sa.String(128), nullable=False),
        sa.Column("document_id", sa.String(64), nullable=False),
        sa.Column("entity_id", sa.String(128), sa.ForeignKey("entities.id"), nullable=False),
        sa.UniqueConstraint("document_id", "entity_id", name="uq_document_entity_link"),
    )
    op.create_index("ix_document_entity_links_owner_subject_id", "document_entity_links", ["owner_subject_id"])
    op.create_index("ix_document_entity_links_document_id", "document_entity_links", ["document_id"])
    op.create_index("ix_document_entity_links_entity_id", "document_entity_links", ["entity_id"])


def downgrade():
    op.drop_index("ix_document_entity_links_entity_id", table_name="document_entity_links")
    op.drop_index("ix_document_entity_links_document_id", table_name="document_entity_links")
    op.drop_index("ix_document_entity_links_owner_subject_id", table_name="document_entity_links")
    op.drop_table("document_entity_links")
    op.drop_index("ix_entities_kind", table_name="entities")
    op.drop_index("ix_entities_owner_subject_id", table_name="entities")
    op.drop_table("entities")
