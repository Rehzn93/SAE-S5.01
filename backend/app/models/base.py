from datetime import datetime
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session
from sqlalchemy import create_engine
import os 

Base = declarative_base()

class BaseModelMixin:
    
    def __getitem__(self, item):
        if hasattr(self, item):
            return getattr(self, item)
        raise KeyError(f"L'objet '{self.__class__.__name__}' n'a pas l'attribut '{item}'")
    
    def to_dict(self):
        result = {}
        for col in self.__table__.columns:
            val = getattr(self, col.name)
            if isinstance(val, datetime):
                val = val.strftime("%Y-%m-%d %H:%M:%S")
            result[col.name] = val
        return result

def get_engine(db_uri=None):
    return create_engine(db_uri, echo=False)

