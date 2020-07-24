from .base import WiscBase
from .parse import parse
from .structures import *
from .things import Thing


class Definition(WiscBase):
    '''
    Specification for defining a value in the namespace of an action.
    '''
    def __init__(self,name):
        self.name = name

    @property
    def serialized(self):
        return {'name':self.name}

    @classmethod
    def load(self,serialized):
        return Definition(serialized['name'])

    def get(self,namespace): # State?
        pass

    def set(self,namespace,value): # State?
        pass

class LiteralDefinition(WiscBase):
    '''
    Specification for defining a literal value in the namespace of an action.
    This is essentially equivalent to:
        y = 2
    '''

    keys = [set(('name','value'))]

    def __init__(self,name,value):
        super(LiteralDefinition,self).__init__(name)
        self.value = value

    @property
    def serialized(self):
        serialized = super(LiteralDefinition,self).serialized
        serialized.update({'value':self.serialize(self.value)})

    @classmethod
    def load(self,serialized):
        value = parse([Thing,Position,Orientation,Pose],serialized)
        return LiteralDefinition(name=serialized['name'],value=value)

class PropertyDefinition(WiscBase):
    '''
    Specification for defining a value via a thing's property in the namespace of an action.
    This is essentially equivalent to:
        is_num = isinstance(2,Int)
    Or:
        position = pose.position
    '''

    keys = [set(('name','item','property'))]

    def __init__(self,name,item,property,fallback=None):
        super(PropertyDefinition,self).__init__(name)
        self.item = item
        self.property = property
        self.fallback = fallback

    @property
    def serialized(self):
        serialized = super(LiteralDefinition,self).serialized
        serialized.update({'item':self.item,
                           'property':self.property,
                           'fallback':self.serialize(self.fallback)})


class IndexDefinition(WiscBase):
    '''
    Specification for defining a value via an object's index in the namespace of an action.
    This is essentially equivalent to:
        pose = trajectory[2]
    '''

    keys = [set(('name','item','index'))]

    def __init__(self,name,item,index,fallback):
        super(PropertyDefinition,self).__init__(name)
        self.item = item
        self.index = index
        self.fallback = fallback

    @property
    def serialized(self):
        serialized = super(LiteralDefinition,self).serialized
        serialized.update({'item':self.item,
                           'index':self.index,
                           'fallback':self.serialize(self.fallback)})
