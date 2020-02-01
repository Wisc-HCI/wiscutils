from wisc_tools.structures import Mode, Position, Quaternion, Pose, ModeTrajectory, PoseTrajectory, AnnotationTrajectory
from collections.abc import Sequence

class Event(object):
    '''
    Event Class.
    Contains information on poses, annotations, and modes
    '''

    def __init__(self, time):
        self.time = time
        self.poses = {}
        self.annotations = {}
        self.modes = {}

    def __lt__(self,other):
        if hasattr(other,'time'):
            return self.time < other.time
        elif hasattr(other,'nanoseconds'):
            return self.time < float(other.nanoseconds) / 10**9
        else:
            return self.time < other

    def __le__(self,other):
        if hasattr(other,'time'):
            return self.time <= other.time
        elif hasattr(other,'nanoseconds'):
            return self.time <= float(other.nanoseconds) / 10**9
        else:
            return self.time <= other

    def __gt__(self,other):
        if hasattr(other,'time'):
            return self.time > other.time
        elif hasattr(other,'nanoseconds'):
            return self.time > float(other.nanoseconds) / 10**9
        else:
            return self.time > other

    def __ge__(self,other):
        if hasattr(other,'time'):
            return self.time >= other.time
        elif hasattr(other,'nanoseconds'):
            return self.time >= float(other.nanoseconds) / 10**9
        else:
            return self.time >= other

    def __repr__(self):
        return '\n\tposes:{0}, \n\tmodes:{1}, \n\tannotations:{1}'.format(self.poses,self.modes,self.annotations)

    @property
    def empty(self):
        return not (len(self.poses) > 0 or len(self.annotations) > 0 or len([mode for mode in self.modes if not mode.empty]) > 0)

    def has_pose(self,pose:str):
        return pose in self.poses.keys()

    def get_pose(self,pose:str):
        pose = self.poses.get(pose,None)
        if pose:
            return pose['value']
        else:
            return None

    def add_pose(self,pose,value,group_id):
        self.poses[pose] = {'value': value, 'group_id': group_id}

    def delete_pose(self,pose:str):
        del self.poses[pose]

    def has_annotation(self,annotation:str):
        return annotation in self.annotations.keys()

    def get_annotation(self,annotation:str):
        return self.annotations.get(annotation,None)

    def add_annotation(self,annotation:str,value:str):
        self.annotations[annotation] = value

    def delete_annotation(self,annotation:str):
        del self.annotations[annotation]

    def has_mode(self,mode:str,mode_override:bool):
        if mode_override:
            return mode in self.modes.keys() and self.modes[mode].has_override
        else:
            return mode in self.modes.keys() and self.modes[mode].has_deferred

    def get_mode(self,mode:str):
        return self.modes.get(mode,None)

    def add_mode(self,mode:str,value:Mode,mode_override:bool):
        if self.modes.get(mode,False):
            if mode_override:
                self.modes[mode].override_value = value
            else:
                self.modes[mode].deferred_value = value
        else:
            if mode_override:
                self.modes[mode] = Mode(value,None)
            else:
                self.modes[mode] = Mode(None,value)

    def delete_mode(self,mode):
        del self.modes[mode]

class EventController(Sequence):
    '''
    EventController Class.
    Contains a series of events with useful ways of accessing them
    '''
    def __init__(self,mode_info={}):
        self.events = []
        self.arm_trajectories = {}
        self.annotation_trajectories = {}
        self.mode_trajectories = {}
        self.mode_overrides = {mode:info['override'] for mode,info in mode_info.items()}
        self.mode_thresholds = {mode:(min([value for key,value in info['values'].items()]),
                                      max([value for key,value in info['values'].items()])) for mode,info in mode_info.items()}

    def __len__(self):
        t = self.times
        minimum = min(t)
        maximum = max(t)
        return max-min

    def __iter__(self):
        return self.events.__iter__()

    def __getitem__(self,time:float):
        return self.get_event_at_time(time)

    @property
    def times(self):
        return [event.time for event in self.events]

    def get_event_at_time(self,time:float):
        return next((e for e in self.events if e.time == time), None)

    def get_arm_trajectory(self,arm:str,current_time:float):
        try:
            current = [self.arm_trajectories[arm][current_time]]
        except:
            current = []
        poses = PoseTrajectory(current+[{'time':event.time,'pose':event.get_pose(arm)} for event in self.events if event.has_pose(arm)])
        self.arm_trajectories[arm] = poses
        return poses

    def get_annotation_trajectory(self,annotation:str,current_time:float):
        try:
            current = [self.annotation_trajectories[annotation][current_time]]
        except:
            current = []
        annotations = AnnotationTrajectory(current+[{'time':event.time,'annotation':event.get_annotation(annotation)} for event in self.events if event.has_annotation(annotation)])
        self.annotation_trajectories[annotation] = annotations
        return annotations

    def get_mode_trajectory(self,mode:str,current_time:float):
        try:
            current = [{'time':current_time,'mode':self.mode_trajectories[mode][current_time]}]
        except:
            current = []
        if self.mode_overrides[mode]:
            future = [{'time':event.time,'mode':event.get_mode(mode).override_value} for event in self.events if event.has_mode(mode,True)]
        else:
            future = [{'time':event.time,'mode':event.get_mode(mode).deferred_value} for event in self.events if event.has_mode(mode,False)]
        modes = ModeTrajectory(current+future)
        self.mode_trajectories[mode] = modes
        return modes

    def set_mode_override(self,current_time:float,mode:str,value:bool):
        if mode not in self.mode_overrides.keys() or self.mode_overrides[mode] != value:
            print('Changing override for {0} to {1}'.format(mode,value))
            self.mode_overrides[mode] = value
            try:
                current = [self.mode_trajectories[mode][current_time]]
            except:
                current = []
            if value:
                self.delete_all_override_modes_after(current_time,mode)
            print('adding mode {0}'.format(mode))
            self.get_mode_trajectory(mode,current_time)

    def delete_all_poses_after(self,time:float,arm:str):
        [event.delete_pose(arm) for event in self.events if event >= time and event.has_pose(arm)]
        self.events = [event for event in self.events if not event.empty]

    def delete_all_annotations_after(self,time:float,annotation:str):
        [event.delete_annotation(annotation) for event in self.events if event >= time and event.has_annotation(annotation)]
        self.events = [event for event in self.events if not event.empty]

    def delete_all_modes_after(self,time:float,mode:str):
        [event.delete_mode(mode) for event in self.events if event >= time and event.has_mode(mode,True)]
        [event.delete_mode(mode) for event in self.events if event >= time and event.has_mode(mode,False)]
        self.events = [event for event in self.events if not event.empty]

    def delete_all_override_modes_after(self,time:float,mode:str):
        [event.delete_mode(mode) for event in self.events if event >= time and event.has_mode(mode,True)]
        self.events = [event for event in self.events if not event.empty]

    def delete_all_deferred_modes_after(self,time:float,mode:str):
        [event.delete_mode(mode) for event in self.events if event >= time and event.has_mode(mode,False)]
        self.events = [event for event in self.events if not event.empty]

    def delete_all_poses_with_group_id(self,group_id):
        # self.events = [event for event in self.events if not event.group_id == group_id]
        print('deleting all poses with group_id: {}'.format(group_id))
        new_events = []
        for event in self.events:
            new_poses = {}
            for pose in event.poses.keys():
                if event.poses[pose]['group_id'] != group_id:
                    print(event.poses[pose]['group_id'])
                    new_poses[pose] = event.poses[pose]
            if len(new_poses) > 0:
                event.poses = new_poses
                new_events.append(event)
        self.events = new_events

    def add_pose_at_time(self,time:float,arm:str,value:Pose,group_id:int):
        if time in self.times:
            event = self.get_event_at_time(time)

            if(event.poses.get(arm, None) is not None):
                self.delete_all_poses_with_group_id(event.poses[arm]['group_id'])
                event = self.get_event_at_time(time)
                if event is None:
                    event = Event(time)
                    event.add_pose(arm,value,group_id)
                    self.events.append(event)
                    self.events.sort()
                else:
                    event.add_pose(arm,value,group_id)
            else:
                event.add_pose(arm,value,group_id)
        else:
            event = Event(time)
            event.add_pose(arm,value,group_id)
            self.events.append(event)
            self.events.sort()

    def add_annotation_at_time(self,time:float,annotation:str,value:str):
        if time in self.times:
            event = self.get_event_at_time(time)
            event.add_annotation(annotation,value)
        else:
            event = Event(time)
            event.add_annotation(annotation,value)
            self.events.append(event)
            self.events.sort()

    def add_mode_at_time(self,time:float,mode:str,value:str,override:bool):
        if time in self.times:
            print('Time exists, adding to event')
            event = self.get_event_at_time(time)
            event.add_mode(mode,value,override)
        else:
            print('Creating new event')
            event = Event(time)
            event.add_mode(mode,value,override)
            self.events.append(event)
            self.events.sort()
        print(self.events)
        self.get_mode_trajectory(mode,time)

    def timestep_to(self,time:float):
        # TODO: Capture any annotations that are queued
        annotations = {annotation:[event.get_annotation(annotation) for event in self.events if event <= time and event.has_annotation(annotation)] for annotation in self.annotation_trajectories.keys()}
        self.events = [event for event in self.events if event >= time]
        return annotations


if __name__ == '__main__':
    controller = EventController()
    controller.add_pose_at_time(1,'test_pose',Pose.from_eulerpose_dict({'position':{'x':0,'y':0,'z':0},'rotation':{'r':0,'p':0,'y':0}}))
    controller.add_annotation_at_time(1,'test_annotation','Annotation')
    controller.add_mode_at_time(2,'test_mode',2)
    controller.add_mode_at_time(4,'test_mode',1)
    print(len(controller))
    print(controller[1].poses)
    print(controller.get_all_of_mode('test_mode'))
    controller.timestep_to(3)
    print(len(controller))
