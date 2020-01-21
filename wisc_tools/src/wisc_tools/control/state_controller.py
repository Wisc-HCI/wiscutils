from wisc_tools.geometry import Position, Quaternion, Pose, ModeTrajectory, PoseTrajectory, AnnotationTrajectory
from wisc_tools.control import EventController

class StateController(object):
    '''
    Generic StateController Object.
    Handles updates to goals, modes, and actions
    '''
    def __init__(self, rosnode, arms=[], joints=[], modes={}, actions={}, poses={}, annotatons={}):
        self.rosnode = rosnode
        self.new(arms, joints, modes, actions, poses, annotations)

    @property
    def current(self):
        now = self.now
        state = {'arms':{},
                 'annotations':{},
                 'modes':{}
                }
        for arm in self.poses.keys():
            state['arms'][arm] = self.arm_trajectories[arm][self.now]
        for annotation in self.annotations.keys():
            state['annotations'] = self.annotation_trajectories[annotation][self.now]
        for mode in self.modes.keys():
            state['modes'] = self.mode_trajectories[mode][self.now]
        return state

    @property
    def now(self):
        return self.rosnode.get_clock().now()

    def new(self, arms, joints, modes, actions, poses, annotations):
        self.event_controller = EventController()
        self.arms = arms
        self.joints = joints
        self.modes = modes
        self.actions = actions
        self.annotations = annotations
        self.poses = {}
        self.arm_trajectories = {}
        self.annotation_trajectories = {}
        self.mode_trajectories = {}
        for arm, pose in poses.items():
            self.poses[arm] = {pose_name:{'pose':Pose.from_eulerpose_dict(pose_info),'default':pose_info['default']} for (pose_name,pose_info) in pose.items()}


    def set_action(self,action):
        # Actions piggyback off poses and modes.
        print('Setting action: {0}'.format(action))
        # Get the time to do the first action, and then specify the offsets based on that
        ttp = self.time_to_pose(action)

    def set_pose(self,arm,pose,offset=None):
        # Estimate the amount of time needed to get to that pose
        print('Setting pose for {0} to {1}'.format(arm, pose))
        # If offset is none, calculate the time to do the event
        spatial_dist,rotation_dist = self.current['arms'][arm].distance_to(self.poses[arm][pose]['pose'])
        print('Estimated distance {0}:{1}'.format(spatial_dist,rotation_dist))

    def set_mode(self,mode,value,offset=None):
        # Estimate time needed to smoothly apply that mode
        print('Setting mode for {0} to {1}'.format(mode, value))
        # If offset is none, calculate the time to do the event

    def cancel_pose(self,arm):
        pass

    def cancel_annotation(self,annotation):
        pass

    def cancel_mode(self,mode):
        pass

    def timestep(self):
        self.event_controller.timestep_to(self.now)

    def get_initial(self):
        initial = {'actions':[],'modes':{},'poses':{}}
        for arm in self.arms:
            defaults = [pose for pose in self.poses[arm].keys() if self.poses[arm][pose]['default']]
            if len(defaults) >= 1:
                initial['poses'][arm] = defaults[0]
            else:
                initial['poses'][arm] = self.poses[arm].keys()[0]
        for mode in self.modes.keys():
            initial['modes'][mode] = {'defer':self.modes[mode]['default'] == 'defer','current':self.modes[mode]['initial']}
        return initial

    def step(self):
        self.timestep()
        return {}

    @staticmethod
    def time_to_pose(current_pose,goal_pose):
        # Hard coded for the time being.
        return 0

    @staticmethod
    def time_to_mode(current_mode,mode_goal):
        # Hard coded for the time being.
        return 0

    @staticmethod
    def events_to_multiarm_trajectory(self,events):
        return None
