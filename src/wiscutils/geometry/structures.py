import numpy as np
from scipy import interpolate
from pyquaternion import Quaternion as pyQuaternion
from util import pairwise
from geometry_msgs.msg import Vector3 as rosVector3
from geometry_msgs.msg import Quaternion as rosQuaternion
from geometry_msgs.msg import Pose as rosPose
from wiscutils.msg import EulerPose

try:
    from relaxed_ik.msg import EEPoseGoals
except:
    from wiscutils.msg import EEPoseGoals


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
        return {"x":self.x,"y":self.y,"z":self.z}

    @classmethod
    def from_ros_vector3(cls,vector3):
        return Position(x=vector3.x,y=vector3.y,z=vector3.z)

class Quaternion(pyQuaternion):

    @property
    def ros_quaternion(self):
        return rosQuaternion(x=self.x,y=self.y,z=self.z,w=self.w)

    @property
    def ros_euler(self):
        (r,p,y) = tf.transformations.euler_from_quaternion(self.ros_quaternion)
        return rosVector3(x=r,y=p,z=y)

    @classmethod
    def from_py_quaternion(self,pyquaternion):
        return Quaternion(x=pyquaterion.x,y=pyquaternion.y,z=pyquaternion.z,w=pyquaternion.w)

    @classmethod
    def from_ros_quaternion(self,quaternion):
        return Quaternion(x=quaterion.x,y=quaternion.y,z=quaternion.z,w=quaternion.w)

    @classmethod
    def from_ros_euler(self,euler,form='sxyz'):
        tf_quat = tf.transformations.quaternion_from_euler(euler.x,euler.y,euler.z,form)
        return Quaternion.from_ros_quaternion(tf_quat)

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
    def from_ros_pose(self,pose):
        return Pose(position=Position.from_ros_vector3(pose.position),orientation=Quaternion.from_ros_quaternion(pose.orientation))


class Waypoint(object):
    def __init__(self, time, pose):
        self.time = time
        self.pose = pose

class Trajectory(object):
    def __init__(self, waypoints):
        self.wps = waypoints

    @property
    def t(self):
        return [wp.time for wp in self.wps]

    @property
    def x(self):
        return [wp.pose.position.x for wp in self.wps]

    @property
    def y(self):
        return [wp.pose.position.y for wp in self.wps]

    @property
    def z(self):
        return [wp.pose.position.z for wp in self.wps]

    @property
    def q(self):
        return [wp.pose.quaternion for wp in self.wps]

    def __getitem__(self,index):
        return self.wps[index]

    def interpolate(self, resolution, circuit=False):
        """interpolate.

        Parameters
        ----------
        resolution : float/int
            The resolution in seconds.
        circuit : type
            Calculate with wraparound, first and last waypoint must have same poses.

        Returns
        -------
        trajectory
            new Trajectory object with specified resolution.

        """
        if len(self.wps) == 0:
            return self
        if not circuit:
            x = interpolate.interp1d(self.t,self.x,kind='cubic')
            y = interpolate.interp1d(self.t,self.y,kind='cubic')
            z = interpolate.interp1d(self.t,self.z,kind='cubic')

        else:
            original = {"t":self.t,"x":self.x,"y":self.y,"z":self.z}
            t = [original["t"][-2]-original["t"][-1]]+self.t+[original["t"][1]+original["t"][-1]]
            xp = [original["x"][-2]-original["x"][-1]]+self.x+[original["x"][1]+original["x"][-1]]
            yp = [original["y"][-2]-original["y"][-1]]+self.y+[original["y"][1]+original["y"][-1]]
            zp = [original["z"][-2]-original["z"][-1]]+self.z+[original["z"][1]+original["z"][-1]]

            x = interpolate.interp1d(t,xp,kind='cubic')
            y = interpolate.interp1d(t,yp,kind='cubic')
            z = interpolate.interp1d(t,zp,kind='cubic')

        total_time = max(self.t)
        indices = np.arange(0,total_time+resolution,resolution)
        x_result = x(indices)
        y_result = y(indices)
        z_result = z(indices)

        quat_results = [self.wps[0]]
        for wp1, wp2 in pairwise(self.wps):
            n = int((wp2.time - wp1.time)/resolution)-1
            quat_results.extend(Quaternion.intermediates(wp1.pose.quaternion,wp2.pose.quaternion,n=n,include_endpoints=False))
            quat_results.append(wp2.pose.quaternion)

        wps = []
        for i in range(0,len(quat_results)):
            wps.append(Waypoint(indices[i],Pose(Position(x_result[i],y_result[i],z_result[i]),
                                                quat_results[i])))
        return Trajectory(wps)