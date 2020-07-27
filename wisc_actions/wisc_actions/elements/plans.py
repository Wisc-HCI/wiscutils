from .base import WiscBase
from .parse import parse
from .actions import Action, Primitive
from .conditions import Condition, UnaryLTLCondition, BinaryLTLCondition
from abc import ABC, abstractmethod
from bson.objectid import ObjectId

class Program(WiscBase):
    '''
    Base class for programs
    '''
    def __init__(self,name='My Program',actions=[],initial=[],_id=None):
        self.id = ObjectId(_id)
        self.name = name
        self.actions = actions
        self.initial = initial
        
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


class PlanningProgram(Program):
    '''
    Program focused on PDDL-like planning representations
    '''
    
    keys = [set(('name','actions','initial','goal','rules'))]
    
    def __init__(self,name='My Planning Program',actions=[],initial=[],goal=[],rules=[],_id=None):
        super(PlanningProgram,self).__init__(name,actions,initial,_id)
        self.goal = goal
        self.rules = rules
    
    @property
    def pddl(self):
        '''
        Returns the domain and instance files as strings.
        TODO: Indicate the version/capabilities that the PDDL supports/requires.
        '''
        
    @classmethod
    def load(cls,serialized):
        id = serialized['_id'] if '_id' in serialized.keys() else None
        actions = parse([Action,Primitive],serialized['actions'])
        initial = [Thing.load(content) for content in serialized['initial']]
        goal = [Thing.load(content) for content in serialized['goal']]
        rules = [parse([Condition,UnaryLTLCondition,BinaryLTLCondition],content) for content in serialized['rules']]
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

class ImperativeProgram(Program):
    '''
    Program focused on imperative, sequential representations
    '''
    
    keys = [set(('name','actions','initial','main'))]
    
    def __init__(self,name='My Imperative Program',actions=[],initial=[],main=None,_id=None):
        super(ImperativeProgram,self).__init__(name,actions,initial,_id)
        self.main = main
        
    @classmethod
    def load(cls,serialized):
        return ImperativeProgram()
        

class AutomataProgram(Program):
    '''
    Program focused on state-action representations
    '''
    
    keys = [set(('name','actions','states','transitions','initial_state','end_states','rules'))]
    
    def __init__(self,name='My Automata Program',actions=[],states=[],transitions=[],initial_state=None,end_states=[],rules=[],_id=None):
        super(AutomataProgram,self).__init__(name,actions,initial=[],_id=_id)
        self.states = states
        self.transitions = transitions
        self.initial_state = initial_state
        self.end_states = end_states
        self.rules = rules
        
    @classmethod
    def load(cls,serialized):
        return AutomataProgram()

class ExecutableProgram(Program):
    '''
    Utility representation for containing sequences of parameterized primitives.
    Can be partial or full programs.
    '''
    
    keys = [set(('name','actions'))]
    
    def __init__(name='My Executable Program',actions=[],_id=None):
        super(ExecutableProgram,self).__init__(name,actions,initial=[],_id=_id)
        
    @classmethod
    def load(cls,serialized):
        return ExecutableProgram()
