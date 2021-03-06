from __future__ import print_function
from wisc_tools.structures import Mode, Position, Quaternion, Pose, ModeTrajectory, PoseTrajectory, AnnotationTrajectory
from wisc_tools.control import EventController
import rospy
import math
import numpy as np

def serialize(input):
    if isinstance(input, dict):
        return {key:serialize(value) for key,value in input.iteritems()}
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
        return rospy.get_time()

    @property
    def current_serializable(self):
        return serialize(self.current)

    @property
    def future(self):
        return {
            'armData':[self.pose_future(arm,trajectory) for (arm, trajectory) in self.event_controller.arm_trajectories.iteritems()],
            'modeData':[self.mode_future(mode,trajectory) for (mode, trajectory) in self.event_controller.mode_trajectories.iteritems()],
        }

    def new(self, arms, joints, modes, actions, poses, annotations):

        self.current = {'actions':[],'modes':{},'arms':{},'annotations':{},'poses':{}}
        self.arms = arms
        self.joints = joints
        self.modes = modes
        self.actions = actions
        self.annotations = annotations
        self.poses = {}
        for arm, pose in poses.iteritems():
            self.poses[arm] = {pose_name:{'pose':Pose.from_eulerpose_dict(pose_info),'default':pose_info['default']} for (pose_name,pose_info) in pose.iteritems()}
        default_poses = []
        for arm in self.arms:
            for pose,poseinfo in self.poses[arm].iteritems():
                if poseinfo['default']:
                    default_poses.append(poseinfo['pose'].ros_pose)
        print(default_poses)

        self.event_controller = EventController({arm:[info['pose'] for pose,info in poses.iteritems() if info['default']][0] for arm,poses in self.poses.iteritems()},
                                                self.annotations,
                                                self.modes)
        self.initialize()

    def pose_future(self,arm,trajectory):
        now = self.now
        times = list(np.linspace(now, now+5, 10))
        plan = [trajectory[time] for time in times]
        return {
                'name':arm,
                'points':[[point.position.y,point.position.z,point.position.x] for point in plan]
               }
        # return {
        #   'name': arm,
        #   'x': [t.position.x for t in plan],
        #   'y': [t.position.y for t in plan],
        #   'z': [t.position.z for t in plan],
        #   'type': 'scatter3d',
        #   'mode': 'lines+markers',
        #   'line': {'color': [t-now for t in times],
        #            'colorscale': "Viridis"},
        #   'marker': {'color': [t-now for t in times],
        #              'colorscale': "Viridis"}
        # }

    def mode_future(self,mode,trajectory):
        now = self.now
        times = list(np.linspace(now, now+5, 20))
        plan = [trajectory[time] for time in times]
        return {
                'name':mode,
                'values':plan
               }
        # return {
        #   'name': mode,
        #   'x': [t-now for t in times],
        #   'y': plan,
        #   'type': 'scatter',
        #   'opacity': 0.5,
        #   'mode': 'lines+markers'
        # }


    def set_action(self,action):
        # Actions piggyback off poses and modes.
        print('Setting action: {0}'.format(action))
        # Get the time to do the first action, and then specify the offsets based on that
        now = self.now
        times = []
        for arm in self.actions[action].keys():
            current_pose = self.event_controller.arm_trajectories[arm][now]
            goal_pose = self.poses[arm][self.actions[action][arm][0]['pose']]['pose']
            times.append(self.time_to_pose(current_pose,goal_pose))

        # Offset is the max time estimate across arms
        ttp = max(times)

        for arm in self.actions[action].keys():
            current_pose = self.event_controller.arm_trajectories[arm][now]
            goal_pose = self.poses[arm][self.actions[action][arm][0]['pose']]['pose']
            last = None
            for event in self.actions[action][arm]:
                if last is None:
                    self.event_controller.add_pose_at_time(self.now, now + ttp, arm, self.poses[arm][event['pose']]['pose'], self.next_group_id)
                    for e in event['modes']:
                        self.event_controller.add_mode_at_time(self.now, now + ttp, e, self.modes[e]['values'][event['modes'][e]], False, self.next_group_id)
                    for e in event['annotations']:
                        self.event_controller.add_annotation_at_time(self.now, now + ttp, e, event['annotations'][e], self.next_group_id)
                else:
                    self.event_controller.add_pose_at_time(self.now, now + ttp + last['time'], arm, self.poses[arm][event['pose']]['pose'], self.next_group_id)
                    for e in event['modes']:
                        self.event_controller.add_mode_at_time(self.now, now + ttp + last['time'], e, self.modes[e]['values'][event['modes'][e]], False, self.next_group_id)
                    for e in event['annotations']:
                        self.event_controller.add_annotation_at_time(self.now, now + ttp, e, event['annotations'][e], self.next_group_id)
                last = event
        self.next_group_id += 1
        self.timestep()
        [print({'time': event.time, 'poses': event.poses}) for event in self.event_controller.events]

    def set_pose(self,arm,pose,offset=None):
        # Estimate the amount of time needed to get to that pose
        print('Setting pose for {0} to {1}'.format(arm, pose))
        # If offset is none, calculate the time to do the event
        goal_pose = self.poses[arm][pose]['pose']
        current_time = self.now
        current_pose =  self.event_controller.arm_trajectories[arm][current_time]
        if offset == None:
            offset = self.time_to_pose(current_pose,goal_pose)

        # spatial_dist,rotation_dist = self.current['arms'][arm].distance_to(self.poses[arm][pose]['pose'])
        # print('Estimated distance {0}:{1}'.format(spatial_dist,rotation_dist))
        self.event_controller.add_pose_at_time(self.now, self.now+offset, arm, goal_pose, self.next_group_id)
        self.next_group_id += 1
        # [print({'time': event.time, 'poses': event.poses}) for event in self.event_controller.events]
        self.timestep()
        # self.event_controller.add_pose_at_time()

    def set_mode(self,mode,value,offset=None,override=True):
        # Estimate time needed to smoothly apply that mode
        print('Mode',mode)
        print('Value',value)
        print('Override',override)
        current_time = self.now
        current_value =  self.event_controller.mode_trajectories[mode][current_time]
        if value != None:
            goal_value = self.modes[mode]['values'][value]
        else:
            goal_value = current_value

        time_to_mode = self.time_to_mode(current_value,goal_value)
        mode_time = current_time + time_to_mode
        print('Setting mode for {0} to {1} in {2}s'.format(mode, value, time_to_mode))
        if override:
            self.event_controller.add_mode_at_time(current_time,mode_time,mode,goal_value,True, self.next_group_id)
            self.event_controller.set_mode_override(current_time,mode,True)
            #print(self.event_controller.events)
        else:
            self.event_controller.set_mode_override(current_time,mode,False)
        self.timestep()

    def set_annotation(self,annotation,data):
        print('setting annotation {} with {}'.format(annotation, data))
        self.event_controller.add_annotation_at_time(self.now, self.now, annotation, data, self.next_group_id)
        self.next_group_id += 1

    def initialize(self):
        initial = {'actions':[],'modes':{},'arms':{},'annotations':{},'poses':{}}
        for arm in self.arms:
            now = self.now
            defaults = [pose for pose in self.poses[arm].keys() if self.poses[arm][pose]['default']]
            if len(defaults) >= 1:
                initial['arms'][arm] = defaults[0]
            else:
                initial['arms'][arm] = self.poses[arm].keys()[0]
            pose = self.poses[arm][initial['arms'][arm]]['pose']
            self.event_controller.add_pose_at_time(now,now,arm,pose,0)
        for mode in self.modes.keys():
            override = self.modes[mode]['override']
            value = self.modes[mode]['value']
            current_value = self.modes[mode]['values'][value]
            initial['modes'][mode] = {'override':override,'name':value,'value':current_value}
            self.event_controller.add_mode_at_time(now,now,mode,current_value,override,0)
        self.current = initial
        return initial

    def timestep(self):
        time = self.now
        annotations = self.event_controller.timestep_to(time)
        self.current["annotations"] = annotations
        for arm in self.arms:
            try:
                self.current['arms'][arm] = self.event_controller.arm_trajectories[arm][time]
            except:
                print("could not find arm "+arm)
        for mode in self.modes.keys():
            try:
                current = self.event_controller.mode_trajectories[mode][time]
                name = None
                for value_name,value in self.modes[mode]['values'].iteritems():
                    if value == current:
                        name = value_name
                self.current['modes'][mode] = {'override':self.event_controller.mode_overrides[mode],
                                               'name':name,
                                               'value':self.event_controller.mode_trajectories[mode][time]}
            except:
                print("could not find mode "+mode)

        return serialize(self.current)

    @staticmethod
    def time_to_pose(current_pose,goal_pose):
        # return 3;
        spatial_dist, rotational_dist = current_pose.distance_to(goal_pose)
        #print(spatial_dist,rotational_dist)
        t = max([spatial_dist*5,rotational_dist*2])
        #print(t)
        return t + 0.5

    @staticmethod
    def time_to_mode(current_mode,mode_goal):
        # Hard coded for the time being.
        return math.fabs(current_mode-mode_goal)*10 + 0.5
