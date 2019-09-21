import numpy as np
from scipy import interpolate
from pyquaternion import Quaternion
from util import pairwise

class Position(object):
    def __init__(self,x,y,z):
        self.x = x
        self.y = y
        self.z = z

class Pose(object):
    def __init__(self,position,quaternion):
        self.position = position
        self.quaternion = quaternion

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
