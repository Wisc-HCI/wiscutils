from abc import ABC, abstractmethod
from bson.objectid import ObjectId
import warnings
import pprint

class WiscBase(ABC):

    keys = [set()] # Empty Set

    @property
    @abstractmethod
    def serialized(self):
        return {}

    @classmethod
    @abstractmethod
    def load(cls, serialized: dict, context: list):
        return WiscBase()

    @classmethod
    def serialize(cls,item):
        # Try running the serialize method:
        if isinstance(item,WiscBase):
            return item.serialized

        # If it is an ObjectId, return the string version
        if isinstance(item,ObjectId):
            return str(item)
        # If it a list, enumerate the entries
        if isinstance(item,list):
            return [cls.serialize(i) for i in item]
        # If it a dict, enumerate the entries
        if isinstance(item,dict):
            return {k:cls.serialize(v) for k,v in item.items()}
        # If it a basic type, return it
        if isinstance(item,(int,float,str)) or item == None:
            return item

        # Serialization method not found.
        warnings.warn('Serialization not found for item of type {0}. Returning "None"'.format(type(item)),Warning)

        return None

    @classmethod
    def parse(classes, serialized: dict, context: list):
        if isinstance(serialized,list):
            return [WiscBase.parse(classes,content,context) for conent in serialized]
        elif isinstance(serialized,int) or isinstance(serialized,float) or isinstance(serialized,str) or serialized == None:
            return serialized
        elif isinstance(serialized,dict):
            for cls in classes:
                for keyset in cls.keys:
                    if keyset == set(serialized.keys()):
                        return cls.load(serialized,context)
        return serialized

    def __repr__(self):
        return pprint.pformat(self.serialized)
