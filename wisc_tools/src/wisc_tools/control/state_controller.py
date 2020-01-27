from wisc_tools.structures import Mode, Position, Quaternion, Pose, ModeTrajectory, PoseTrajectory, AnnotationTrajectory
from wisc_tools.control import EventController
from rclpy.duration import Duration
import math

class StateController(object):
    '''
    Generic StateController Object.
    Handles updates to goals, modes, annotations, and actions
    '''
    def __init__(self, rosnode, arms=[], joints=[], modes={}, actions={}, poses={}, annotations={}):
        self.rosnode = rosnode
        self.new(arms, joints, modes, actions, poses, annotations)

    @property
    def now(self):
        return self.rosnode.get_clock().now()

    def new(self, arms, joints, modes, actions, poses, annotations):
        self.event_controller = EventController(modes)
        self.current = {}
        self.arms = arms
        self.joints = joints
        self.modes = modes
        self.actions = actions
        self.annotations = annotations
        self.poses = {}
        for arm, pose in poses.items():
            self.poses[arm] = {pose_name:{'pose':Pose.from_eulerpose_dict(pose_info),'default':pose_info['default']} for (pose_name,pose_info) in pose.items()}
        self.initialize()


    def set_action(self,action):
        # Actions piggyback off poses and modes.
        print('Setting action: {0}'.format(action))
        # Get the time to do the first action, and then specify the offsets based on that
        ttp = self.time_to_pose(action)
        # runs self.set_mode(with override=False)

    def set_pose(self,arm,pose,offset=None):
        # Estimate the amount of time needed to get to that pose
        print('Setting pose for {0} to {1}'.format(arm, pose))
        # If offset is none, calculate the time to do the event
        spatial_dist,rotation_dist = self.current['arms'][arm].distance_to(self.poses[arm][pose]['pose'])
        print('Estimated distance {0}:{1}'.format(spatial_dist,rotation_dist))

    def set_mode(self,mode,value,offset=None,override=True):
        # Estimate time needed to smoothly apply that mode
        current_value =  self.modes[mode]['values'][self.current['modes'][mode]['current']]
        goal_value = self.modes[mode]['values'][value]
        time_to_mode = self.time_to_mode(current_value,goal_value)
        mode_time = float((self.now+time_to_mode).nanoseconds) / 10**9
        print('Setting mode for {0} to {1} in {2}'.format(mode, value, time_to_mode))
        if override and value == 'defer':
            self.event_controller.set_mode_override(self.now.nanoseconds / 10**9,mode,False)
        elif override:
            self.event_controller.add_mode_at_time(mode_time,mode,value,True)
            self.event_controller.set_mode_override(self.now.nanoseconds / 10**9,mode,True)
        else:
            self.event_controller.add_mode_at_time(mode_time,mode,value,False)

    def cancel_pose(self,arm):
        pass

    def cancel_annotation(self,annotation):
        pass

    def initialize(self):
        initial = {'actions':[],'modes':{},'arms':{},'annotations':{}}
        for arm in self.arms:
            defaults = [pose for pose in self.poses[arm].keys() if self.poses[arm][pose]['default']]
            if len(defaults) >= 1:
                initial['arms'][arm] = defaults[0]
            else:
                initial['arms'][arm] = self.poses[arm].keys()[0]
            self.event_controller.add_pose_at_time(self.now,arm,self.poses[arm][initial['arms'][arm]])
        for mode in self.modes.keys():
            initial['modes'][mode] = {'defer':self.modes[mode]['default'] == 'defer','current':self.modes[mode]['initial']}
        self.current = initial
        return initial

    def timestep(self):
        time = float(self.now.nanoseconds) / 10**9
        annotations = self.event_controller.timestep_to(time)
        self.current["annotations"] = annotations
        for arm in self.arms:
            self.current['arms'][arm] = self.event_controller.arm_trajectories[arm][time]
        for mode in self.modes.keys():
            self.current['modes'][mode] = self.event_controller.mode_trajectories[mode][time]
        return self.current

    @staticmethod
    def time_to_pose(current_pose,goal_pose):
        # Hard coded for the time being.
        return 0

    @staticmethod
    def time_to_mode(current_mode,mode_goal):
        # Hard coded for the time being.
        return Duration(seconds=math.fabs(current_mode-mode_goal)*10)

    @staticmethod
    def events_to_multiarm_trajectory(self,events):
        return None
