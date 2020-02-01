from wisc_tools.structures import Mode, Position, Quaternion, Pose, ModeTrajectory, PoseTrajectory, AnnotationTrajectory
from wisc_tools.control import EventController
from rclpy.duration import Duration
import math

def serialize(input):
    if isinstance(input, dict):
        return {key:serialize(value) for key,value in input.items()}
    elif isinstance(input, list):
        return [serialize(element) for element in input]
    elif isinstance(input, Pose):
        return input.dict
    else:
        return input

class StateController(object):
    '''
    Generic StateController Object.
    Handles updates to goals, modes, annotations, and actions
    '''

    next_group_id = 0

    def __init__(self, rosnode, arms=[], joints=[], modes={}, actions={}, poses={}, annotations={}):
        self.rosnode = rosnode
        self.new(arms, joints, modes, actions, poses, annotations)

    @property
    def now(self):
        return self.rosnode.get_clock().now()

    @property
    def current_serializable(self):
        return serialize(self.current)

    def new(self, arms, joints, modes, actions, poses, annotations):
        self.event_controller = EventController(modes)
        self.current = {'actions':[],'modes':{},'arms':{},'annotations':{},'poses':{}}
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
        ttp = self.time_to_pose(action,None)

        for arm in self.actions[action].keys():
            last = None
            for event in self.actions[action][arm]:
                if last is None:
                    self.event_controller.add_pose_at_time(ttp, arm, event['pose'], self.next_group_id)
                else:
                    self.event_controller.add_pose_at_time(ttp + last['time'], arm, event['pose'], self.next_group_id)
                last = event
        self.next_group_id += 1
        self.timestep()
        #[print({'time': event.time, 'poses': event.poses}) for event in self.event_controller.events]

    def set_pose(self,arm,pose,offset=None):
        # Estimate the amount of time needed to get to that pose
        print('Setting pose for {0} to {1}'.format(arm, pose))
        # If offset is none, calculate the time to do the event
        # spatial_dist,rotation_dist = self.current['arms'][arm].distance_to(self.poses[arm][pose]['pose'])
        # print('Estimated distance {0}:{1}'.format(spatial_dist,rotation_dist))
        self.event_controller.add_pose_at_time(0, arm, pose, self.next_group_id)
        self.next_group_id += 1
        [print({'time': event.time, 'poses': event.poses}) for event in self.event_controller.events]
        self.timestep()
        # self.event_controller.add_pose_at_time()

    def set_mode(self,mode,value,offset=None,override=True):
        # Estimate time needed to smoothly apply that mode
        current_time = float(self.now.nanoseconds) * 10**-9
        current_value =  self.event_controller.mode_trajectories[mode][current_time]
        goal_value = self.modes[mode]['values'][value]
        time_to_mode = self.time_to_mode(current_value,goal_value)
        mode_time = current_time + time_to_mode
        print('Setting mode for {0} to {1} in {2}s'.format(mode, value, time_to_mode))
        if override:
            self.event_controller.add_mode_at_time(mode_time,mode,goal_value,True)
            self.event_controller.set_mode_override(current_time,mode,True)
            #print(self.event_controller.events)
        else:
            self.event_controller.set_mode_override(current_time,mode,False)
        self.timestep()

    def cancel_pose(self,arm):
        pass

    def cancel_annotation(self,annotation):
        pass

    def initialize(self):
        initial = {'actions':[],'modes':{},'arms':{},'annotations':{},'poses':{}}
        for arm in self.arms:
            now = float(self.now.nanoseconds) * 10**-9
            defaults = [pose for pose in self.poses[arm].keys() if self.poses[arm][pose]['default']]
            if len(defaults) >= 1:
                initial['arms'][arm] = defaults[0]
            else:
                initial['arms'][arm] = self.poses[arm].keys()[0]
            pose = self.poses[arm][initial['arms'][arm]]['pose']
            self.event_controller.add_pose_at_time(now,arm,pose,0)
            self.event_controller.get_arm_trajectory(arm,now)
        for mode in self.modes.keys():
            override = self.modes[mode]['override']
            value = self.modes[mode]['value']
            current_value = self.modes[mode]['values'][value]
            initial['modes'][mode] = {'override':override,'name':value,'value':current_value}
            self.event_controller.add_mode_at_time(now,mode,current_value,override)
        self.current = initial
        return initial

    def timestep(self):
        time = float(self.now.nanoseconds) * 10**-9
        annotations = self.event_controller.timestep_to(time)
        self.current["annotations"] = annotations
        for arm in self.arms:
            self.current['arms'][arm] = self.event_controller.arm_trajectories[arm][time]
        for mode in self.modes.keys():
            current = self.event_controller.mode_trajectories[mode][time]
            name = None
            for value_name,value in self.modes[mode]['values'].items():
                if value == current:
                    name = value_name
            self.current['modes'][mode] = {'override':self.event_controller.mode_overrides[mode],
                                           'name':name,
                                           'value':self.event_controller.mode_trajectories[mode][time]}

        return serialize(self.current)

    @staticmethod
    def time_to_pose(current_pose,goal_pose):
        # Hard coded for the time being.
        return 0

    @staticmethod
    def time_to_mode(current_mode,mode_goal):
        # Hard coded for the time being.
        return math.fabs(current_mode-mode_goal)*10

    @staticmethod
    def events_to_multiarm_trajectory(self,events):
        return None
