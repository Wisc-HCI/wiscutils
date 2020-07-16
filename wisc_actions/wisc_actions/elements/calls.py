from .base import WiscBase

class Call(WiscBase):
    '''
    Container for specifying a call to another action or primitive.
    '''

    keys = [set(('id','parameters'))]

    def __init__(self,id,parameters):
        self.id = id
        self.parameters = parameters

    @property
    def serialized(self):
        return {'id':self.id,'parameters':self.serialize(self.parameters)}

    @classmethod
    def load(cls,serialized)
        # TODO
        pass
