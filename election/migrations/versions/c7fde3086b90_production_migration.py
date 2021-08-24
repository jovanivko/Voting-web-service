"""Production migration

Revision ID: c7fde3086b90
Revises: 
Create Date: 2021-08-24 15:20:54.266428

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c7fde3086b90'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('elections',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('start', sa.DATETIME(), nullable=False),
    sa.Column('end', sa.DATETIME(), nullable=False),
    sa.Column('individual', sa.BOOLEAN(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('end'),
    sa.UniqueConstraint('start')
    )
    op.create_table('participants',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=256), nullable=False),
    sa.Column('individual', sa.BOOLEAN(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('electionparticipant',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('electionId', sa.Integer(), nullable=False),
    sa.Column('participantId', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['electionId'], ['elections.id'], ),
    sa.ForeignKeyConstraint(['participantId'], ['participants.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('invalidvotes',
    sa.Column('guid', sa.Integer(), nullable=False),
    sa.Column('electionId', sa.Integer(), nullable=False),
    sa.Column('pollNumber', sa.Integer(), nullable=False),
    sa.Column('officialsJmbg', sa.String(length=13), nullable=False),
    sa.Column('reason', sa.String(length=256), nullable=False),
    sa.ForeignKeyConstraint(['electionId'], ['elections.id'], ),
    sa.PrimaryKeyConstraint('guid')
    )
    op.create_table('votes',
    sa.Column('guid', sa.Integer(), nullable=False),
    sa.Column('electionId', sa.Integer(), nullable=False),
    sa.Column('pollNumber', sa.Integer(), nullable=False),
    sa.Column('officialsJmbg', sa.String(length=13), nullable=False),
    sa.ForeignKeyConstraint(['electionId'], ['elections.id'], ),
    sa.ForeignKeyConstraint(['pollNumber'], ['participants.id'], ),
    sa.PrimaryKeyConstraint('guid')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('votes')
    op.drop_table('invalidvotes')
    op.drop_table('electionparticipant')
    op.drop_table('participants')
    op.drop_table('elections')
    # ### end Alembic commands ###