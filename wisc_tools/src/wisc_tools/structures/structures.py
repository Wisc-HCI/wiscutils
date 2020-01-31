import numpy as np
import math
from scipy import interpolate
from pyquaternion import Quaternion as pyQuaternion
from wisc_tools.convenience import pairwise
from wisc_tools.conversions import transformations
from wisc_msgs.msg import Euler, EulerPose, EEPoseGoals
from geometry_msgs.msg import Vector3 as rosVector3
from geometry_msgs.msg import Quaternion as rosQuaternion
from geometry_msgs.msg import Pose as rosPose
from abc import ABC, abstractmethod

class Mode(object):
    '''
    Mode Class
    Itty bitty mode object that handles override and deferred values
    '''
    def __init__(self, override_value=None, deferred_value=None):
        self.deferred_value = deferred_value
        self.override_value = override_value

    @property
    def empty(self):
        return self.override_value == None and self.deferred_value == None

    @property
    def has_override(self):
        return self.override_value != None

    @property
    def has_deferred(self):
        return self.deferred_value != None

class Position(object):
    def __init__(self,x,y,z):
        self.x = x
        self.y = y
        self.z = z

    @property
    def ros_vector3(self):
        return rosVector3(x=self.x,y=self.y,z=self.z)

    @property
    def array(self):
        return np.array([self.x,self.y,self.z])

    @property
    def dict(self):
        return {'x':self.x,'y':self.y,'z':self.z}

    @classmethod
    def from_ros_vector3(cls,vector3):
        return Position(x=vector3.x,y=vector3.y,z=vector3.z)

    def distance_to(self,other):
        return math.sqrt(math.pow(self.x-other.x,2)+math.pow(self.y-other.y,2)+math.pow(self.z-other.z,2))

class Quaternion(pyQuaternion):

    @property
    def ros_quaternion(self):
        return rosQuaternion(x=self.x,y=self.y,z=self.z,w=self.w)

    @property
    def ros_euler(self):
        (r,p,y) = transformations.euler_from_quaternion(self.ros_quaternion)
        return Euler(r=r,p=p,y=y)

    @classmethod
    def from_vector_quaternion(self,vector):
        return Quaternion(w=vector[0],x=vector[1],y=vector[2],z=vector[3])

    @classmethod
    def from_py_quaternion(self,pyquaternion):
        return Quaternion(x=pyquaternion.x,y=pyquaternion.y,z=pyquaternion.z,w=pyquaternion.w)

    @classmethod
    def from_ros_quaternion(self,quaternion):
        return Quaternion(x=quaternion.x,y=quaternion.y,z=quaternion.z,w=quaternion.w)

    @classmethod
    def from_ros_euler(self,euler):
        tf_quat = transformations.quaternion_from_euler(euler.r,euler.p,euler.y,'szyx')
        return Quaternion.from_vector_quaternion(tf_quat)

    @classmethod
    def from_euler_dict(self,dict):
        tf_quat = transformations.quaternion_from_euler(dict['r'],dict['p'],dict['y'])
        return Quaternion.from_vector_quaternion(tf_quat)

    def distance_to(self,other):
        return pyQuaternion.distance(self,other)

class Pose(object):
    def __init__(self,position,quaternion):
        self.position = position
        self.quaternion = quaternion

    @property
    def ros_pose(self):
        return rosPose(position=self.position.ros_vector3,orientation=self.quaternion.ros_quaternion)

    @property
    def ros_eulerpose(self):
        return EulerPose(position=self.position.ros_vector3,orientation=self.orientation.ros_euler)

    @classmethod
    def from_ros_eulerpose(self,eulerpose):
        pass

    @classmethod
    def from_eulerpose_dict(cls,dict):
        position = Position(**dict['position'])
        quaternion = Quaternion.from_euler_dict(dict['rotation'])
        return cls(position,quaternion)

    @classmethod
    def from_pose_dict(cls,dict):
        position = Position(**dict['position'])
        quaternion = Quaternion(**dict['quaternion'])
        return cls(position,quaternion)

    @classmethod
    def from_ros_pose(self,pose):
        return Pose(position=Position.from_ros_vector3(pose.position),orientation=Quaternion.from_ros_quaternion(pose.orientation))

    def distance_to(self,pose):
        return (self.position.distance_to(pose.position),self.quaternion.distance_to(pose.quaternion))

class Trajectory(ABC):

    def __init__(self,waypoints,kind='cubic',circuit=False,min_value=None,max_value=None):
        self.wps = waypoints
        self.kind = kind
        self.circuit = circuit
        self.min_value = min_value
        self.max_Value = max_value
        self.__interpolate__()

    @property
    def t(self):
        if len(self.wps) < 4:
            base = self.wps[0]['time']
            return [base-15,base-10,base-5] + [wp['time'] for wp in self.wps]
        else:
            return [wp['time'] for wp in self.wps]

    def __len__(self):
        t = self.t
        start = min(t)
        stop = max(t)
        return stop-start

    def __pad__(self,vals):
        if len(vals) < 4:
            return [vals[0],vals[0],vals[0]] + vals
        else:
            return vals

    def __iter__(self):
        return self.wps.__iter__()

    @abstractmethod
    def __filter__(self,value):
        return value

    @abstractmethod
    def __interpolate__(self):
        pass

class ModeTrajectory(Trajectory):

    def __init__(self,waypoints,fill='interpolate',kind='cubic',circuit=False,min_value=None,max_value=None):
        self.fill = fill
        super(ModeTrajectory,self).__init__(waypoints,kind='cubic',circuit=False,min_value=None,max_value=None)

    @property
    def v(self):
        return [wp['mode'] for wp in self.wps]

    def __getitem__(self,time):
        if self.circuit:
            start = min(self.t)
            time = time - start % (len(self) + start)
        return self.__filter__(self.vfn(time))

    def __filter__(self,value):
        if self.min_value != None and self.min_value > value:
            return self.min_value
        elif self.max_value != None and self.max_value < value:
            return self.max_value
        else:
            return value

    def __interpolate__(self):
        assert len(self.wps) > 0
        t = self.t
        v = self.v
        if not self.circuit:
            self.vfn = interpolate.interp1d(t,v,kind=self.kind,fill_value='extrapolate')
        else:
            tp = [t[-2]-t[-1]]+t+[t[1]+t[-1]]
            vp = [v[-2]-v[-1]]+v+[v[1]+v[-1]]
            self.vfn = interpolate.interp1d(tp,vp,kind=self.kind,fill_value='extrapolate')

class AnnotationTrajectory(Trajectory):

    @property
    def a(self):
        return [wp['annotation'] for wp in self.wps]

    def __getitem__(self,time):
        if self.circuit:
            start = min(self.t)
            time = time - start % (len(self) + start)
        if time in self.t:
            return [event['annotation'] for event in self.wps][0]
        else:
            return None

    def __filter__(self,value):
        return value

    def __interpolate__(self):
        pass


class PoseTrajectory(Trajectory):

    @property
    def x(self):
        return self.__pad__([wp['pose'].position.x for wp in self.wps])

    @property
    def y(self):
        return self.__pad__([wp['pose'].position.y for wp in self.wps])

    @property
    def z(self):
        return self.__pad__([wp['pose'].position.z for wp in self.wps])

    @property
    def q(self):
        return self.__pad__([wp['pose'].quaternion for wp in self.wps])

    def __filter__(self,value):
        return value

    def __getitem__(self,time):
        times = self.t
        if self.circuit:
            start = min(times)
            time = time - start % (len(self) + start)
        x = self.__filter__(self.xfn(time))
        y = self.__filter__(self.yfn(time))
        z = self.__filter__(self.zfn(time))

        pos = Position(x,y,z)

        start = min(times)
        stop = max(times)
        if time < start:
            quat = self.wps[0]['pose'].quaternion
        elif time > stop:
            quat = self.wps[-1]['pose'].quaternion
        else:
            for start_idx,pair in enumerate(pairwise(times)):
                if pair[0] <= time <= pair[1]:
                    quat1 = self.wps[start_idx]['pose'].quaternion
                    quat2 = self.wps[start_idx+1]['pose'].quaternion
                    quat_times = (self.wps[start_idx]['time'],self.wps[start_idx+1]['time'])
                percent = (time - quat_times[0]) / (quat_times[1] - quat_times[0])
                quat = Quaternion.from_py_quaternion(pyQuaternion.slerp(quat1,quat2,percent))
        return Pose(pos,quat)

    def __interpolate__(self):
        assert len(self.wps) > 0
        times = self.t
        if not self.circuit:
            self.xfn = interpolate.interp1d(times,self.x,kind=self.kind,fill_value='extrapolate')
            self.yfn = interpolate.interp1d(times,self.y,kind=self.kind,fill_value='extrapolate')
            self.zfn = interpolate.interp1d(times,self.z,kind=self.kind,fill_value='extrapolate')
        else:
            xs = self.x
            ys = self.y
            zs = self.z
            tp = [times[-2]-times[-1]]+t+[times[1]+times[-1]]
            xp = [xs[-2]-xs[-1]]+xs+[xs[1]+xs[-1]]
            yp = [ys[-2]-ys[-1]]+ys+[ys[1]+ys[-1]]
            zp = [zs[-2]-zs[-1]]+zs+[zs[1]+zs[-1]]

            self.xfn = interpolate.interp1d(tp,xp,kind=self.kind,fill_value='extrapolate')
            self.yfn = interpolate.interp1d(tp,yp,kind=self.kind,fill_value='extrapolate')
            self.zfn = interpolate.interp1d(tp,zp,kind=self.kind,fill_value='extrapolate')
