from .base import WiscBase
from .structures import *
from .things import Thing
from .parse import parse

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
        value = parse([Thing,Positon,Orientation,Pose],serialized)
        return Property(name=serialized['name'],value=value)
