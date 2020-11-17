from .base import WiscBase
from .things import Prototype
from .actions import Primitive, Action
from .conditions import Condition
from typing import List, Union
from fuzzywuzzy import fuzz

class KnowledgeBase(WiscBase):
    '''
    Class for defining general knowledge
    '''
    keys = [{'actions','rules','prototypes'}]

    def __init__(self,actions:List[Union[Primitive,Action]]=[],rules:List[Condition]=[],prototypes:List[Prototype]=[]):
        self.actions = actions
        self.rules = rules
        self.prototypes = prototypes

    def get_action_by_id(self,id) -> Primitive:
        # Fast way to return the first item that has that id
        return next((a for a in self.actions if a.id == id or str(a.id) == id), None)

    def get_actions_by_name(self,name:str) -> List[Primitive]:
        # Since unique action names are not enforced, this may return more than one.
        # If all action names are unique, will return a list of length 1.
        return [action for action in self.actions if action.name == name]

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

    @property
    def serialized(self):
        return {'actions':self.serialize(self.actions),'rules':self.serialize(self.rules)}

    @classmethod
    def load(cls, serialized: dict, context: list):
        unresolved = serialized['prototpyes']
        passed_without_resolve = 0
        while len(unresolved) > 0 and passed_without_resolve < 3:
            for prototype in unresolved:
                try:
                    pass
                except:
                    pass
        return KnowledgeBase(actions=[WiscBase.parse([Primitive,Action],action,context) for action in serialized['actions']],
                             prototypes=[WiscBase.parse([Prototype],prototype,context) for prototype in serialized['prototypes']],
                             rules=[])

    def match_prototype(self,text):
        types = []
        for prototype in self.prototypes:
            best_score = 0
            for property in prototype.properties:
                score = fuzz.ratio(text.lower(),property.name.lower())
                if score > best_score:
                    best_score = score
            types.append({'prototype':prototype,'score':best_score})
        return sorted(types,key=lambda item: item['score'],reverse=True)
