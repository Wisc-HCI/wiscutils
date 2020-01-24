from wisc_tools.structures import Mode, Position, Quaternion, Pose, ModeTrajectory, PoseTrajectory, AnnotationTrajectory
from collections.abc import Sequence
from rclpy.time import Time

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
        else:
            return self.time < other

    def __le__(self,other):
        if hasattr(other,'time'):
            return self.time <= other.time
        else:
            return self.time <= other

    def __gt__(self,other):
        if hasattr(other,'time'):
            return self.time > other.time
        else:
            return self.time > other

    def __ge__(self,other):
        if hasattr(other,'time'):
            return self.time >= other.time
        else:
            return self.time >= other

    @property
    def empty(self):
        return not (len(self.poses) > 0 or len(self.annotations) > 0 or len([mode for mode in self.modes if not mode.empty]) > 0)

    def has_pose(self,pose:str):
        return pose in self.poses.keys()

    def get_pose(self,pose:str):
        return self.poses.get(pose,None)

    def add_pose(self,pose:str,value:Pose):
        self.poses[pose] = value

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
        self.mode_overrides = {mode:info['initial']!='defer' for mode,info in mode_info.items()}
        self.mode_thresholds = {mode:(min([value for key,value in info['values'].items()]),
                                      max([value for key,value in info['values'].items()])) for mode,info in mode_info.items()}

    def __len__(self):
        t = self.times
        minimum = min(t)
        maximum = max(t)
        return max-min

    def __iter__(self):
        return self.events.__iter__()

    def __getitem__(self,time):
        return self.get_event_at_time(time)

    @property
    def times(self):
        return [event.time for event in self.events]

    def get_event_at_time(self,time):
        return next((e for e in self.events if e.time == time), None)

    def get_arm_trajectory(self,arm,current_time:Time):
        try:
            current = [self.arm_trajectories[arm][current_time]]
        except:
            current = []
        poses = PoseTrajectory(current+[{'time':event.time,'pose':event.get_pose(arm)} for event in self.events if event.has_pose(arm)])
        self.arm_trajectories[arm] = poses
        return poses

    def get_annotation_trajectory(self,annotation,current_time:Time):
        try:
            current = [self.annotation_trajectories[annotation][current_time]]
        except:
            current = []
        annotations = AnnotationTrajectory(current+[{'time':event.time,'annotation':event.get_annotation(annotation)} for event in self.events if event.has_annotation(annotation)])
        self.annotation_trajectories[annotation] = annotations
        return annotations

    def get_mode_trajectory(self,mode,current_time:Time):
        try:
            current = [self.mode_trajectories[mode][current_time]]
        except:
            current = []
        if self.mode_overrides[mode]:
            future = [{'time':event.time,'mode':event.get_mode(mode).override_value} for event in self.events if event.has_mode(mode,True)]
        else:
            future = [{'time':event.time,'mode':event.get_mode(mode).deferred_value} for event in self.events if event.has_mode(mode,False)]
        modes = ModeTrajectory(current+future)
        self.mode_trajectories[mode] = modes
        return modes

    def set_mode_override(self,current_time:Time,mode:str,value:bool):
        if mode not in self.mode_overrides.keys() or self.mode_overrides[mode] != value:
            self.mode_overrides[mode] = value
            if value:
                self.delete_all_override_modes_after(current_time,mode)
            self.mode_trajectories[mode] = ModeTrajectory(current+[{'time':event.time,'mode':event.get_mode(mode)} for event in self.events if event.has_mode(mode,self.mode_overrides[mode])])

    def delete_all_poses_after(self,time,arm):
        [event.delete_pose(arm) for event in self.events if event >= time and event.has_pose(arm)]
        self.events = [event for event in self.events if not event.empty]

    def delete_all_annotations_after(self,time,annotation):
        [event.delete_annotation(annotation) for event in self.events if event >= time and event.has_annotation(annotation)]
        self.events = [event for event in self.events if not event.empty]

    def delete_all_modes_after(self,time,mode):
        [event.delete_mode(mode) for event in self.events if event >= time and event.has_mode(mode,True)]
        [event.delete_mode(mode) for event in self.events if event >= time and event.has_mode(mode,False)]
        self.events = [event for event in self.events if not event.empty]

    def delete_all_override_modes_after(self,time,mode):
        [event.delete_mode(mode) for event in self.events if event >= time and event.has_mode(mode,True)]
        self.events = [event for event in self.events if not event.empty]

    def delete_all_deferred_modes_after(self,time,mode):
        [event.delete_mode(mode) for event in self.events if event >= time and event.has_mode(mode,False)]
        self.events = [event for event in self.events if not event.empty]

    def add_pose_at_time(self,time:Time,arm,value):
        if time in self.times:
            event = self.get_event_at_time(time)
            event.add_pose(arm,value)
        else:
            event = Event(time)
            event.add_pose(arm,value)
            self.events.append(event)
            self.events.sort()

    def add_annotation_at_time(self,time:Time,annotation,value):
        if time in self.times:
            event = self.get_event_at_time(time)
            event.add_annotation(annotation,value)
        else:
            event = Event(time)
            event.add_annotation(annotation,value)
            self.events.append(event)
            self.events.sort()

    def add_mode_at_time(self,time:Time,mode:str,value:str,override:bool):
        if time in self.times:
            event = self.get_event_at_time(time)
            event.add_mode(mode,value,override)
        else:
            event = Event(time)
            event.add_mode(mode,value,override)
            self.events.append(event)
            self.events.sort()

    def timestep_to(self,time:Time):
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
