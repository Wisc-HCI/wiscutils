from .base import WiscBase
from .parse import parse
from .calls import Call

class Branch(WiscBase):
    '''
    Flow structure for branching logic.
    Each call is evaluated to see if the preconditions match.
    The first to match is evaluated.
    Features:
        - [Required] A set of calls that get checked consecutively
    '''

    keys = [set('flow','calls')]

    def __init__(self,calls=[]):
        self.calls = calls

    @property
    def serialized(self):
        return {'flow':'branch',
                'calls':[call.serialized for call in self.calls]}

    @classmethod
    def load(self,serialized):
        return Branch(calls=[Call.load(content) for content in serialized['calls']])

    @property
    def preconditions(self):
        '''
        The complete set of preconditions for this action
        '''
        return []

    @property
    def postconditions(self):
        '''
        The complete set of postconditions for this action
        '''
        return []

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
        pass

    def check(self,state,parameters):
        '''
        Check whether the action can be executed given the current state
        '''
        pass

class Loop(WiscBase):
    '''
    Flow structure for looping logic.
    Inner call is executed until the preconditions are no longer satisfied.
    Features:
        - [Required] An action call to execute on each item
    '''

    keys = [set('flow','call')]

    def __init__(self,loopable,item,call):
        self.call = call

    @property
    def serialized(self):
        return {'flow':'loop',
                'call':self.call.serialized}

    @classmethod
    def load(self,serialized):
        return Conditional(call=serialized['call'])

    @property
    def preconditions(self):
        '''
        The complete set of preconditions for this action
        '''
        return []

    @property
    def postconditions(self):
        '''
        The complete set of postconditions for this action
        '''
        return []

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
        pass

    def check(self,state,parameters):
        '''
        Check whether the action can be executed given the current state
        '''
        pass
