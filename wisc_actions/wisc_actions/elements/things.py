from bson.objectid import ObjectId
from .properties import Property
from .base import WiscBase

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
        self.properties = []
        for property in properties:
            if isinstance(property,Property):
                self.properties.append(property)
            else:
                self.properties.append(Property.load(property))

    @property
    def serialized(self):
        return {'_id':str(self.id),'name':self.name,'properties':self.serialize(self.properties)}

    @classmethod
    def load(cls,serialized):
        return Thing(**serialized)
