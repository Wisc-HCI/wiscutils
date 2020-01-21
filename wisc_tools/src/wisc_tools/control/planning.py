from wisc_tools.geometry import Position, Quaternion, Pose, ModeTrajectory, PoseTrajectory, AnnotationTrajectory
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
        return not (len(self.poses) > 0 or len(self.annotations) > 0 or len(self.modes) > 0)

    def has_pose(self,pose):
        return pose in self.poses.keys()

    def get_pose(self,pose):
        return self.poses.get(pose,None)

    def add_pose(self,pose,value):
        self.poses[pose] = value

    def delete_pose(self,pose):
        del self.poses[pose]

    def has_annotation(self,annotation):
        return annotation in self.annotations.keys()

    def get_annotation(self,annotation):
        return self.annotations.get(annotation,None)

    def add_annotation(self,annotation,value):
        self.annotations[annotation] = value

    def delete_annotation(self,annotation):
        del self.annotations[annotation]

    def has_mode(self,mode):
        return mode in self.modes.keys()

    def get_mode(self,mode):
        return self.modes.get(mode,None)

    def add_mode(self,mode,value):
        self.modes[mode] = value

    def delete_mode(self,mode):
        del self.modes[mode]

class EventController(Sequence):
    '''
    EventController Class.
    Contains a series of events with useful ways of accessing them
    '''
    def __init__(self):
        self.events = []

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

    def get_pose_trajectory(self,pose,current_time,current_pose):
        return PoseTrajectory([{'time':current_time,'pose':curent_pose}]+[{'time':event.time,'pose':event.get_pose(pose)} for event in self.events if event.has_pose(pose)])

    def get_annotation_trajectory(self,annotation,current_time,current_annotation):
        return AnnotationTrajectory([{'time':current_time,'annotation':curent_annotation}]+[{'time':event.time,'annotation':event.get_annotation(annotation)} for event in self.events if event.has_annotation(annotation)])

    def get_all_of_mode(self,mode,current_time,current_mode):
        return ModeTrajectory([{'time':current_time,'mode':curent_mode}]+[{'time':event.time,'mode':event.get_mode(mode)} for event in self.events if event.has_mode(mode)])

    def delete_all_poses_after(self,time,pose):
        [event.delete_pose(pose) for event in self.events if event >= time and event.has_pose(pose)]
        self.events = [event for event in self.events if not event.empty]

    def delete_all_annotations_after(self,time,annotation):
        [event.delete_annotation(annotation) for event in self.events if event >= time and event.has_annotation(annotation)]
        self.events = [event for event in self.events if not event.empty]

    def delete_all_modes_after(self,time,mode):
        [event.delete_mode(mode) for event in self.events if event >= time and event.has_mode(mode)]
        self.events = [event for event in self.events if not event.empty]

    def add_pose_at_time(self,time,pose,value):
        if time in self.times:
            event = self.get_event_at_time(time)
            event.add_pose(pose,value)
        else:
            event = Event(time)
            event.add_pose(pose,value)
            self.events.append(event)
            self.events.sort()

    def add_annotation_at_time(self,time,annotation,value):
        if time in self.times:
            event = self.get_event_at_time(time)
            event.add_annotation(annotation,value)
        else:
            event = Event(time)
            event.add_annotation(annotation,value)
            self.events.append(event)
            self.events.sort()

    def add_mode_at_time(self,time,mode,value):
        if time in self.times:
            event = self.get_event_at_time(time)
            event.add_mode(mode,value)
        else:
            event = Event(time)
            event.add_mode(mode,value)
            self.events.append(event)
            self.events.sort()

    def timestep_to(self,time):
        self.events = [event for event in self.events if event >= time]


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
