from bson.objectid import ObjectId
from .base import WiscBase
from .calls import Call
from .flow import Branch, Loop
from .assignments import Assign
from .conditions import Condition, PropertyCondition, UnaryLTLCondition, BinaryLTLCondition
from typing import List


class Primitive(WiscBase):
    '''
    Encoding for Primitive Actions. All higher-level management is handled by enclosing actions.
    '''

    keys = [{'_id', 'name', 'parameters'}]

    def __init__(self, name: str, parameters: List[str], _id: str = None):
        self.id = ObjectId(_id)
        self.name = name
        self.parameters = parameters

    @property
    def serialized(self):
        return {'_id': str(self.id),
                'name': self.name,
                'parameters': self.serialize(self.parameters)}

    @classmethod
    def load(cls, serialized: dict, context: list):
        return Primitive(**serialized)

    def create_call(self, parameters: dict) -> Call:
        return Call(id=self.id, parameters=parameters)


class Action(Primitive):
    '''
    Encoding for Mid-Level Actions, as well as Higher-Level Actions, such as Macros.
    By default, preconditions and postconditions are inferred by sub-actions, but additional
    conditions can be specified through the keyword arguments.
    '''

    keys = [{'_id', 'name', 'parameters', 'subactions','preconditions', 'postconditions'}]

    def __init__(self, name: str, parameters: List[str], subactions: List[Call], assignments: List[Assign], preconditions: List[Condition], postconditions: List[Condition], _id: str = None):
        super(Action, self).__init__(name, parameters, _id=_id)
        self.subactions = subactions
        self.assignments = assignments
        self.additional_preconditions = preconditions
        self.additional_postconditions = postconditions

    @classmethod
    def load(cls, serialized: dict, context: list):
        id = serialized['_id'] if '_id' in serialized.keys() else None
        name = serialized['name']
        parameters = serialized['parameters']
        subactions = []
        assignments = []
        preconditions = []
        postconditions = []
        for serial_subaction in serialized['subactions']:
            subactions.append(WiscBase.parse([Call, Loop, Branch], serial_subaction))
        for serial_assignment in serialized['assignments']:
            assignments.append(Assign.parse(serial_assignment,context))
        for serial_precondition in serialized['preconditions']:
            preconditions.append(
                WiscBase.parse([Condition, UnaryLTLCondition, BinaryLTLCondition], serial_precondition))
        for serial_postcondition in serialized['postconditions']:
            postconditions.append(
                WiscBase.parse([Condition, UnaryLTLCondition, BinaryLTLCondition], serial_postcondition))
        return Action(_id=id,
                      name=name,
                      parameters=parameters,
                      subactions=subactions,
                      assignments=assignments,
                      preconditions=preconditions,
                      postconditions=postconditions)

    @property
    def serialized(self):
        repr = super(Action, self).serialized
        repr.update({'subactions': self.serialize(self.subactions),
                     'assignments': self.serialize(self.assignments),
                     'preconditions': self.serialize(self.preconditions),
                     'postconditions': self.postconditions})
        return repr

    @property
    def inferred_preconditions(self):
        '''
        Returns the set of preconditions inferred from the subactions
        '''
        # TODO
        preconditions = []
        for subaction in self.subactions:
            if isinstance(subaction, Action):
                # Add the preconditions
                pass
        return preconditions

    @property
    def inferred_postconditions(self):
        '''
        Returns the set of postconditions inferred from the subactions
        '''
        # TODO
        return []

    @property
    def preconditions(self):
        '''
        The complete set of preconditions for this action
        '''
        return self.inferred_preconditions + self.additional_preconditions

    @property
    def postconditions(self):
        '''
        The complete set of postconditions for this action
        '''
        return self.inferred_postconditions + self.additional_postconditions

    def update_context(self,context,parameters:dict):
        '''
        Update all items in the context of the action for its execution.
        '''
        # add a new scope
        scope = {} # (ref, obj) pairs

        # add all parameters

        assert set(parameters.keys()) == set(self.parameters)

        # argument_parameters = { 'grip': 3, 'force': 67 }
        for key, value in parameters.items():
            scope[Reference(key)] = value

        # scope: { 'grip': 3, 'force': 67 }

        # add anything in assignments
        for assignment in self.assignments:
            scope[Reference(assignment.name)] = assignment

        # scope: { 'grip': 3, 'force': 67, 'some_def': {fallback: 1}  }

        # exit
        context.add(scope=scope)

    def resolve(self,context,parameters):
        '''
        Calling "resolve" has the effect of resolving the executable
        to a a static set of parameterized primitives.
        '''
        pass

    def simulate(self,context,parameters):
        '''
        Calling "simulate" has the effect of executing the resolved action
        '''
        pass

    def check(self,context,parameters):
        '''
        Check whether the action can be executed given the current context
        '''
        pass

    def add_assignment(self, assignment: Assign):
        self.assignments.append(assignment)

    def create_assignment(self, **kwargs) -> Assign:
        assignment = Assign(**kwargs)
        self.add_assignment(assignment)
        return assignment

    def add_precondition(self, condition: Condition):
        self.additional_preconditions.append(condition)

    def create_precondition(self, **kwargs):
        precondition = WiscBase.parse(
            [PropertyCondition, UnaryLTLCondition, BinaryLTLCondition], kwargs)
        self.add_precondition(precondition)
        return precondition

    def add_postcondition(self, condition: Condition):
        self.additional_postconditions.append(condition)

    def create_postcondition(self, **kwargs):
        postcondition = WiscBase.parse(
            [PropertyCondition, UnaryLTLCondition, BinaryLTLCondition], kwargs)
        self.add_postcondition(postcondition)
        return postcondition
