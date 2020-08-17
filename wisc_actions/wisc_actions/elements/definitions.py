from .base import WiscBase
from .parse import parse
from .things import Thing
from .math import Math
from .structures import Position, Orientation, Pose

class AttributeWrapper(WiscBase):
    '''
    Wrapper for containing non-WiscBase items.
    '''
    def __init__(self,obj,property,lookup_type='property'):
        self.obj = obj
        self.property = property
        self.lookup_type = lookup_type

    def get(self):
        if self.lookup_type == 'property':
            getattr(self.obj, self.property)
        if self.lookup_type == 'dictionary':
            self.obj[self.property]

    def set(self,value):
        if self.lookup_type == 'property':
            setattr(self.obj,self.property,value)
        elif self.lookup_type == 'dictionary':
            self.obj[self.property] = value

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


    @abstractmethod
    def get(self,context): # State?
        pass


class LiteralDefinition(Definition):
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
        return serialized

    @classmethod
    def load(self,serialized):
        value = parse([Thing,Position,Orientation,Pose],serialized)
        return LiteralDefinition(name=serialized['name'],value=value)

    def get(self,context): # State?
        return self.value


class PropertyDefinition(Definition):
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
        serialized = super(PropertyDefinition,self).serialized
        serialized.update({'item':self.item,
                           'property':self.property,
                           'fallback':self.serialize(self.fallback)})
        return serialized

    @classmethod
    def load(self,serialized):
        fallback = serialized['fallback'] if 'fallback' in serialized.keys() else None
        return PropertyDefinition(name=serialized['name'],
                                  item=serialized['item'],
                                  property=serialized['property'],
                                  fallback=parse([Thing,Position,Orientation,Pose],fallback))

    @abstractmethod
    def get(self,context):
        # Item is the reference to the object, or the id in state
        obj = context.get(self.item)

        # Three cases:
        # Property Class of Thing (e.g. is_ball(obj))
        if isinstance(Thing,obj):
            for property in obj.properties:
                if property.name == self.property:
                    return property

        # Key in Dictionary (e.g obj['ball'])
        elif isinstance(Dict, obj):
            # Might have to change this:
            return AttributeWrapper(obj,self.property,lookup_type='dictionary')

        # Python Attribute of Thing (e.g. obj.ball)
        elif isinstance(WiscBase,obj):
            # Might have to change this:
            attr = getattr(obj, self.property)
            if not isinstance(WiscBase,attr):
                return AttributeWrapper(obj,self.property,lookup_type='property')
            return attr

        return self.fallback


class IndexDefinition(Definition):
    '''
    Specification for defining a value via an object's index in the namespace of an action.
    This is essentially equivalent to:
        box = boxes[0]
    '''

    keys = [set(('name','item','index'))]

    def __init__(self,name,item,index,fallback):
        super(IndexDefinition,self).__init__(name)
        self.item = item
        self.index = index
        self.fallback = fallback

    @property
    def serialized(self):
        serialized = super(IndexDefinition,self).serialized
        serialized.update({'item':self.item,
                           'index':self.index,
                           'fallback':self.serialize(self.fallback)})
        return serialized

    @classmethod
    def load(self,serialized):
        return IndexDefinition(name=serialized['name'],
                               item=serialized['item'],
                               property=serialized['index'])

    @abstractmethod
    def get(self,context):
        # Returns an item in a WiscBase Enumerable
        pass

class DescriptionDefinition(Definition):
    '''
    Specification for defining a set of things based on descriptions.
    This is essentially equivalent to:
        boxes = [object for object in objects if object.is_box]
    '''

    keys = [set(('name','descriptions'))]

    def __init__(self,name,description):
        super(DescriptionDefinition,self).__init__(name)
        self.descriptions = descriptions

    @property
    def serialized(self):
        serialized = super(DescriptionDefinition,self).serialized
        serialized.update({'descriptions':[description.serialized for descriptions in self.descriptions]})
        return serialized

    @classmethod
    def load(self,serialized):
        return DescriptionDefinition(name=serialized['name'],
                                     descriptions=[Description.load(content) for content in serialized['descriptions']])

    @abstractmethod
    def get(self,context):
        # Returns a WiscBase Enumerable
        pass

class MathDefinition(Definition):
    '''
    Specification for defining a set of things based on math operations.
    This is essentially equivalent to:
        a = b + c
    '''

    keys = [set(('name','math'))]

    def __init__(self,name:str,math:Math):
        super(MathDefinition,self).__init__(name)
        self.math = math

    @property
    def serialized(self):
        serialized = super(MathDefinition,self).serialized
        serialized.update({'math':self.math.serialized})
        return serialized

    @classmethod
    def load(self,serialized):
        return MathDefinition(name=serialized['name'],
                              math=Math.load(serialized['math']))

    @abstractmethod
    def get(self,context):
        # Returns a WiscBase Enumerable
        pass
