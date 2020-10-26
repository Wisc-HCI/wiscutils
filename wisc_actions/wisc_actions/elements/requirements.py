from .base import WiscBase
from .conditions import *
from .definitions import *
from .things import Prototype

class Requirement(WiscBase):
    def __init__(self, definition:DescriptionDefinition, description:Description):
        self.definition = definition
        self.description = description

    @property
    def serialized(self):
        return {'definition': self.serialize(self.definition),'description':self.serialize(self.description)}

    @classmethod
    def load(cls, serialized: dict, context: list):
        return Requirement(serialized['name'])


    @abstractmethod
    def get(self,context): # State?
        pass
