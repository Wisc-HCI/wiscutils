from .base import WiscBase
from .actions import Action, Primitive
from .conditions import Condition, PropertyCondition, UnaryLTLCondition, BinaryLTLCondition
from .things import Thing, Property
from wisc_actions.errors.warnings import DuplicateActionNameWarning, MainDoesNotExistWarning
from abc import ABC, abstractmethod
from bson.objectid import ObjectId
import warnings
from typing import List

class Program(WiscBase):
    '''
    Base class for programs
    '''
    def __init__(self,name:str='My Program',actions:List[Primitive]=[],initial=[],_id:str=None):
        self.id = ObjectId(_id)
        self.name = name
        self.actions = actions
        self.initial = initial

    @classmethod
    @abstractmethod
    def new(cls,name:str='My Program'):
        return Program(name)

    @abstractmethod
    def simultate(self):
        pass

    @abstractmethod
    def resolve(self):
        pass

    @property
    def serialized(self):
        return {'_id':str(self.id),
                'name':self.name,
                'actions':self.serialize(self.actions),
                'initial':self.serialize(self.initial)
        }

    def get_action_by_id(self,id) -> Primitive:
        # Fast way to return the first item that has that id
        return next((a for a in self.actions if a.id == id or str(a.id) == id), None)

    def get_actions_by_name(self,name:str) -> List[Primitive]:
        # Since unique action names are not enforced, this may return more than one.
        # If all action names are unique, will return a list of length 1.
        return [action for action in self.actions if action.name == name]

    def get_thing_in_initial_state_by_id(self,id) -> Thing:
        # Fast way to return the first item that has that id
        return next((t for t in self.initial if t.id == id or str(t.id) == id), None)

    def add_action(self,action:Primitive):
        if len(self.get_actions_by_name(action.name)) > 0:
            warnings.warn('Action name {0} already exists. This is permitted but will require searching for actions by ID',DuplicateActionNameWarning)
        self.actions.append(action)

    def create_action(self,name:str,parameters:List[str]=[]) -> Action:
        action = Action(name,parameters,[],[],[],[])
        self.add_action(action)
        return action

    def create_primitive(self,name:str,parameters:List[str]=[]) -> Primitive:
        primitive = Primitive(name,parameters)
        self.add_action(primitive)
        return primitive

    def add_thing_to_initial_state(self,thing):
        self.initial.append(thing)

    def create_thing(self,name:str,properties:List[Property]) -> Thing:
        thing = Thing(name,properties)
        self.add_thing_to_initial_state(thing)
        return thing

    def add_property_to_thing_in_initial_state(self,thing_id,property:Property):
        thing = self.get_thing_in_initial_state_by_id(thing_id)
        thing.add_property(property)

class PlanningProgram(Program):
    '''
    Program focused on PDDL-like planning representations
    '''

    keys = [set(('name','actions','initial','goal','rules'))]

    def __init__(self,name:str='My Planning Program',actions:List[Primitive]=[],initial=[],goal=[],rules:List[Condition]=[],_id:str=None):
        super(PlanningProgram,self).__init__(name,actions,initial,_id)
        self.goal = goal
        self.rules = rules

    @property
    def pddl(self):
        '''
        Returns the domain and instance files as strings.
        TODO: Indicate the version/capabilities that the PDDL supports/requires.
        '''
        instance = ''
        domain = ''
        return instance, domain

    @classmethod
    def load(cls,serialized:dict,context:list):
        id = serialized['_id'] if '_id' in serialized.keys() else None
        actions = WiscBase.parse([Action,Primitive],serialized['actions'])
        initial = [Thing.load(content,context) for content in serialized['initial']]
        goal = [Thing.load(content,context) for content in serialized['goal']]
        rules = [WiscBase.parse([Condition,UnaryLTLCondition,BinaryLTLCondition],content,context) for content in serialized['rules']]
        return PlanningProgram(name=serialized['name'],actions=actions,initial=initial,goal=goal,rules=rules,_id=id)

    @property
    def serialized(self):
        return {'_id':str(self.id),
                'name':self.name,
                'actions':self.serialize(self.actions),
                'initial':self.serialize(self.initial),
                'goal':self.serialize(self.goal),
                'rules':self.serialize(self.rules)
               }

    @classmethod
    def new(cls,name:str='My Planning Program'):
        return PlanningProgram(name)

class ImperativeProgram(Program):
    '''
    Program focused on imperative, sequential representations
    '''

    keys = [set(('name','actions','initial','main','rules'))]

    def __init__(self,name='My Imperative Program',actions=[],initial=[],main=None,rules=[],_id=None):
        super(ImperativeProgram,self).__init__(name,actions,initial,_id)
        self.main = main
        self.rules = rules

    @classmethod
    def load(cls,serialized:dict,context:list):
        id = serialized['_id'] if '_id' in serialized.keys() else None
        actions = WiscBase.parse([Action,Primitive],serialized['actions'],context)
        initial = [Thing.load(content) for content in serialized['initial']]
        main = serialized['main']
        rules = [WiscBase.parse([Condition,UnaryLTLCondition,BinaryLTLCondition],content,context) for content in serialized['rules']]
        return ImperativeProgram(name=serialized['name'],actions=actions,initial=initial,main=main,_id=id)

    @property
    def serialized(self):
        return {'_id':str(self.id),
                'name':self.name,
                'actions':self.serialize(self.actions),
                'initial':self.serialize(self.initial),
                'main':str(self.main),
                'rules':self.serialize(self.rules)
               }

    def set_main_by_id(self,id):
        self.main = id
        if self.get_action_by_id(id) == None:
            warnings.warn('The ID specified does not belong to an action that is currently defined for this plan.',MainDoesNotExistWarning)

    @classmethod
    def new(cls,name='My Imperative Program'):
        main = Action(name='main', parameters=[], subactions=[], definitions=[], preconditions=[], postconditions=[])
        return ImperativeProgram(name=name,actions=[main],initial=[],main=main.id)

    def simultate(self):
        pass

    def resolve(self):
        pass


class AutomataProgram(Program):
    '''
    Program focused on state-action representations
    '''

    keys = [set(('name','actions','states','transitions','initial','end_states','rules'))]

    def __init__(self,name='My Automata Program',actions=[],states=[],transitions=[],initial=None,end_states=[],rules=[],_id=None):
        super(AutomataProgram,self).__init__(name,actions,initial=[],_id=_id)
        self.states = states
        self.transitions = transitions
        self.initial = initial
        self.end_states = end_states
        self.rules = rules

    @classmethod
    def load(cls,serialized:dict,context:list):
        id = serialized['_id'] if '_id' in serialized.keys() else None
        name = serialized['name']
        actions = WiscBase.parse([Action,Primitive],serialized['actions'],context)
        # TODO: Decide on whether we want to structure automata as states and transitions
        states = serialized['states']
        transitions = serialized['transitions']
        initial_state = serialized['initial_state']
        end_states = serialized['end_states']
        rules = [WiscBase.parse([Condition,UnaryLTLCondition,BinaryLTLCondition],content,context) for content in serialized['rules']]
        return AutomataProgram(name,actions,states,transitions,initial_state,end_states,rules,id)

    @classmethod
    def new(cls,name='My Automata Program'):
        # TODO: define an initial state and initialize the new program with it.
        return AutomataProgram(name=name)

class ExecutableProgram(Program):
    '''
    Utility representation for containing sequences of parameterized primitives.
    Can be partial or full programs.
    '''

    keys = [set(('name','actions'))]

    def __init__(name='My Executable Program',actions=[],_id=None):
        super(ExecutableProgram,self).__init__(name,actions,initial=[],_id=_id)

    @classmethod
    def load(cls,serialized:dict,context:list):
        return ExecutableProgram()
