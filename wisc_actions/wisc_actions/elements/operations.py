from enum import Enum

class Operation(Enum):

    @classmethod
    def load(cls,serialized):
        for op in cls:
            if op.value == serialized:
                return op

    @property
    def serialized(self):
        return self.value

class PropertyOperation(Operation):
    EQUALS = '=='
    NOT_EQUALS = '!='
    GREATER_THAN = '>'
    GREATER_THAN_OR_EQUALS = '>='
    LESS_THAN = '<'
    LESS_THAN_OR_EQUALS = '<='
    EXISTS = 'exists'

    def exec(self,prop1,prop2=None):
        try:
            if self == PropertyOperation.EQUALS:
                return prop1 == prop2
            elif self == PropertyOperation.NOT_EQUALS:
                return prop1 != prop2
            elif self == PropertyOperation.GREATER_THAN:
                return prop1 > prop2
            elif self == PropertyOperation.GREATER_THAN_OR_EQUALS:
                return prop1 >= prop2
            elif self == PropertyOperation.LESS_THAN:
                return prop1 < prop2
            elif self == PropertyOperation.LESS_THAN_OR_EQUALS:
                return prop1 <= prop2
            elif self == PropertyOperation.EXISTS:
                return True
        except TypeError:
            return false

class LTLOperation(Operation):
    NOT = '!'            # [Unary]: Inverts condition.
    NEXT = 'X'           # LTL [Unary]: Condition has to hold at the next state.
    FINALLY = 'F'        # LTL [Unary]: Condition eventually has to hold (somewhere on the subsequent path).
    GLOBALLY = 'G'       # LTL [Unary]: Condition has to hold on the entire subsequent path.
    UNTIL = 'U'          # LTL [Binary]: Condition A has to hold at least until the other condition B becomes true, which must hold at the current or a future position.
    RELEASE = 'R'        # LTL [Binary]: Condition A has to be true until and including the point where another condition B first becomes true; if B never becomes true, A must remain true forever.
    WEAK_UNTIL = 'W'     # LTL [Binary]: Condition A has to hold at least until B; if B never becomes true, A must remain true forever.
    STRONG_RELEASE = 'M' # LTL [Binary]: Condition A has to be true until and including the point where B first becomes true, which must hold at the current or a future position.

class MathOperation(Operation):
    ADD = '+'
    SUBTRACT = '-'
    MULTIPLY = 'x'
    DIVIDE = '/'
    POWER = '^'
    MODULUS = '%'
    CARTESIAN_DISTANCE = 'cartesian_dist'
    ANGULAR_DISTANCE = 'angular_dist'

class SetOperation(Operation):
    UNION = 'U'
    INTERSECTION = 'I'
