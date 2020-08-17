from bson.objectid import ObjectId
from .base import WiscBase
from .parse import parse
from .structures import Position, Orientation, Pose
from typing import Any

# class Literal(WiscBase):
#     '''
#     Wrapper for specifying literal values.
#     '''
#     keys = []
#
#     def __init__(self,value=None):
#         self.value = value
#
#     def serialized(self):
#         return self.value
#
#     def load(self,serialized):
#         return Literal(serialized)

class Reference(WiscBase):
    '''
    Wrapper for handling references to things in the space
    '''
    keys = []

    def __init__(self,name="ref"):
        self.name = name

    def serialized(self):
        return self.name

    def load(self,serialized):
        return Reference(serialized)


class Property(WiscBase):
    '''
    A generic container for specifying object properties.
    '''

    keys = [set(('name','value'))]

    def __init__(self,name='property',value=None):
        self.name = name
        self.value = value

    @property
    def serialized(self):
        return {'name':self.name,'value':self.serialize(self.value)}

    @classmethod
    def load(self,serialized):
        # Parse value. If it isn't one of these things, just use the serialized value.
        value = parse([Thing,Position,Orientation,Pose],serialized)
        return Property(name=serialized['name'],value=value)

class Thing(WiscBase):
    '''
    Takes 3 Parameters:
        - _id (optional): The unique ID of the thing. If not specified, a new one is created.
        - name (required): A name for the thing.
        - properties (required): a sequence of Property objects or serialized properties.
    '''

    keys = [set(('name','properties'))]

    def __init__(self,name,properties,_id=None):
        self.id = ObjectId(_id)
        self.name = name
        self.properties = properties

    @property
    def serialized(self):
        return {'_id':str(self.id),'name':self.name,'properties':self.serialize(self.properties)}

    @classmethod
    def load(cls,serialized):
        return Thing(_id=serialized['_id'] if '_id' in serialized.keys() else None,
                     name=serialized['name'],
                     properties=[Property.load(content) for content in serialized['properties']])

    def add_property(self,property:Property):
        self.properties.append(property)

    def create_property(self,name:str,value:Any) -> Property:
        property = Property(name,value)
        self.add_property(property)
        return property
