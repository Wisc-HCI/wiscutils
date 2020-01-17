import tf

from wisc_msgs.msg import EulerPose, EEPoseGoals
import geometry_msgs.msg.Vector3 as rosVector3
import geometry_msgs.msg.Quaternion as rosQuaternion
import pyquaternion
from wisc_tools.geometry import *

#===============================================================================
#       Position Message Conversion
#===============================================================================

def position_msgFromDict(dct):
    return rosVector3(x=dct['x'],y=dct['y'],z=dct['z'])

def position_dictFromMsg(msg):
    return {'x':msg.x,'y':msg.y,'z':msg.z}

#===============================================================================
#       Orientation Message Conversion
#===============================================================================

def orientation_eulerMsgFromQuaterionMsg(qmsg):
    tf_quat == orientation_tfFromQuaternionMsg(qmsg)
    (r,p,y) = tf.transformations.euler_from_quaternion(tf_quat)
    return rosVector3(x=r,y=p,z=y)

def orientation_quaterionMsgFromEulerMsg(emsg, form='sxyz'):
    tf_quat = tf.transformations.quaternion_from_euler(emsg.x,emsg.y,emsg.z,form)
    return orientation_quaternionMsgFromTf(tf_quat)

def orientation_eulerMsgFromEulerDict(dct):
    return rosVector3(x=dct['x'],y=dct['y'],z=dct['z'])

def orientation_quaterionMsgFromQuaternionDict(dct):
    return rosQuaternion(x=dct['x'],y=dct['y'],z=dct['z'],w=dct['w'])

def orientation_eulerDictFromEulerMsg(msg):
    return {'x':msg.x, 'y':msg.y, 'z':msg.z}

def orientation_eulerDictFromQuaternionMsg(qmsg):
    tf_quat == orientation_tfFromQuaternionMsg(qmsg)
    (r,p,y) = tf.transformations.euler_from_quaternion(tf_quat)
    return {'x':r, 'y':p, 'z':y}

def orientation_quaternionDictFromEulerMsg(emsg, form='sxyz'):
    tf_quat = tf.transformations.quaternion_from_euler(emsg.x,emsg.y,emsg.z,form)
    return orientation_quaternionDictFromTf(tf_quat)

def orientation_eulerMsgFromQuaternionDict(dct):
    tf_quat = orientation_tfFromQuaternionDict(dct)
    (r,p,y) = tf.transformations.euler_from_quaternion(tf_quat)
    return rosVector3(x=r,y=p,z=y)

def orientation_quaternionMsgFromEulerDict(dct, form='sxyz'):
    tf_quat = tf.transformations.quaternion_from_euler(dct['x'],dct['y'],dct['z'],form)
    return orientation_quaternionMsgFromTf(tf_quat)

def orientation_quaternionDictFromQuaternionMsg(msg):
    return {'x':msg.x, 'y':msg.y, 'z':msg.z, 'w':msg.w}

def orientation_quaternionDictFromEulerDict(dct, form='sxyz'):
    tf_quat = tf.transformations.quaternion_from_euler(dct['x'],dct['y'],dct['z'],form)
    return orientation_quaternionDictFromTf(tf_quat)

def orientation_eulerDictFromQuaternionDict(dct):
    tf_quat = orientation_tfFromQuaternionDict(dct)
    (r,p,y) = tf.transformations.euler_from_quaternion(tf_quat)
    return {'x':r, 'y':p, 'z':y}

#===============================================================================
#       Pose Message Conversion
#===============================================================================

def pose_eulerMsgFromQuaternionMsg(qmsg):
    return EulerPose(position=qmsg.position,
                     orientation=orientation_eulerMsgFromQuaterionMsg(qmsg.orientation))

def pose_eulerMsgFromEulerDict(dct):
    return EulerPose(position=position_msgFromDict(dct['position']),
                     orientation=orientation_eulerMsgFromEulerDict(dct['orientation']))

def pose_quaternionMsgFromEulerMsg(emsg, form='sxyz'):
    return Pose(position=emsg.position,
                orientation=orientation_quaterionMsgFromEulerMsg(emsg.orientation,form))

def pose_quaternionMsgFromQuaternionDict(dct):
    return Pose(position=position_msgFromDict(dct['position']),
                orientation=orientation_quaterionMsgFromQuaternionDict(dct['orientation']))

def pose_eulerDictFromEulerMsg(msg):
    return {
        'position': position_dictFromMsg(msg.position),
        'orientation': orientation_eulerDictFromEulerMsg(msg.orientation)
    }

def pose_quaternionDictFromQuaterionMsg(msg):
    return {
        'position': position_dictFromMsg(msg.position),
        'orientation': orientation_quaternionDictFromQuaternionMsg(msg.orientation)
    }

def pose_eulerDictFromQuaternionDict(dct):
    return {
        'position': dct['position'],
        'orientation': orientation_eulerDictFromQuaternionDict(dct['orientation'])
    }

def pose_quaternionDictFromEulerDict(dct, form='sxyz'):
    return {
        'position': dct['position'],
        'orientation': orientation_quaternionDictFromEulerDict(dct['orientation'],form)
    }

def pose_eulerDictFromQuaternionMsg(msg):
    return {
        'position': position_dictFromMsg(msg.position),
        'orientation': orientation_eulerDictFromQuaternionMsg(msg.orientation)
    }

def pose_quaternionDictFromEulerMsg(msg, form='sxyz'):
    return {
        'position': position_dictFromMsg(msg.position),
        'orientation': orientation_quaternionDictFromEulerMsg(msg.orientation,form)
    }

def pose_eulerMsgFromQuaternionDict(dct):
    EulerPose(position=position_msgFromDict(dct['position']),
              orientation=orientation_eulerMsgFromQuaternionDict(dct['orientation']))

def pose_quaternionMsgFromEulerDict(dct, form='sxyz'):
    return Pose(position=position_msgFromDict(dct['position']),
                orientation=orientation_quaternionMsgFromEulerDict(dct['orientation'],form))

#===============================================================================
#       Position to Tf Conversion
#===============================================================================

def position_tfFromDict(dct):
    return [dct['x'],dct['y'],dct['z']]

def position_tfFromMsg(msg):
    return [msg.x,msg.y,msg.z]

def position_dictFromTf(t):
    return {'x':t[0], 'y':t[1], 'z':[2]}

def position_msgFromTf(t):
    return rosVector3(x=t[0],y=t[1],z=t[2])

#===============================================================================
#       Orientation to Tf Conversion
#===============================================================================

def orientation_tfFromQuaternionDict(dct):
    return [dct['x'],dct['y'],dct['z'],dct['w']]

def orientation_tfFromQuaternionMsg(msg):
    return [msg.x,msg.y,msg.z,msg.w]

def orientation_quaternionDictFromTf(t):
    return {'x':t[0], 'y':t[1], 'z':t[2], 'w':t[3]}

def orientation_quaternionMsgFromTf(t):
    return rosQuaternion(x=t[0], y=t[1], z=t[2], w=t[3])

#===============================================================================
#       Pose to Tf Conversion
#===============================================================================

def pose_tfFromQuaternionDict(dct):
    return pos, rot

def pose_tfFromQuaternionMsg(msg):
    pos = position_tfFromMsg(msg.position)
    rot = orientation_tfFromQuaternionMsg(msg.orientation)
    return pos, rot

def pose_quaternionDictFromTf(pos,rot):
    return {
        'position': position_dictFromTf(pos),
        'orientation': orientation_quaternionDictFromTf(rot)
    }

def pose_quaternionMsgFromTf(pos,rot):
    return Pose(position=position_msgFromTf(pos),
                orientation=orientation_quaternionMsgFromTf(rot))
