from wiscutils.interpolation import Position, Pose, Quaternion, Waypoint, Trajectory
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d


if __name__ == "__main__":

    wps =[
        Waypoint(0,Pose(Position(0,0,0),Quaternion(1,0,0,0))),
        Waypoint(2,Pose(Position(2,1,0),Quaternion(1,0,0,0))),
        Waypoint(6,Pose(Position(2,2,1),Quaternion(1,0,0,0))),
        Waypoint(9,Pose(Position(1,2,2),Quaternion(1,0,0,0))),
        Waypoint(11,Pose(Position(2,3,1),Quaternion(1,0,0,0))),
        Waypoint(13,Pose(Position(1,2,1),Quaternion(1,0,0,0))),
        Waypoint(14,Pose(Position(0,1,0),Quaternion(1,0,0,0))),
        Waypoint(15,Pose(Position(0,0,0),Quaternion(1,0,0,0)))
    ]

    goal = Trajectory(wps)
    traj = goal.interpolate(.1,circuit=True)
    ax = plt.axes(projection='3d')
    ax.scatter(goal.x, goal.y, goal.z, marker='o')
    ax.scatter(traj.x, traj.y, traj.z, marker='.',linewidths=0.1)
    plt.show()
