from std_msgs.msg import ColorRGBA

#===============================================================================
#       Color Message Conversion
#===============================================================================

def color_msgFromDict(dct):
    # assuming range from 0 to 1
    alpha = dct['a'] if 'a' in dct.keys() else 1
    return ColorRGBA(r=dct['r'],g=dct['g'],b=dct['b'],a=alpha)

def color_dictFromMsg(msg):
    return { 'r': msg.r, 'g': msg.g, 'b': msg.b, 'a': msg.a }
