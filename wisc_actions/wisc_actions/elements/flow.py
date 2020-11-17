from .base import WiscBase
from .calls import Call
from .things import Term
from .conditions import Condition
from .operations import Operation
from typing import Union

class Flow(WiscBase):

    keys = [{'subactions'}]

    def __init__(self,subactions:Union['Call','Flow','Assign']=[]):
        self.subactions = subactions

    @property
    def serialized(self):
        return {'subactions':self.serialize(self.subactions)}

class ForThingObserved(Flow):
    '''
    Pairing of Term, Observe Operation, and a set of executable calls
    (e.g. other logic or primitive/action calls).
    For every thing observed in the state with the observation operation,
    load that thing into the term and execute the calls.
    This will exit as soon as there are no more objects with the described description,
    but that observation is evaluated each time,
    so if something is added during execution, it would handle this.
    '''

    keys = [{'subactions','term','operation'}]

    def __init__(self,term:Term,operation:Operation,subactions:Union['Call','Flow','Assign']=[]):
        super(ForThingObserved,self).__init__(subactions)
        self.term = term
        self.operation = operation

    @property
    def serialized(self):
        serialized = super(ForThingObserved,self).serialized
        serialized['term'] = self.term.serialized
        serialized['operation'] = self.operation.serialized
        return serialized

    def execute(self,kb,context):
        '''
        Calling "execute" has the effect of executing the flow.
        '''
        # First, get the initial list
        things = self.operation.execute(context)
        while len(things) > 0:
            self.context.set(self.term,things[0])
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
            things = self.operation.execute(context)

    def resolve(self,kb,context):
        '''
        Calling "execute" has the effect of resolving the flow to primitives.
        '''
        resolved = []
        things = self.operation.execute(context)
        while len(things) > 0:
            self.context.set(self.term,things[0])
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
                    executable.execute(context)
                if isinstance(executable,Call):
                    subaction.takedown(kb,context,executable.parameters)
            things = self.operation.execute(context)

        return resolved

class While(Flow):
    '''
    Pairing of some condition with a set of executable calls.
    This encompasses property checks, etc, and behaves similar
    to what you would expect with a standard while loop.
    '''

    keys = [{'subactions','condition'}]

    def __init__(self,condition:Condition,subactions:Union['Call','Flow','Assign']=[]):
        super(While,self).__init__(subactions)
        self.condition = condition

    @property
    def serialized(self):
        serialized = super(While,self).serialized
        serialized['condition'] = self.condition.serialized
        return serialized

    def execute(self,kb,context):
        '''
        Calling "execute" has the effect of executing the flow.
        '''

        # First, get the initial list
        while self.condition.check(context):
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

    def resolve(self,kb,context):
        '''
        Calling "execute" has the effect of resolving the flow to primitives.
        '''
        resolved = []
        while self.condition.check(context):
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
                    executable.execute(context)
                if isinstance(executable,Call):
                    subaction.takedown(kb,context,executable.parameters)

        return resolved

class Branch(Flow):
    '''
    Pairing of some condition with a pair of executable sets.
    If condition matches, execute the first, otherwise the second.
    '''

    keys = [{'if_pass','if_fail','condition'}]

    def __init__(self,condition:Condition,if_pass:Union['Call','Flow','Assign']=[],if_fail:Union['Call','Flow','Assign']=[]):
        super(Branch,self).__init__([])
        self.condition = condition
        self.if_pass = if_pass
        self.if_fail = if_fail

    @property
    def serialized(self):
        serialized = {'condition':self.serialize(self.condition),
                      'if_pass':self.serialize(self.if_pass),
                      'if_fail':self.serialize(self.if_fail)
        }
        return serialized

    def execute(self, kb, context, simulate=False):
        '''
        Calling "execute" has the effect of executing the flow.
        '''
        # First, get the initial list
        if self.condition.check(context):
            for executable in self.if_pass:
                if isinstance(executable,Call):
                    subaction = kb.get_action_by_id(executable.id)
                    subaction.setup(kb,context,executable.parameters)
                elif isinstance(executable,Flow):
                    executable.execute(kb,context)
                else:
                    executable.execute(context)
                if isinstance(executable,Call):
                    subaction.takedown(kb,context,executable.parameters)
        else:
            for executable in self.if_fail:
                if isinstance(executable,Call):
                    subaction = kb.get_action_by_id(executable.id)
                    subaction.setup(kb,context,executable.parameters)
                elif isinstance(executable,Flow):
                    executable.execute(kb,context)
                else:
                    executable.execute(context)
                if isinstance(executable,Call):
                    subaction.takedown(kb,context,executable.parameters)

    def resolve(self,kb,context):
        '''
        Calling "execute" has the effect of resolving the flow to primitives.
        '''
        resolved = []
        if self.condition.check(context):
            for executable in self.if_pass:
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
                    executable.execute(context)
                if isinstance(executable,Call):
                    subaction.takedown(kb,context,executable.parameters)
        else:
            for executable in self.if_fail:
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
                    executable.execute(context)
                if isinstance(executable,Call):
                    subaction.takedown(kb,context,executable.parameters)

        return resolved

class ExecuteOnConditionUntil(Flow):
    '''
    Given 2 conditions, the first tells when the executables should execute,
    and the second says when the control block should end.
    '''

    keys = [{'subactions','on','until'}]

    def __init__(self,on:Condition,until:Condition,subactions:Union['Call','Flow','Assign']=[]):
        super(ExecuteOnConditionUntil,self).__init__(subactions)
        self.on = on
        self.until = until

    @property
    def serialized(self):
        serialized = super(ExecuteOnConditionUntil,self).serialized
        serialized['on'] = self.on.serialized
        serialized['until'] = self.until.serialized
        return serialized

    def execute(self,kb,context):
        '''
        Calling "execute" has the effect of executing the flow.
        '''
        # First, get the initial list
        while not self.until.check(context):
            if self.on.check(context):
                for executable in self.subactions:
                    if isinstance(executable,Call):
                        subaction = kb.get_action_by_id(executable.id)
                        subaction.setup(kb,context,executable.parameters)
                    else:
                        subaction = executable
                    subaction.execute(kb,context)
                    if isinstance(executable,Call):
                        subaction.takedown(kb,context,executable.parameters)

    def resolve(self,kb,context):
        '''
        Calling "execute" has the effect of resolving the flow to primitives.
        '''
        resolved = []
        while not self.until.check(context):
            if self.on.check(context):
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
