from .base import WiscBase
from .things import Term,Thing
from .structures import Position, Orientation, Pose

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

    def get(self,reference:Term,level:int=0):
        # Search in the lowermost scope for the object,
        # and if it is not found, seach in the state.
        if level < len(self.scopes):
            scope = self.scopes[len(self.scopes)-level]
        else:
            scope = self.state

        if reference.name in scope:
            if isinstance(scope[reference.name],Term):
                return self.get(scope[reference],level+1)
            else:
                return scope[reference.name]
        elif reference.name in self.state:
            return scope[reference.name]

        return None

    def set(self,reference:Term,node:WiscBase,level:int=0):
        # Search in the lowermost scope for the object,
        # and if it is not found, seach in the state.
        if level < len(self.scopes):
            scope = self.scopes[len(self.scopes)-level]
        else:
            scope = self.state

        if reference.name in scope:
            if isinstance(scope[reference.name],Term):
                self.set(scope[reference],node,level+1)
            else:
                scope[reference.name] = node
        elif reference.name in self.state:
            scope[reference.name] = node
        else:
            scope[reference.name] = node

    def __repr__(self):
        return str(self.scopes)

    def load(self, serialized: dict, context: list = []):
        [WiscBase.parse(classes,content,context) for conent in serialized]
        initial = {key:WiscBase.parse([Thing,Term,Position,Orientation,Pose],value,context) for key,value in serialized.items()}
        return Context(initial)

    @property
    def serialized(self):
        return {key:self.serialize(value) for key,value in self.state.items()}
