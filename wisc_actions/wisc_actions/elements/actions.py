from bson.objectid import ObjectId
from .base import WiscBase
from .parse import parse
from .properties import Property
from .calls import Call
from .definitions import LiteralDefinition, PropertyDefinition, IndexDefinition
from .conditions import Condition

class Primitive(WiscBase):
    '''
    Encoding for Primitive Actions. All higher-level management is handled by enclosing actions.
    '''

    keys = [set(['_id','name','parameters'])]

    def __init__(self, name, parameters, _id=None):
        self.id = ObjectId(_id)
        self.name = name
        self.parameters = parameters

    @property
    def serialized(self):
        return {'_id':self.id,
                'name':self.name,
                'parameters':self.serialize(self.parameters)}

    @classmethod
    def load(cls,serialized):
        return Primitive(**serialized)

    def resolve(self,state,parameters):
        '''
        Calling "resolve" has the effect of resolving the executable
        to a fully-specified version of itself, but not evaluating it.
        '''
        pass


class Action(Primitive):
    '''
    Encoding for Mid-Level Actions, as well as Higher-Level Actions, such as Macros.
    By default, preconditions and postconditions are inferred by sub-actions, but additional
    conditions can be specified through the keyword arguments.
    '''

    keys = [set(['_id','name','parameters','subactions','preconditions','postconditions'])]

    def __init__(self, name, parameters, subactions, definitions, preconditions, postconditions, _id=None):
        super(Action,self).__init__(_id, name, parameters)
        self.subactions = subactions
        self.definitions = definitions
        self.additional_preconditions = preconditions
        self.additional_postconditions = postconditions

    @classmethod
    def load(self,serialized):
        id = serialized['_id'] if '_id' in serialized.keys() else None
        name = serialized['name']
        parameters = serialized['parameters']
        subactions = []
        definitions = []
        preconditions = []
        postconditions = []
        for serial_subaction in serialized['subactions']:
            subactions.append(Call.load(serial_subaction))
        for serial_definition in serialized['definitions']:
            definitions.append(parse([LiteralDefinition, PropertyDefinition, IndexDefinition],serial_definition))
        for serial_precondition in serialized['preconditions']:
            preconditions.append(Condition.load(serial_precondition))
        for serial_postcondition in serialized['postconditions']:
            postconditions.append(Condition.load(serial_postcondition))
        return Action(_id=id,
                      name=name,
                      parameters=parameters,
                      subactions=subactions,
                      definitions=definitions,
                      preconditions=preconditions,
                      postconditions=postconditions)



    @property
    def serialized(self):
        repr = super(Action,self).serialized
        repr.update({'subactions':self.serialize(self.subactions),
                     'definitions':self.serialize(self.definitions),
                     'preconditions':self.serialize(self.preconditions),
                     'postconditions':self.postconditions})
        return repr

    @property
    def inferred_preconditions(self):
        '''
        Returns the set of preconditions inferred from the subactions
        '''
        # TODO
        preconditions = []
        for subaction in self.subactions:
            if isinstance(subaction,Action):
                # Add the preconditions
                pass

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

    def get_namespace(self,state,parameters):
        '''
        Obtain all items in the namespace of the action.
        '''
        namespace = {}
        # First, get the parameters specified as arguments
        for parameter in self.parameters:
            item = parameters[parameter]
            # Check to see if the value is in the state space
            if item in state:
                # Retrieve the thing for that id item
                namespace[parameter] = state[item]
            else:
                # Save the literal item value
                namespace[parameter] = item

        # Next, define anything in the definitions.
        for definitions in self.definitions:
            name = definition.name
            namespace[name] = definition

        return namespace

    def resolve(self,state,parameters):
        '''
        Calling "resolve" has the effect of resolving the executable
        to a fully-specified version of itself, but not evaluating it.
        '''
        pass

    def simulate(self,state,parameters):
        '''
        Calling "simulate" has the effect of executing the resolved action
        '''

    def check(self,state,parameters):
        '''
        Check whether the action can be executed given the current state
        '''
