from bson.objectid import ObjectId
from .base import WiscBase
from .properties import Property

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
