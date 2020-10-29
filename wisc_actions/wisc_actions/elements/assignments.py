from .base import WiscBase
from .things import Thing, Property
from .structures import Position, Orientation, Pose
from .operations import *

class Assign(WiscBase):
    '''
    Specification for defining a value in the namespace of an action
    '''
    keys = [{'term', 'operation', 'fallback'}]

    def __init__(self,term,operation,fallback=None):
        self.term = term
        self.operation = operation
        self.fallback = fallback

    @property
    def serialized(self):
        return {'term':self.term.serialized,
                'operation':self.serialize(self.operation),
                'fallback':self.serialize(self.fallback)}

    @classmethod
    def load(cls, serialized: dict, context: list):
        return Assign(term=Term(serialized['term']),
                      operation=WiscBase.parse([Operation,Observe,Term],serialized['operation'],context),
                      fallback=WiscBase.parse([Operation,Observe,Term],serialized['fallback'],context))

    def evaluate(self,context):
        item = context.get(self.term)
        result = self.operation.execute(context)
        if result == None:
            result = self.fallback.execute(context)

        if isinstance(item,Thing) and isinstance(result,Property):
            item.add_property(result)
        else:
            context.set(self.term,result)

# class Definition(WiscBase):
#     '''
#     Specification for defining a value in the namespace of an action.
#     '''
#
#     def __init__(self, name):
#         self.name = name
#
#     @property
#     def serialized(self):
#         return {'name': self.name}
#
#     @classmethod
#     def load(cls, serialized: dict, context: list):
#         return Definition(serialized['name'])
#
#
#     @abstractmethod
#     def get(self,context): # State?
#         pass
#
#
# class LiteralDefinition(Definition):
#     '''
#     Specification for defining a literal value in the namespace of an action.
#     This is essentially equivalent to:
#         y = 2
#     '''
#
#     keys = [set(('name', 'value'))]
#
#     def __init__(self, name, value):
#         super(LiteralDefinition, self).__init__(name)
#         self.value = value
#         # set value in namespace
#         # self.set(namespace, self.value)
#
#     @property
#     def serialized(self):
#         serialized = super(LiteralDefinition, self).serialized
#         serialized.update({'value': self.serialize(self.value)})
#         return serialized
#
#     @classmethod
#     def load(cls, serialized: dict, context: list):
#         value = WiscBase.parse([Thing, Position, Orientation, Pose], serialized, context)
#         return LiteralDefinition(name=serialized['name'], value=value)
#
#
#     def get(self,context): # State?
#         return self.value
#
#
# class PropertyDefinition(Definition):
#     '''
#     Specification for defining a value via a thing's property in the namespace of an action.
#     This is essentially equivalent to:
#         is_num = isinstance(2,Int)
#     Or:
#         position = pose.position
#     '''
#
#     keys = [set(('name', 'item', 'property'))]
#
#     def __init__(self, name, item, property, fallback=None):
#         super(PropertyDefinition, self).__init__(name)
#         self.item = item
#         self.property = property
#         self.fallback = fallback
#
#     @property
#     def serialized(self):
#         serialized = super(PropertyDefinition, self).serialized
#         serialized.update({'item': self.item,
#                            'property': self.property,
#                            'fallback': self.serialize(self.fallback)})
#         return serialized
#
#     @classmethod
#     def load(cls, serialized: dict, context: list):
#         fallback = serialized['fallback'] if 'fallback' in serialized.keys(
#         ) else None
#         return PropertyDefinition(name=serialized['name'],
#                                   item=serialized['item'],
#                                   property=serialized['property'],
#                                   fallback=WiscBase.parse([Thing, Position, Orientation, Pose], fallback))
#
#     @abstractmethod
#     def get(self,context):
#         # Item is the reference to the object, or the id in state
#         obj = context.get(self.item)
#
#         # Three cases:
#         # Property Class of Thing (e.g. is_ball(obj))
#         if isinstance(Thing,obj):
#             for property in obj.properties:
#                 if property.name == self.property:
#                     return property
#
#         # Key in Dictionary (e.g obj['ball'])
#         elif isinstance(Dict, obj):
#             # Might have to change this:
#             return AttributeWrapper(obj,self.property,lookup_type='dictionary')
#
#         # Python Attribute of Thing (e.g. obj.ball)
#         elif isinstance(WiscBase,obj):
#             # Might have to change this:
#             attr = getattr(obj, self.property)
#             if not isinstance(WiscBase,attr):
#                 return AttributeWrapper(obj,self.property,lookup_type='property')
#             return attr
#
#         return self.fallback
#
#
# class IndexDefinition(Definition):
#     '''
#     Specification for defining a value via an object's index in the namespace of an action.
#     This is essentially equivalent to:
#         box = boxes[0]
#     '''
#
#     keys = [set(('name', 'item', 'index'))]
#
#     def __init__(self, name, item, index, fallback):
#         super(IndexDefinition, self).__init__(name)
#         self.item = item
#         self.index = index
#         self.fallback = fallback
#
#     @property
#     def serialized(self):
#         serialized = super(IndexDefinition, self).serialized
#         serialized.update({'item': self.item,
#                            'index': self.index,
#                            'fallback': self.serialize(self.fallback)})
#         return serialized
#
#     @classmethod
#     def load(cls, serialized: dict, context: list):
#         return IndexDefinition(name=serialized['name'],
#                                item=serialized['item'],
#                                property=serialized['index'])
#
#     @abstractmethod
#     def get(self,context):
#         # Returns an item in a WiscBase Enumerable
#         enum = context.get(self.item)
#         if isinstance(Enumerable, enum):
#             if len(enum) != 0 and self.index >= len(enum):
#                 return self.fallback # index out of bounds
#             return enum[self.index]
#         return self.fallback
#
# class DescriptionDefinition(Definition):
#     '''
#     Specification for defining a set of things based on descriptions.
#     This is essentially equivalent to:
#         boxes = [object for object in objects if object.is_box]
#     '''
#
#     keys = [set(('name', 'descriptions', 'operation'))]
#
#     def __init__(self, name, descriptions, operation:SetOperation):
#         super(DescriptionDefinition, self).__init__(name)
#         self.descriptions = descriptions
#         self.operation = operation
#
#     @property
#     def serialized(self):
#         serialized = super(DescriptionDefinition, self).serialized
#         serialized.update(
#             {'descriptions': [description.serialized for description in self.descriptions]})
#         return serialized
#
#     @classmethod
#     def load(cls, serialized: dict, context: list):
#         return DescriptionDefinition(name=serialized['name'],
#                                      descriptions=[Description.load(content,context) for content in serialized['descriptions']])
#
#     @abstractmethod
#     def get(self,context):
#         # Returns a WiscBase Enumerable
#         items = []
#
#         if self.operation == SetOperation.UNION:
#             for description in self.descriptions:
#                 for key,value in context.state.items():
#                     if value in items:
#                         pass
#                     elif isinstance(Thing,value):
#                         if value.has_description(description):
#                             items.append(value)
#                     elif isinstance(WiscBase,value):
#                         if description.operation == Operation.EXISTS and description.property.name in value.keys:
#                             items.append(value)
#                         elif description.property.name in value.keys:
#                             attr = getattr(value,description.property.name)
#                             if description.operation.execute(attr,description.property.value):
#                                 items.append(value)
#                     elif isinstance(dict,value):
#                         if description.operation == Operation.EXISTS and description.property.name in value.keys():
#                             items.append(value)
#                         elif description.property.name in value.keys():
#                             if description.operation.execute(value[description.property.name],description.property.value):
#                                 items.append(value)
#
#         elif self.operation == SetOperation.Intersection:
#             items = [item for key,item in context.state.items()]
#
#             for description in self.descriptions:
#                 to_remove = []
#                 for value in items:
#                     should_remove = True
#                     if value in to_remove:
#                         should_remove = False
#                     elif isinstance(Thing,value):
#                         if not value.has_description(description):
#                             should_remove = False
#                     elif isinstance(WiscBase,value):
#                         should_remove = True
#                         if description.operation == Operation.EXISTS and description.property.name in value.keys:
#                             should_remove = False
#                         elif description.property.name in value.keys:
#                             attr = getattr(value,description.property.name)
#                             if description.operation.execute(attr,description.property.value):
#                                 should_remove = False
#                     elif isinstance(dict,value):
#                         if description.operation == Operation.EXISTS and description.property.name in value.keys():
#                             should_remove = False
#                         elif description.property.name in value.keys():
#                             if description.operation.execute(value[description.property.name],description.property.value):
#                                 should_remove = False
#                     if should_remove:
#                         to_remove.append(value)
#                 items = [item for item in items if item not in to_remove]
#
#         return Enumerable(items=items)
#
# class OperationDefinition(Definition):
#     '''
#     Specification for defining a set of things based on operations.
#     This is essentially equivalent to:
#         a = b + c
#         is_fast = speed > 5
#     '''
#
#     keys = [set(('name', 'operation'))]
#
#     def __init__(self, name: str, operation: Math):
#         super(OperationDefinition, self).__init__(name)
#         self.operation = operation
#
#     @property
#     def serialized(self):
#         serialized = super(OperationDefinition, self).serialized
#         serialized.update({'operation': self.operation.serialized})
#         return serialized
#
#     @classmethod
#     def load(cls, serialized: dict, context: list):
#         return MathDefinition(name=serialized['name'],
#                               operation=Math.load(serialized['operation'],context))
#
#     @abstractmethod
#     def get(self,context):
#         self.operation.execute()
#         pass
#
#         '''
#         b = Term('b')
#         c = Term('c')
#         summation = OperationDefinition('a', b+c)
#         '''
