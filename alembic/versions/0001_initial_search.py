from alembic import op
import sqlalchemy as sa
revision='0001_initial_search'; down_revision=None; branch_labels=None; depends_on=None
def upgrade():
 op.create_table('search_documents',sa.Column('document_id',sa.String(64),primary_key=True),sa.Column('owner_subject_id',sa.String(128),nullable=False),sa.Column('text',sa.Text(),nullable=False)); op.create_index('ix_search_documents_owner_subject_id','search_documents',['owner_subject_id'])
def downgrade(): op.drop_index('ix_search_documents_owner_subject_id',table_name='search_documents'); op.drop_table('search_documents')
