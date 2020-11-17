from bson.objectid import ObjectId
from .base import WiscBase
from .calls import Call
from .flow import Flow, While, ForThingObserved, ExecuteOnConditionUntil
from .assignments import Assign
from .things import Term
from .conditions import Condition
from typing import List, Union
from copy import deepcopy

class Print(WiscBase):
    '''
    Utility Class for Printing terms.
    '''
    keys = [{'term'}]

    def __init__(self,term:Term):
        self.term = term

    @property
    def serialized(self):
        return {'term':self.serialize(self.term)}

    @classmethod
    def load(cls, serialized:dict, context:list):
        return Print(Term.load(serialized['term'],context))

    def execute(self, context):
        # Get term referent
        referent = context.get(self.term)
        print(str(referent))

class Primitive(WiscBase):
    '''
    Encoding for Primitive Actions. All higher-level management is handled by enclosing actions.
    '''

    keys = [{'_id', 'name', 'parameters'}]

    def __init__(self, name: str, parameters: List[Term], _id: str = None):
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

    def call(self, parameters: dict) -> Call:
        return Call(id=self.id, parameters=parameters)

    def execute(self, kb, context, simulate=False):
        pass

    def resolve(self, kb, context):
        return {'_id': str(self.id),
                'name': self.name,
                'parameters': {self.serialize(term):context.get(term) for term in self.parameters}
        }

    def setup(self,kb,context,parameters):
        new_scope = {}
        for parameter,reference in parameters.items():
            new_scope[parameter.name] = reference
        context.add(new_scope)

    def takedown(self,kb,context,parameters):
        context.pop()

    def simulate(self,kb,context,parameters):
        context = deepcopy(context)
        parameters = deepcopy(parameters)
        self.setup(kb,context,parameters)
        self.execute(kb,context)
        self.takedown(kb,context,parameters)
        return context


class Action(Primitive):
    '''
    Encoding for Mid-Level Actions, as well as Higher-Level Actions, such as Macros.
    By default, preconditions and postconditions are inferred by sub-actions, but additional
    conditions can be specified through the keyword arguments.
    '''

    keys = [{'_id', 'name', 'parameters', 'subactions','preconditions', 'postconditions'}]

    def __init__(self, name: str, parameters: List[Term], subactions: List[Union[Call,Flow,Assign]], preconditions: List[Condition], postconditions: List[Condition], _id: str = None):
        super(Action, self).__init__(name, parameters, _id=_id)
        self.subactions = subactions
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
            subactions.append(WiscBase.parse([Call, While, ForThingObserved, ExecuteOnConditionUntil], serial_subaction))
        for serial_precondition in serialized['preconditions']:
            preconditions.append(
                WiscBase.parse([Condition], serial_precondition,context))
        for serial_postcondition in serialized['postconditions']:
            postconditions.append(
                WiscBase.parse([Condition], serial_postcondition,context))
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

    def resolve(self,kb,context):
        '''
        Calling "resolve" has the effect of resolving the executable
        to a a static set of parameterized primitives.
        '''
        resolved = []

        for executable in self.subactions:
            if isinstance(executable,Call):
                subaction = kb.get_action_by_id(executable.id)
                subaction.setup(kb,context,executable.parameters)
                res = subaction.execute(kb,context)
                if isinstance(res,list):
                    resolved.extend(res)
                else:
                    resolved.append(res)
            elif isinstance(executable,Flow):
                res = executable.resolve(kb,context)
                resolved.extend(res)
            else:
                executable.execute(kb,context)
            if isinstance(executable,Call):
                subaction.takedown(kb,context,executable.parameters)

        return resolved

    def takedown(self,kb,context,parameters):
        for postcondition in self.additional_postconditions:
            postcondition.execute(context)
        context.pop()

    def execute(self, kb, context):
        '''
        Calling "execute" has the effect of executing the action
        '''
        # A new scope should have been defined outside this action.
        # Execute each of the sub-actions
        for executable in self.subactions:
            if isinstance(executable,Call):
                subaction = kb.get_action_by_id(executable.id)
                subaction.setup(kb,context,executable.parameters)
                subaction.execute(kb,context)
            elif isinstance(executable,Flow):
                executable.execute(kb,context)
            else:
                executable.execute(context)
            if isinstance(executable,Call):
                subaction.takedown(kb,context,executable.parameters)

    def check(self,kb,context,parameters):
        '''
        Check whether the action can be executed given the current context and parameters
        '''
        # TODO: Set up scope and add parameters
        passed = True
        for precondition in self.preconditions:
            if not precondition.check(kb,context):
                passed = False
        return passed

    def add_assignment(self, assignment: Assign):
        self.assignments.append(assignment)

    def create_assignment(self, **kwargs) -> Assign:
        assignment = Assign(**kwargs)
        self.add_assignment(assignment)
        return assignment

    def add_precondition(self, condition: Assign):
        self.additional_preconditions.append(condition)

    def create_precondition(self, **kwargs) -> Assign:
        precondition = WiscBase.parse([Assign], kwargs)
        self.add_precondition(precondition)
        return precondition

    def add_postcondition(self, condition: Assign):
        self.additional_postconditions.append(condition)

    def create_postcondition(self, **kwargs) -> Assign:
        postcondition = WiscBase.parse([Assign], kwargs)
        self.add_postcondition(postcondition)
        return postcondition
