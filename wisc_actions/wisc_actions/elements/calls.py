from .base import WiscBase
from .things import Term
from typing import Dict

class Call(WiscBase):
    '''
    Container for specifying a call to another action or primitive.
    '''

    keys = [{'id','parameters'}]

    def __init__(self,id,parameters:Dict[Term,Term]):
        self.id = id
        self.parameters = parameters

    @property
    def serialized(self):
        return {'id':str(self.id),'parameters':self.serialize(self.parameters)}

    @classmethod
    def load(cls, serialized: dict, context: list):
        return Call(id=serialized['id'],parameters=[{Term(key):Term(key)} for key,value in serialized['parameters'].items()])
