from abc import ABC, abstractmethod

class WiscBase(ABC):

    keys = [set()] # Empty Set

    @property
    @abstractmethod
    def serialized(self):
        return {}

    @classmethod
    @abstractmethod
    def load(cls,serialized):
        return WiscBase()

    @classmethod
    def serialize(cls,item):
        # Try running the serialize method:
        if isinstance(item,WiscBase):
            return item.serialized

        # If it a list, enumerate the entries
        if isinstance(item,list):
            return [cls.serialize(i) for i in item]
        # If it a dict, enumerate the entries
        if isinstance(item,dict):
            return {k:cls.serialize(v) for k,v in item.items()}
        # If it a basic type, return it
        if isinstance(item,int) or isinstance(item,float) or isinstance(item,str):
            return item

        # Serialization method not found.
        warnings.warn('Serialization not found for item of type {0}. Returning "None"'.format(type(item)),Warning)

        return None
