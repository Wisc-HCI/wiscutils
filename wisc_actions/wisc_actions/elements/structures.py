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
    from sensor_msgs.msg import JointState as rosJointState
    HAS_ROS = True
except:
    warnings.warn('ROS is not loaded. Exporting to ROS messages is not supported.',Warning)
    HAS_ROS = False
from abc import abstractmethod
from .base import WiscBase

class Structure(WiscBase):

    @property
    def serialized(self):
        return self.dict

class Position(Structure):

    keys = [{'x','y','z'}]

    def __init__(self,x,y,z):
        self.x = x
        self.y = y
        self.z = z

    @property
    def serialized(self):
        return self.dict

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
    def load(cls,data,context=[]):
        return Position(data['x'],data['y'],data['z'])

    def distance_to(self,other):
        return math.sqrt(math.pow(self.x-other.x,2)+math.pow(self.y-other.y,2)+math.pow(self.z-other.z,2))

    def __repr__(self):
        return '[x:{0},y:{1},z:{2}]'.format(self.x,self.y,self.z)

class Orientation(pyQuaternion,Structure):

    keys = [{'r','p','y'},{'w','x','y','z'}]

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
    def load(self,dict,context=[]):
        if {'r','p','y'}.issubset(set(dict.keys())):
            return from_euler_dict(dict)
        elif {'w','x','y','z'}.issubset(set(dict.keys())):
            return from_dict(dict)


    def distance_to(self,other):
        return pyQuaternion.distance(self,other)

class Pose(Structure):

    keys = [{'position','orientation'}]

    def __init__(self,position,orientation):
        self.position = position
        self.orientation = orientation

    @property
    def ros_pose(self):
        return rosPose(position=self.position.ros_point,orientation=self.orientation.ros_quaternion)

    @property
    def ros_eulerpose(self):
        return EulerPose(position=self.position.ros_point,orientation=self.orientation.ros_euler)

    @classmethod
    def from_ros_eulerpose(self,eulerpose):
        pass

    @classmethod
    def from_eulerpose_dict(cls,dict):
        position = Position(**dict['position'])
        quaternion = Orientation.from_euler_dict(dict['orientation'])
        return cls(position,quaternion)

    @classmethod
    def from_pose_dict(cls,dict):
        position = Position(**dict['position'])
        quaternion = Orientation(**dict['orientation'])
        return cls(position,quaternion)

    @classmethod
    def from_ros_pose(self,pose):
        return Pose(position=Position.from_ros_point(pose.position),orientation=Quaternion.from_ros_quaternion(pose.orientation))

    @property
    def dict(self):
        return {'position':self.position.dict,'orientation':self.orientation.dict}

    @property
    def quaternion_dict(self):
        return {'position':self.position.dict,'orientation':{'w':self.orientation.w,'x':self.orientation.x,'y':self.orientation.y,'z':self.orientation.z}}

    def distance_to(self,pose):
        return (self.position.distance_to(pose.position),self.orientation.distance_to(pose.orientation))

    def __repr__(self):
        return '({0}, {1})'.format(self.position,self.orientation)

    @classmethod
    def load(cls,data,context=[]):
        return Pose(Position.load(data['position']),Orientation.load(data['orientation']))

class JointStates(Structure):

    keys = [{'joint_names','joint_values'}]

    def __init__(self,joint_names,joint_values):
        self.joint_names = joint_names
        self.joint_lookup = {}
        for i,name in enumerate(joint_names):
            self.joint_lookup[name] = joint_values[i]

    @property
    def dict(self):
        result = {'joint_names':[],'joint_values':[]}
        for name,value in self.joint_lookup.items():
            result['joint_names'].append(name)
            result['joint_values'].append(value)
        return result

    @classmethod
    def load(cls,data,context=[]):
        return JointStates(joint_names=data['joint_names'],
                           joint_values=data['joint_values'])

    @property
    def ros_joint_state(self):
        serialized = self.dict
        return rosJointState(name=serialized['joint_names'],position=serialized['joint_values'])

    def __getattr__(self,attr):
        try:
            super(JointStates,self).__getattr__(attr)
        except:
            if isinstance(attr,int):
                return self.joint_lookup[self.joint_names[attr]]
            else:
                return self.joint_lookup[attr]

class PoseSet(Structure):

    keys = [{'pose_names','pose_values'}]

    def __init__(self,pose_names,pose_values):
        self.pose_names = pose_names
        self.pose_lookup = {}
        for i,name in enumerate(pose_names):
            self.pose_lookup[name] = pose_values[i]

    @property
    def dict(self):
        result = {'pose_names':[],'pose_values':[]}
        for name,value in self.pose_lookup.items():
            result['pose_names'].append(name)
            result['pose_values'].append(value)
        return result

    @classmethod
    def load(cls,data,context=[]):
        return PoseSet(pose_names=data['pose_names'],
                       pose_values=data['pose_values'])

    def __getattr__(self,attr):
        try:
            super(PoseSet,self).__getattr__(attr)
        except:
            if isinstance(attr,int):
                return self.pose_lookup[self.pose_names[attr]]
            else:
                return self.pose_lookup[attr]

class Enumerable(Structure):

    keys = [{'items'}]

    def __init__(self,items):
        self.items = items

    def __len__(self):
        return len(self.items)

    def __iter__(self):
        return self.items.__iter__()

    def __getitem__(self,i):
        return self.items[i]

    def append(self,item):
        self.items.append(item)

    @property
    def serialized(self):
        # Note, this probably shouldn't be serialized.
        return {'items':[self.serialize(item) for item in self.items]}

    @classmethod
    def load(cls,data,context=[]):
        # Note, this probably shouldn't be loaded.
        return Enumerable([WiscBase.parse([Position,Orientation,Pose],item,context) for item in data['items']])


class Vector(WiscBase):
    pass

class Mesh(WiscBase):
    pass

class Trajectory(WiscBase):

    keys = [{'kind','wps','circuit'}]

    def __init__(self,waypoints,kind=3,method='univariate_spline',circuit=False,min_value=None,max_value=None):
        self.wps = waypoints
        self.kind = kind
        self.circuit = circuit
        self.min_value = min_value
        self.max_Value = max_value
        self.method = method
        self.__interpolate__()

    @property
    def serialized(self):
        # Note, this probably shouldn't be serialized.
        return {'kind':self.kind,'circuit':self.circuit,'wps':[self.serialize(item) for item in self.wps]}

    @classmethod
    def load(cls,data,context=[]):
        # Note, this probably shouldn't be loaded.
        return Trajectory([])

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
        return '[{0}]'.format(','.join([str(wp) for wp in self.wps]))

class ModeTrajectory(Trajectory):

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
            if self.method == 'univariate_spline':
                self.vfn = interpolate.InterpolatedUnivariateSpline(t,v,k=self.kind,ext='const')
            else:
                self.vfn = interpolate.interp1d(t,v,kind=self.kind,fill_value='extrapolate')
        else:
            tp = [t[-2]-t[-1]]+t+[t[1]+t[-1]]
            vp = [v[-2]-v[-1]]+v+[v[1]+v[-1]]
            if self.method == 'univariate_spline':
                self.vfn = interpolate.InterpolatedUnivariateSpline(t,v,k=self.kind,ext='const')
            else:
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
        return self.__pad__([wp['pose'].orientation for wp in self.wps])

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
            quat = self.wps[0]['pose'].orientation
        elif time > stop:
            quat = self.wps[-1]['pose'].orientation
        else:
            for start_idx,pair in enumerate(pairwise(times)):
                if pair[0] <= time <= pair[1]:
                    quat1 = q[start_idx]
                    quat2 = q[start_idx+1]
                    quat_times = (pair[0],pair[1])
            percent = (time - quat_times[0]) / (quat_times[1] - quat_times[0])
            quat = Orientation.from_py_quaternion(pyQuaternion.slerp(quat1,quat2,percent))
        return Pose(pos,quat)

    def __interpolate__(self):
        assert len(self.wps) > 0
        times = self.t
        if not self.circuit:
            if self.method == 'univariate_spline':
                self.xfn = interpolate.InterpolatedUnivariateSpline(times,self.x,k=self.kind,ext='const')
                self.yfn = interpolate.InterpolatedUnivariateSpline(times,self.y,k=self.kind,ext='const')
                self.zfn = interpolate.InterpolatedUnivariateSpline(times,self.z,k=self.kind,ext='const')
            else:
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
            if self.method == 'univariate_spline':
                self.xfn = interpolate.InterpolatedUnivariateSpline(tp,xp,k=self.kind,ext='const')
                self.yfn = interpolate.InterpolatedUnivariateSpline(tp,yp,k=self.kind,ext='const')
                self.zfn = interpolate.InterpolatedUnivariateSpline(tp,zp,k=self.kind,ext='const')
            else:
                self.xfn = interpolate.interp1d(tp,xp,kind=self.kind,fill_value='extrapolate')
                self.yfn = interpolate.interp1d(tp,yp,kind=self.kind,fill_value='extrapolate')
                self.zfn = interpolate.interp1d(tp,zp,kind=self.kind,fill_value='extrapolate')
