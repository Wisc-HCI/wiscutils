from .base import WiscBase
from .things import Reference

# class Redirect(object):
#     '''
#     Performs linkages from the scopes to other scopes or the state
#     '''
#     def __init__(self,object):
#         self.object

class Context(WiscBase):
    '''
    Runtime - calculated context and state of the program and its values
    (When serialized, reverts to state)
    '''
    def __init__(self,initial:dict):
        self.state = initial
        self.scopes = []

    def add(self,scope={}):
        self.scopes.append(scope)

    def pop(self):
        self.scopes.pop()

    def get(self,reference:Reference,level:Int=0):
        # Search in the lowermost scope for the object,
        # and if it is not found, seach in the state.
        if level < len(self.scopes):
            scope = self.scopes[len(self.scopes)-level]
        else:
            scope = self.state

        if reference in scope:
            if isinstance(Reference,scope[reference]):
                return self.get(scope[reference],level+1)
            else:
                return scope[reference]
        elif reference in self.state:
            return scope[reference]

        return None

    def set(self,reference:Reference,node):
        #TODO
        pass

        # for level in reversed(self.scopes):
        #     if varname in level.keys():
        #         level[varname] = node
        #         return
        # # Not already defined, add to the current scope
        # self.scopes[-1][varname] = node

    def __repr__(self):
        return str(self.scopes)
