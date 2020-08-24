from .operations import MathOperation
from .base import WiscBase

EXECUTION = {
    MathOperation.ADD:lambda term_a, term_b: term_a + term_b,
    MathOperation.SUBTRACT:lambda term_a, term_b: term_a - term_b,
    MathOperation.MULTIPLY:lambda term_a, term_b: term_a * term_b,
    MathOperation.DIVIDE:lambda term_a, term_b: term_a / term_b,
    MathOperation.POWER:lambda term_a, term_b: term_a ** term_b,
    MathOperation.MODULUS:lambda term_a, term_b: term_a % term_b,
    MathOperation.CARTESIAN_DISTANCE:lambda term_a, term_b: term_a.distance_to(term_b),
    MathOperation.ANGULAR_DISTANCE:lambda term_a, term_b: term_a.distance_to(term_b),
}

class Math(WiscBase):
    '''
    Class for defining mathematical operations
    '''

    keys = [set(('term_a','term_b','operation'))]

    def __init__(self,term_a,term_b=None,operation=None):
        self.term_a = term_a
        self.term_b = term_b
        self.operation = operation

    @classmethod
    def load(cls,serialized):
        '''
        TODO: handle whatever context-grabbing implementation we use here for
        non-math terms.
        '''
        return Math(term_a=parse([Math],serialized['term_a']),
                    term_b=parse([Math],serialized['term_b']),
                    operation=MathOperation.load(serialized['operation']))

    @property
    def serialized(self):
        return {'term_a':self.serialize(self.term_a),
                'term_b':self.serialize(self.term_b),
                'operation':self.serialize(self.operation)
                }

    def exec(self,context):
        lhs = Math.resolve(self.term_a, context)
        rhs = Math.resolve(self.term_b, context)
        return EXECUTION[self.operation](lhs, rhs)

    @classmethod
    def resolve(self,term,context):
        if isinstance(str,term):
            return context.get(term)
        elif isinstance(int,term) or isinstance(float,term):
            return term

'''
b = Math(2)
c = Math(3)
a = Math(b, c, MathOperation.ADD)
print(a.exec()) # 5
'''
