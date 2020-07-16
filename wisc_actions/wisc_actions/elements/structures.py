import numpy as np
import math
import warnings
from scipy import interpolate
from pyquaternion import Quaternion as pyQuaternion
from more_itertools import pairwise
try:
    from wisc_tools.conversions import transformations
    from wisc_msgs.msg import Euler, EulerPose, EEPoseGoals
    from geometry_msgs.msg import Vector3 as rosVector3
    from geometry_msgs.msg import Point as rosPoint
    from geometry_msgs.msg import Quaternion as rosQuaternion
    from geometry_msgs.msg import Pose as rosPose
    HAS_ROS = True
except:
    warnings.warn('ROS is not loaded. Exporting to ROS messages is not supported.',Warning)
    HAS_ROS = False
from abc import ABC, abstractmethod
from .base import WiscBase

class Position(WiscBase):

    keys = [set(('x','y','z'))]

    def __init__(self,x,y,z):
        self.x = x
        self.y = y
        self.z = z

    @property
    def serialized(self):
        return {'x':self.x,'y':self.y,'z':self.z}

    @property
    def ros_vector3(self):
        assert HAS_ROS, 'This method requires ROS'
        return rosVector3(x=self.x,y=self.y,z=self.z)

    @property
    def ros_point(self):
        assert HAS_ROS, 'This method requires ROS'
        return rosPoint(x=self.x,y=self.y,z=self.z)

    @property
    def array(self):
        return np.array([self.x,self.y,self.z])

    @property
    def dict(self):
        return {'x':self.x,'y':self.y,'z':self.z}

    @classmethod
    def from_ros_vector3(cls,vector3):
        return Position(x=vector3.x,y=vector3.y,z=vector3.z)

    @classmethod
    def from_ros_point(cls,point):
        return Position(x=point.x,y=point.y,z=point.z)

    @classmethod
    def load(cls,data):
        return Position(data['x'],data['y'],data['z'])

    def distance_to(self,other):
        return math.sqrt(math.pow(self.x-other.x,2)+math.pow(self.y-other.y,2)+math.pow(self.z-other.z,2))

    def __repr__(self):
        return '[x:{0},y:{1},z:{2}]'.format(self.x,self.y,self.z)

class Orientation(pyQuaternion,WiscBase):

    keys = [set(('r','p','y')),set(('w','x','y','z'))]

    @property
    def ros_quaternion(self):
        assert HAS_ROS, 'This method requires ROS'
        return rosQuaternion(x=self.x,y=self.y,z=self.z,w=self.w)

    @property
    def ros_euler(self):
        assert HAS_ROS, 'This method requires ROS'
        (r,p,y) = transformations.euler_from_quaternion([self.w,self.x,self.y,self.z],'szxy')
        return Euler(r=r,p=p,y=y)

    @property
    def dict(self):
        assert HAS_ROS, 'This method requires ROS'
        (r,p,y) = transformations.euler_from_quaternion([self.w,self.x,self.y,self.z],'szxy')
        return {'r':r,'p':p,'y':y}

    @property
    def serialize(self):
        return self.dict

    @classmethod
    def from_vector_quaternion(self,vector):
        return Orientation(w=vector[0],x=vector[1],y=vector[2],z=vector[3])

    @classmethod
    def from_py_quaternion(self,pyquaternion):
        return Orientation(x=pyquaternion.x,y=pyquaternion.y,z=pyquaternion.z,w=pyquaternion.w)

    @classmethod
    def from_ros_quaternion(self,quaternion):
        return Orientation(x=quaternion.x,y=quaternion.y,z=quaternion.z,w=quaternion.w)

    @classmethod
    def from_ros_euler(self,euler):
        assert HAS_ROS, 'This method requires ROS'
        tf_quat = transformations.quaternion_from_euler(euler.r,euler.p,euler.y,'szxy')
        return Orientation.from_vector_quaternion(tf_quat)

    @classmethod
    def from_euler_dict(self,dict):
        assert HAS_ROS, 'This method requires ROS'
        tf_quat = transformations.quaternion_from_euler(dict['r'],dict['p'],dict['y'],'szxy')
        return Orientation.from_vector_quaternion(tf_quat)

    @classmethod
    def from_dict(self,dict):
        return Orientation(w=dict['w'],x=dict['z'],y=dict['y'],z=dict['z'])

    @classmethod
    def load(self,dict):
        if set(('r','p','y')).issubset(set(dict.keys())):
            return from_euler_dict(dict)
        elif set(('w','x','y','z')).issubset(set(dict.keys())):
            return from_dict(dict)


    def distance_to(self,other):
        return pyQuaternion.distance(self,other)

class Pose(WiscBase):

    keys = [set(('position','orientation'))]

    def __init__(self,position,orientation):
        self.position = position
        self.orientation = orientation

    @property
    def ros_pose(self):
        return rosPose(position=self.position.ros_point,orientation=self.quaternion.ros_quaternion)

    @property
    def ros_eulerpose(self):
        return EulerPose(position=self.position.ros_point,orientation=self.orientation.ros_euler)

    @classmethod
    def from_ros_eulerpose(self,eulerpose):
        pass

    @classmethod
    def from_eulerpose_dict(cls,dict):
        position = Position(**dict['position'])
        quaternion = Quaternion.from_euler_dict(dict['orientation'])
        return cls(position,quaternion)

    @classmethod
    def from_pose_dict(cls,dict):
        position = Position(**dict['position'])
        quaternion = Quaternion(**dict['orientation'])
        return cls(position,quaternion)

    @classmethod
    def from_ros_pose(self,pose):
        return Pose(position=Position.from_ros_point(pose.position),orientation=Quaternion.from_ros_quaternion(pose.orientation))

    @property
    def dict(self):
        return {'position':self.position.dict,'orientation':self.quaternion.dict}

    def distance_to(self,pose):
        return (self.position.distance_to(pose.position),self.quaternion.distance_to(pose.orientation))

    def __repr__(self):
        return '({0}, {1})'.format(self.position,self.quaternion)

class Vector(WiscBase):
    pass

class Mesh(WiscBase):
    pass

class Trajectory(ABC,WiscBase):

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
            return [base-20,base-15,base-10,base-5] + [wp['time'] for wp in self.wps] + [self.wps[-1]['time']+5, self.wps[-1]['time']+10, self.wps[-1]['time']+15]
        else:
            return [wp['time'] for wp in self.wps] + [self.wps[-1]['time']+5, self.wps[-1]['time']+10, self.wps[-1]['time']+15]

    def __len__(self):
        t = self.t
        start = min(t)
        stop = max(t)
        return stop-start

    def __pad__(self,vals):
        if len(vals) < 4:
            return [vals[0],vals[0],vals[0],vals[0]] + vals + [vals[-1],vals[-1],vals[-1]]
        else:
            return vals + [vals[-1],vals[-1],vals[-1]]

    def __iter__(self):
        return self.wps.__iter__()

    @abstractmethod
    def __filter__(self,value):
        return value

    @abstractmethod
    def __interpolate__(self):
        pass

    def __repr__(self):
        return '[{0}]'.format(','.join(self.wps))

class ModeTrajectory(Trajectory,WiscBase):

    def __init__(self,waypoints,fill='interpolate',kind='cubic',circuit=False,min_value=None,max_value=None):
        super(ModeTrajectory,self).__init__(waypoints,kind='cubic',circuit=False,min_value=None,max_value=None)

    @property
    def v(self):
        return self.__pad__([wp['mode'] for wp in self.wps])

    def __getitem__(self,time):
        if self.circuit:
            start = min(self.t)
            time = time - start % (len(self) + start)
        return self.__filter__(self.vfn(time))

    def __filter__(self,value):
        if type(value) == np.ndarray:
            value = float(value)
        if min(self.v) > value:
            return min(self.v)
        elif max(self.v) < value:
            return max(self.v)
        else:
            return value

    def __interpolate__(self):
        assert len(self.wps) > 0
        t = self.t
        v = self.v
        if not self.circuit:
            #self.vfn = interpolate.interp1d(t,v,kind=self.kind,fill_value='extrapolate')
            self.vfn = interpolate.UnivariateSpline(t,v,ext='const')
        else:
            tp = [t[-2]-t[-1]]+t+[t[1]+t[-1]]
            vp = [v[-2]-v[-1]]+v+[v[1]+v[-1]]
            self.vfn = interpolate.UnivariateSpline(t,v,ext='const')
            #self.vfn = interpolate.interp1d(tp,vp,kind=self.kind,fill_value='extrapolate')

class AnnotationTrajectory(Trajectory,WiscBase):

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


class PoseTrajectory(Trajectory,WiscBase):

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
        if type(value) == np.ndarray:
            value = float(value)
        return value

    def __getitem__(self,time):
        times = self.t
        if self.circuit:
            start = min(times)
            time = time - start % (len(self) + start)
        x = self.__filter__(self.xfn(time))
        y = self.__filter__(self.yfn(time))
        z = self.__filter__(self.zfn(time))
        q = self.q
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
                    quat1 = q[start_idx]
                    quat2 = q[start_idx+1]
                    quat_times = (pair[0],pair[1])
            percent = (time - quat_times[0]) / (quat_times[1] - quat_times[0])
            quat = Quaternion.from_py_quaternion(pyQuaternion.slerp(quat1,quat2,percent))
        return Pose(pos,quat)

    def __interpolate__(self):
        assert len(self.wps) > 0
        times = self.t
        if not self.circuit:
            # self.xfn = interpolate.interp1d(times,self.x,kind=self.kind,fill_value='extrapolate')
            # self.yfn = interpolate.interp1d(times,self.y,kind=self.kind,fill_value='extrapolate')
            # self.zfn = interpolate.interp1d(times,self.z,kind=self.kind,fill_value='extrapolate')
            # TODO: Test whether the code below produces better results
            self.xfn = interpolate.UnivariateSpline(times,self.x,ext='const')
            self.yfn = interpolate.UnivariateSpline(times,self.y,ext='const')
            self.zfn = interpolate.UnivariateSpline(times,self.z,ext='const')
        else:
            xs = self.x
            ys = self.y
            zs = self.z
            tp = [times[-2]-times[-1]]+t+[times[1]+times[-1]]
            xp = [xs[-2]-xs[-1]]+xs+[xs[1]+xs[-1]]
            yp = [ys[-2]-ys[-1]]+ys+[ys[1]+ys[-1]]
            zp = [zs[-2]-zs[-1]]+zs+[zs[1]+zs[-1]]
            self.xfn = interpolate.UnivariateSpline(tp,xp,ext='const')
            self.yfn = interpolate.UnivariateSpline(tp,yp,ext='const')
            self.zfn = interpolate.UnivariateSpline(tp,zp,ext='const')
