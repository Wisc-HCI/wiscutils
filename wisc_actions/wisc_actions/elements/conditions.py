from .base import WiscBase
from .things import Term, Thing, Property
from .operations import Operator, Operation
from typing import Union

class Description(WiscBase):
    '''
    Encoding for thing-agnostic property attributes.
    '''
    keys = [{'property','operator'}]

    def __init__(self,property:Property,operator:Operator):
        self.property = property
        self.operator = operator

    @classmethod
    def load(cls, serialized: dict, context: list):
        return Description(property=Property.load(serialized['property'],context),
                           operator=Operator.load(serialized['operator'],context))

    @property
    def serialized(self):
        return {'property':self.property.serialized,
                'operator':self.operator.serialized
                }

    @classmethod
    def equals(cls,property):
        return Description(property,Operator.EQUALS)

    @classmethod
    def not_equals(cls,property):
        return Description(property,Operator.NOT_EQUALS)

    @classmethod
    def less_than(cls,property):
        return Description(property,Operator.LESS_THAN)

    @classmethod
    def less_than_or_equals(cls,property):
        return Description(property,Operator.LESS_THAN_OR_EQUALS)

    @classmethod
    def greater_than(cls,property):
        return Description(property,Operator.GREATER_THAN)

    @classmethod
    def greater_than_or_equals(cls,property):
        return Description(property,Operator.GREATER_THAN_OR_EQUALS)

    @classmethod
    def exists(cls,other):
        return Description(property,Operator.EXISTS)

    def observe(self):
        return Operation(self,None,Operator.OBSERVE)

    def union(self,other):
        return Operation(self.observe(),other.observe(),Operator.UNION)

    def intersection(self,other):
        return Operation(self.observe(),other.observe(),Operator.INTERSECTION)

class Condition(WiscBase):
    '''
    Specification for defining a condition
    '''
    keys = [{'term', 'operation'}]

    def __init__(self,lhs:Union[Term,Operation],rhs:Union[Term,Operation]=None,operator:Operator=Operator.EQUALS):
        self.lhs = lhs
        self.rhs = rhs
        self.operator = operator

    @property
    def serialized(self):
        return {'lhs':self.serialize(self.lhs),
                'rhs':self.serialize(self.rhs) if self.rhs != None else None,
                'operator':self.serialize(self.operator)}

    @classmethod
    def load(cls, serialized: dict, context: list):
        return Condition(lhs=WiscBase.parse([Operation,Term],serialized['lhs'],context),
                         rhs=WiscBase.parse([Operation,Term,Property],serialized.get('rhs',None),context),
                         operator=Operator.parse(serialized['operator']))

    def execute(self,context):
        # Get the LHS
        if isinstance(self.lhs,Term):
            lhs = context.get(self.lhs)
        elif isinstance(self.lhs,Operation):
            lhs = self.lhs.execute(context)

        # Get the RHS
        if self.rhs == None:
            rhs = None
        if isinstance(self.rhs,Term):
            rhs = context.get(self.rhs)
        elif isinstance(self.rhs,Operation):
            rhs = self.rhs.execute(context)
        elif isinstance(self.rhs,Property):
            rhs = self.rhs

        if isinstance(lhs,Thing) and isinstance(rhs,Property) and self.operator == Operator.HAS_PROPERTY:
            lhs.add_property(rhs)
        elif isinstance(lhs,list) and isinstance(rhs,Property) and self.operator == Operator.HAS_PROPERTY:
            for item in lhs:
                item.add_property(rhs)
        elif self.operator == Operator.EQUALS and rhs != None:
            lhs = rhs
        elif rhs == None and self.operator == Operator.EXISTS:
            context.add_to_state(lhs)
        elif rhs == None and self.operator == Operator.DOESNT_EXIST:
            context.remove_from_state(lhs)

    def check(self,context):
        # Get the LHS
        if isinstance(self.lhs,Term):
            lhs = context.get(self.lhs)
        elif isinstance(self.lhs,Operation):
            lhs = self.lhs.execute(context)

        # Get the RHS
        if self.rhs == None:
            rhs = None
        if isinstance(self.rhs,Term):
            rhs = context.execute(self.rhs)
        elif isinstance(self.rhs,Operation):
            rhs = self.rhs.execute(context)
        elif isinstance(self.rhs,Property):
            rhs = self.rhs

        if isinstance(lhs,Thing) and isinstance(rhs,Property) and self.operator == Operator.HAS_PROPERTY:
            return lhs.has_property(rhs)
        elif isinstance(lhs,list) and isinstance(rhs,Property) and self.operator == Operator.HAS_PROPERTY:
            passed = True
            for item in lhs:
                if not item.has_property(rhs): passed = False
            return passed
        elif self.operator == Operator.EQUALS and rhs != None:
            return lhs == rhs
        elif rhs == None and self.operator == Operator.EXISTS:
            return context.exists(lhs)
        elif rhs == None and self.operator == Operator.DOESNT_EXIST:
            return not context.exists(lhs)

    @classmethod
    def has_property(cls,term:Term,property:Property):
        return Condition(lhs=term,rhs=property,operator=Operator.HAS_PROPERTY)

    @classmethod
    def doesnt_have_property(cls,term:Term,property:Property):
        return Condition(lhs=term.access(Term(property.name)),rhs=property,operator=Operator.NOT_EQUALS)

# class PropertyCondition(Condition):
#     '''
#     Encoding for thing-property comparison conditions.
#     '''
#
#     keys = [{'thing','property','operator'}]
#
#     def __init__(self,thing:str,property:Property,operator:Operator):
#         super(PropertyCondition,self).__init__(operator)
#         self.thing = thing
#         self.property = property
#
#     @classmethod
#     def load(cls, serialized: dict, context: list):
#         return PropertyCondition(thing=serialized['thing'],
#                                  property=parse([Property],serialized['property'],context),
#                                  operator=parse([Operator],serialized['operator'],context))
#
#     @property
#     def serialized(self):
#         return {'thing':self.thing,
#                 'property':self.property.serialized,
#                 'operator':self.operator.serialized
#         }
#
#     def evaluate(self,state):
#         '''
#         Check to see if the condition is satisfied.
#         '''
#         return False
#
#     def execute(self,state):
#         '''
#         Modify the state
#         '''
#         return state
#
# class UnaryLTLCondition(Condition):
#     '''
#     Encoding for unary LTL conditions. Consists of a condition and a unary LTL operator.
#     '''
#     keys = [{'condition','operator'}]
#
#     def __init__(self,condition,operator):
#         self.condition = condition
#         self.operator = operator
#
#     @classmethod
#     def load(cls,serialized):
#         return UnaryCondition(condition=WiscBase.parse([Condition,UnaryLTLCondition,BinaryLTLCondition],serialized['condition']),
#                               operator=Operator.load(serialized['operator']))
#
#     @property
#     def serialized(self):
#         return {'condition':self.condition.serialized,
#                 'operator':self.operator.serialized
#                 }
#
# class BinaryLTLCondition(Condition):
#     '''
#     Encoding for binary LTL conditions. Consists of two conditions (a/b) and a binary LTL operator.
#     '''
#
#     keys = [{'condition_a','condition_b','operator'}]
#
#     def __init__(self,condition_a,condition_b,operator):
#         self.condition_a = condition_a
#         self.condition_b = condition_b
#         self.operator = operator
#
#     @classmethod
#     def load(cls,serialized):
#         return BinaryCondition(condition_a=WiscBase.parse([PropertyCondition,UnaryLTLCondition,BinaryLTLCondition],serialized['condition_a']),
#                                condition_b=WiscBase.parse([PropertyCondition,UnaryLTLCondition,BinaryLTLCondition],serialized['condition_b']),
#                                operator=Operator.load(serialized['operator']))
#
#     @property
#     def serialized(self):
#         return {'condition_a':self.condition_a.serialized,
#                 'condition_b':self.condition_b.serialized,
#                 'operator':self.operator.serialized
#                 }
#
#     def evaluate(self,state):
#         '''
#         Check to see if the condition is satisfied.
#         '''
#         return False
#
#     def execute(self,state):
#         '''
#         Modify the state
#         '''
#         return state
