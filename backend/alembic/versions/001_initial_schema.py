"""Initial schema with pgvector support

Revision ID: 001
Revises:
Create Date: 2026-02-02

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')

    # Create lectures table
    op.create_table(
        'lectures',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('module_code', sa.String(20), nullable=False, index=True),
        sa.Column('week_number', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('filename', sa.String(255), nullable=False),
        sa.Column('upload_date', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('num_pages', sa.Integer(), nullable=True),
    )

    # Create chunks table with vector embedding
    op.create_table(
        'chunks',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('lecture_id', UUID(as_uuid=True), sa.ForeignKey('lectures.id', ondelete='CASCADE'), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('slide_number', sa.Integer(), nullable=False),
        sa.Column('embedding', Vector(384), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Create index on lecture_id for faster joins
    op.create_index('idx_chunks_lecture_id', 'chunks', ['lecture_id'])

    # Create HNSW index for vector similarity search (cosine distance)
    op.execute(
        'CREATE INDEX idx_chunks_embedding_hnsw ON chunks USING hnsw (embedding vector_cosine_ops)'
    )

    # Create topics table
    op.create_table(
        'topics',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('module_code', sa.String(20), nullable=False, index=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Create topic_appearances table
    op.create_table(
        'topic_appearances',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('topic_id', UUID(as_uuid=True), sa.ForeignKey('topics.id', ondelete='CASCADE'), nullable=False),
        sa.Column('lecture_id', UUID(as_uuid=True), sa.ForeignKey('lectures.id', ondelete='CASCADE'), nullable=False),
        sa.Column('frequency', sa.Integer(), default=1),
        sa.Column('first_slide', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Create indexes for faster queries
    op.create_index('idx_topic_appearances_topic_id', 'topic_appearances', ['topic_id'])
    op.create_index('idx_topic_appearances_lecture_id', 'topic_appearances', ['lecture_id'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('topic_appearances')
    op.drop_table('topics')
    op.drop_table('chunks')
    op.drop_table('lectures')

    # Drop pgvector extension (optional - may affect other tables)
    # op.execute('DROP EXTENSION IF EXISTS vector')
