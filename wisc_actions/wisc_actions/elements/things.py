from bson.objectid import ObjectId
from .base import WiscBase
from .structures import Position, Orientation, Pose
from .operations import MathOperation, PropertyOperation
from .math import Math
from typing import Any, List, Dict


class Term(WiscBase):
    '''
    Wrapper for handling references to things in the space
    '''
    keys = []

    def __init__(self,name:str):
        self.name = name

    @property
    def serialized(self):
        return self.name

    def load(self,serialized):
        return Term(serialized)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def __add__(self,other):
        if isinstance(other,(Term,Math,int,float)):
            return Math(self,other,MathOperation.ADD)
        else:
            return None

    def __sub__(self,other):
        if isinstance(other,(Term,Math,int,float)):
            return Math(self,other,MathOperation.SUBTRACT)
        else:
            return None

    def __mul__(self,other):
        if isinstance(other,(Term,Math,int,float)):
            return Math(self,other,MathOperation.MULTIPLY)
        else:
            return None

    def __truediv__(self,other):
        if isinstance(other,(Term,Math,int,float)):
            return Math(self,other,MathOperation.DIVIDE)
        else:
            return None

    def __mod__(self,other):
        if isinstance(other,(Term,Math,int,float)):
            return Math(self,other,MathOperation.MODULUS)
        else:
            return None

    def __lt__(self,other):
        if isinstance(other,(Term,Math,int,float)):
            return Math(self,other,PropertyOperation.LESS_THAN)
        else:
            return None

    def __le__(self,other):
        if isinstance(other,(Term,Math,int,float)):
            return Math(self,other,PropertyOperation.LESS_THAN_OR_EQUALS)
        else:
            return None

    def __gt__(self,other):
        if isinstance(other,(Term,Math,int,float)):
            return Math(self,other,PropertyOperation.GREATER_THAN)
        else:
            return None

    def __ge__(self,other):
        if isinstance(other,(Term,Math,int,float)):
            return Math(self,other,PropertyOperation.GREATER_THAN_OR_EQUALS)
        else:
            return None

    def __eq__(self,other):
        if isinstance(other,(Term,Math,int,float)):
            return Math(self,other,PropertyOperation.EQUALS)
        else:
            return None

    def execute(self,plan,context):
        return context.get(self.name)


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
        value = WiscBase.parse([Thing,Position,Orientation,Pose],serialized)
        return Property(name=serialized['name'],value=value)

    def __eq__(self, other):
        return self.name == other.name and self.value == other.value

class Prototype(WiscBase):
    '''
    Takes 4 Parameters:
        - name (required): A name for the thing.
        - parents (required): A list of parent prototypes to inherit from.
        - properties (required): a sequence of Property objects or serialized properties.
    '''
    keys = [set(('name','properties','parents'))]

    def __init__(self,name:str,parents:List['Prototype'],properties:List[Property]):
        self.name = name
        self._parents = parents
        self._properties = properties

    @property
    def serialized(self):
        return {'name':self.name,'parents':[parent.name for parent in self.parents],'properties':self.serialize(self._properties)}

    @classmethod
    def load(cls,serialized,context):
        parents = []
        for parent_name in serialized['parents']:
            found = False
            for prototype in context:
                if prototype.name == parent_name:
                    parents.append(prototype)
                    found = True
            if not found:
                raise ImportError
        return Prototype(name=serialized['name'],
                         parents=parents,
                         properties=[Property.load(content,context) for content in serialized['properties']])

    @property
    def parents(self):
        parents = []
        for parent in self._parents:
            for parent_parent in parent.parents:
                if parent_parent not in parents:
                    parents.append(parent_parent)
        return parents

    @property
    def properties(self) -> List[Property]:
        properties = {}
        for parent in self.parents:
            for parent_property in parent.properties:
                properties[parent_property.name] = parent_property
        for property in self._properties:
            properties[property.name] = property
        return [property for name,property in properties.items()]

    def add_property(self,property:Property):
        self._properties.append(property)

    def has_property(self,property_name:str) -> bool:
        for property in self.properties:
            if property.name == property_name:
                return True
        return False

    def get_property(self,property_name:str):
        for property in self.properties:
            if property.name == property_name:
                return property

    def has_description(self,description:'Description') -> bool:
        if self.has_property(description.property.name):
            if description.operation == PropertyOperation.EXISTS:
                return self.has_property(description.property.name)
            prop = self.get_property(description.property.name)
            return description.operation.execute(prop.value,description.property.value)
        else:
            return False

    def create_property(self,name:str,value:Any) -> Property:
        property = Property(name,value)
        self.add_property(property)
        return property

    def create_thing(self,name:str,properties:list) -> 'Thing':
        thing = Thing(name,self,properties)
        return thing

    def create_prototype(self,name,properties:list) -> 'Prototype':
        prototype = Prototype(name,)


class Thing(Prototype):
    '''
    Takes 4 Parameters:
        - _id (optional): The unique ID of the thing. If not specified, a new one is created.
        - name (required): A name for the thing.
        - prototype (required): Thing Prototype.
        - properties (required): a sequence of Property objects or serialized properties.
    '''

    keys = [set(('name','properties','prototype'))]

    def __init__(self,name:str,prototype:Prototype,properties:List[Property],_id=None):
        super(Thing,self).__init__(self,name,[prototype],properties,_id)

    def create_thing(self,name:str,properties:list) -> 'Thing':
        raise NotImplementedError

    def create_prototype(self,name,properties:list) -> 'Prototype':
        raise NotImplementedError

    @property
    def prototype(self):
        return self.parents[0]

    @property
    def serialized(self):
        return {'_id':str(self.id),'name':self.name,'prototype':self.prototype.name,'properties':self.serialize(self.properties)}

    @classmethod
    def load(cls,serialized,context):
        thing_prototype = None
        for prototype in context:
            if prototype.name == serialized['prototype']:
                thing_prototype = prototype
                break
        if thing_prototype == None:
            raise ImportError
        return Thing(_id=serialized['_id'] if '_id' in serialized.keys() else None,
                     name=serialized['name'],
                     prototype=thing_prototype,
                     properties=[Property.load(content) for content in serialized['properties']])
