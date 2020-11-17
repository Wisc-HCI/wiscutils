from .base import WiscBase
from .things import Term,Thing
from .structures import Position, Orientation, Pose
from typing import Any, List, Dict
import z3
from fuzzywuzzy import fuzz

class Context(WiscBase):
    '''
    Runtime - calculated context and state of the program and its values
    (When serialized, reverts to state)
    '''
    def __init__(self,initial:List[Thing]=[]):
        self.state = initial
        self.scopes = [{}]

    def add(self,scope={}):
        self.scopes.append(scope)

    def pop(self):
        if len(self.scopes) > 1:
            self.scopes.pop()

    def add_to_state(self,thing:Thing,reference:Term=None):
        found = False
        for idx,state_thing in enumerate(self.state):
            if thing.id == state_thing.id:
                self.state[idx] = thing
                found = True
        if not found:
            self.state.append(thing)
        if reference != None:
            self.scopes[len(self.scopes)-1][reference.name] = Term(str(thing.id))

    def remove_from_state(self,thing:Thing=None,reference:Term=None):
        if thing != None:
            self.state = [entity for entity in self.state if entity.id != thing.id]
            self.remove_references(Term(str(thing.id)))
        elif reference != None:
            thing = self.get(reference,0)
            self.state = [entity for entity in self.state if entity.id != thing.id]
            self.remove_references(reference)


    def get(self,reference:Term,level:int=0):
        # Search in the lowermost scope for the object,
        # and if it is not found, seach in the state.
        if level < len(self.scopes):
            scope = self.scopes[len(self.scopes)-level-1]
        else:
            scope = {str(thing.id):thing for thing in self.state}

        if reference.name in scope:
            if isinstance(scope[reference.name],Term):
                return self.get(scope[reference.name],level+1)
            else:
                return scope[reference.name]
        elif reference.name in self.state:
            return scope[reference.name]

        return None

    def set(self,reference:Term,node:WiscBase,level:int=0):
        # Search in the lowermost scope for the object,
        # and if it is not found, seach in the state.
        if level < len(self.scopes):
            scope = self.scopes[len(self.scopes)-level-1]
            if reference.name in scope:
                if isinstance(scope[reference.name],Term):
                    self.set(scope[reference.name],node,level+1)
                else:
                    scope[reference.name] = node
                    return
            else:
                scope[reference.name] = node
                return
        if isinstance(node,Thing):
            for idx,item in enumerate(self.state):
                if str(item.id) == reference.name:
                    self.state[idx] = node
                    if str(node.id) != str(item.id):
                        self.replace_references(str(item.id),str(node.id))
                    return


    def replace_references(self,former,new):
        for scope in self.scopes:
            for key,value in scope.items():
                if isinstance(value,Term) and value.name == former:
                    value.name = new

    def remove_references(self,reference:Term):
        target = self.get(reference)
        for scope in reversed(self.scopes):
            for key,value in scope.items():
                if isinstance(value,Term) and self.get(value) == target:
                    del scope[key]


    def exists(self,reference:Term,level:int=0):
        if level < len(self.scopes):
            scope = self.scopes[len(self.scopes)-level-1]
        else:
            scope = {thing.id:thing for thing in self.state}

        if reference.name in scope:
            if isinstance(scope[reference.name],Term):
                return self.exists(scope[reference.name],level+1)
            else:
                return True
        elif reference.name in [thing.id for thing in self.state]:
            return True

        return False

    def match_thing(self,text):
        types = []
        for thing in self.state:
            best_score = 0
            for property in thing.properties:
                score = fuzz.ratio(text.lower(),property.name.lower())
                if score > best_score:
                    best_score = score
            types.append({'thing':thing,'score':best_score})
        return sorted(types,key=lambda item: item['score'],reverse=True)

    @property
    def z3(self):
        constraints = []
        for thing in self.state:
            constraints.extend(thing.z3)
        return constraints

    def __repr__(self):
        return str(self.scopes)

    def load(self, serialized: dict, context: list = []):
        [WiscBase.parse(classes,content,context) for conent in serialized]
        initial = {key:WiscBase.parse([Thing,Term,Position,Orientation,Pose],value,context) for key,value in serialized.items()}
        return Context(initial)

    @property
    def serialized(self):
        return {key:self.serialize(value) for key,value in self.state.items()}
