from bson.objectid import ObjectId
from .base import WiscBase
from .structures import Position, Orientation, Pose
from .operations import Operator, Operation
from typing import Any, List, Dict
import z3

class Term(WiscBase):
    '''
    Wrapper for handling references to things in the space
    '''
    keys = [{'name'}]

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
        if isinstance(other,(Term,Operation,int,float)):
            return Operation(self,other,Operator.ADD)
        else:
            return None

    def __sub__(self,other):
        if isinstance(other,(Term,Operation,int,float)):
            return Operation(self,other,Operator.SUBTRACT)
        else:
            return None

    def __mul__(self,other):
        if isinstance(other,(Term,Operation,int,float)):
            return Operation(self,other,Operator.MULTIPLY)
        else:
            return None

    def __truediv__(self,other):
        if isinstance(other,(Term,Operation,int,float)):
            return Operation(self,other,Operator.DIVIDE)
        else:
            return None

    def __mod__(self,other):
        if isinstance(other,(Term,Operation,int,float)):
            return Operation(self,other,Operator.MODULUS)
        else:
            return None

    def __lt__(self,other):
        if isinstance(other,(Term,Operation,int,float)):
            return Operation(self,other,Operator.LESS_THAN)
        else:
            return None

    def __le__(self,other):
        if isinstance(other,(Term,Operation,int,float)):
            return Operation(self,other,Operator.LESS_THAN_OR_EQUALS)
        else:
            return None

    def __gt__(self,other):
        if isinstance(other,(Term,Operation,int,float)):
            return Operation(self,other,Operator.GREATER_THAN)
        else:
            return None

    def __ge__(self,other):
        if isinstance(other,(Term,Operation,int,float)):
            return Operation(self,other,Operator.GREATER_THAN_OR_EQUALS)
        else:
            return None

    def __eq__(self,other):
        if isinstance(other,(Term,Operation,int,float)):
            return Operation(self,other,Operator.EQUALS)
        else:
            return None

    def __hash__(self):
        return hash(self.name)

    def execute(self,plan,context):
        return context.get(self.name)

    def access(self,name:'Term') -> Operation:
        return Operation(self,name,Operator.ACCESS)

class Property(WiscBase):
    '''
    A generic container for specifying object properties.
    '''

    keys = [{'name','value'}]

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
        if isinstance(other,Property):
            return self.name == other.name and self.value == other.value
        else:
            return False

class Prototype(WiscBase):
    '''
    Takes 4 Parameters:
        - name (required): A name for the thing.
        - parents (required): A list of parent prototypes to inherit from.
        - properties (required): a sequence of Property objects or serialized properties.
    '''
    keys = [{'name','properties','parents'}]

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
            if parent not in parents:
                parents.append(parent)
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
        found = False
        for idx,prop in enumerate(self._properties):
            if prop.name == property.name:
                self._properties[idx] = property
                found = True
        if not found:
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
            if description.operation == Operator.EXISTS:
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

    def create_prototype(self,name) -> 'Prototype':
        prototype = Prototype(name,[self],[])
        return prototype

    @property
    def z3(self):
        vars = []
        for property in self.properties:
            prop_name = self.name+'_'+property.name
            if isinstance(property.value,int):
                prop = z3.Int(prop_name)
                vars.append(prop==property.value)
            elif isinstance(property.value,float):
                prop = z3.Float64(prop_name)
                vars.append(prop==property.value)
            elif isinstance(property.value,float):
                prop = z3.Bool(prop_name)
                vars.append(prop==property.value)
            elif isinstance(property.value,str):
                prop = z3.String(prop_name)
                vars.append(prop==property.value)
            elif isinstance(property.value,[Position,Orientation]):
                for key,value in property.value.serialized.items():
                    attr_prop_name = prop_name+'_'+key
                    prop = z3.Float64(attr_prop_name)
                    vars.append(prop==value)
            elif isinstance(property.value,Pose):
                items = property.value.serialized.items()
                for field in ['position','orientation']:
                    for key,value in items[field]:
                        attr_prop_name = prop_name+'_'+field+'_'+key
                        prop = z3.Float64(attr_prop_name)
                        vars.append(prop==value)
        return vars


class Thing(Prototype):
    '''
    Takes 4 Parameters:
        - _id (optional): The unique ID of the thing. If not specified, a new one is created.
        - name (required): A name for the thing.
        - prototype (required): Thing Prototype.
        - properties (required): a sequence of Property objects or serialized properties.
    '''

    keys = [{'name','properties','prototype'}]

    def __init__(self,name:str,prototype:Prototype,properties:List[Property],_id=None):
        super(Thing,self).__init__(name,[prototype],properties)
        self.id = ObjectId(_id)

    def create_thing(self,name:str,properties:list) -> 'Thing':
        raise NotImplementedError

    def create_prototype(self,name,properties:list) -> 'Prototype':
        raise NotImplementedError

    @property
    def prototype(self):
        return self.parents[0]

    @prototype.setter
    def prototype(self,prototype):
        self.parents[0] = prototype

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
