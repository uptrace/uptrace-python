
from opentelemetry import trace
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.trace import TracerProvider

from sqlalchemy import create_engine, Column, Integer, String, Sequence
from exts import db

class User(db.Model):
    __tablename__ = 'users'

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    name = Column(String)
    username = Column(String)

    def __repr__(self):
        return "<User(id='%s' name='%s', username='%s')>" % (self.id, self.name, self.username)
