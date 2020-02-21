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
        return not (len(self.poses) > 0 or len(self.annotations) > 0 or len([mode for mode in self.modes if not mode['value'].empty]) > 0)

    def has_pose(self,pose:str):
        return pose in self.poses.keys()

    def get_pose(self,pose:str):
        pose = self.poses.get(pose,None)
        if pose:
            return pose['value']
        else:
            return None

    def add_pose(self,pose:str,value:Pose,group_id:int):
        self.poses[pose] = {'value': value, 'group_id': group_id}

    def delete_pose(self,pose:str):
        del self.poses[pose]

    def has_annotation(self,annotation:str):
        return annotation in self.annotations.keys()

    def get_annotation(self,annotation:str):
        annotation = self.annotations.get(annotation,None)
        if annotation:
            return annotation['value']
        else:
            return None

    def add_annotation(self,annotation:str,value:str,group_id:int):
        self.annotations[annotation] = {'value':value, 'group_id':group_id}

    def delete_annotation(self,annotation:str):
        del self.annotations[annotation]

    def has_mode(self,mode:str,mode_override:bool):
        if mode_override:
            return mode in self.modes.keys() and self.modes[mode]['value'].has_override
        else:
            return mode in self.modes.keys() and self.modes[mode]['value'].has_deferred

    def get_mode(self,mode:str):
        mode = self.modes.get(mode,None)
        if mode:
            return mode['value']
        else:
            return None

    def add_mode(self,mode:str,value:Mode,mode_override:bool,group_id:int):
        if self.modes.get(mode,False):
            if mode_override:
                self.modes[mode]['value'].override_value = value
            else:
                self.modes[mode]['value'].deferred_value = value
        else:
            if mode_override:
                self.modes[mode] = {'value':Mode(value,None),'group_id':group_id}
            else:
                self.modes[mode] = {'value':Mode(None,value),'group_id':group_id}

    def delete_mode(self,mode):
        del self.modes[mode]

class EventController(Sequence):
    '''
    EventController Class.
    Contains a series of events with useful ways of accessing them
    '''
    def __init__(self,arm_info={},annotation_info={},mode_info={}):
        self.events = []
        self.arm_trajectories = {arm:PoseTrajectory([{'time':0,'pose':pose}]) for arm,pose in arm_info.items()}
        self.annotation_trajectories = {annotation:AnnotationTrajectory([]) for annotation in annotation_info.keys()}
        self.mode_trajectories = {mode:ModeTrajectory([{'time':0,'mode':info['values'][info['value']]}]) for mode,info in mode_info.items()}
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

    def refresh_arm_trajectory(self,current_time:float,arm:str):
        current = [{'time':current_time,'pose':self.arm_trajectories[arm][current_time]}]
        future = [{'time':event.time,'pose':event.get_pose(arm)} for event in self.events if event.has_pose(arm) and event.time > current_time]
        self.arm_trajectories[arm] = PoseTrajectory(current+future)

    def refresh_annotation_trajectory(self,current_time:float,annotation:str):
        current = [{'time':current_time,'annotation':self.annotation_trajectories[annotation][current_time]}]
        future = [{'time':event.time,'annotation':event.get_annotation(annotation)} for event in self.events if event.has_annotation(annotation) and event.time > current_time]
        self.annotation_trajectories[annotation] = AnnotationTrajectory(current+future)

    def refresh_mode_trajectory(self,current_time:float,mode:str):
        current = [{'time':current_time,'mode':self.mode_trajectories[mode][current_time]}]
        if self.mode_overrides[mode]:
            future = [{'time':event.time,'mode':event.get_mode(mode).override_value} for event in self.events if event.has_mode(mode,True) and event.time > current_time]
        else:
            future = [{'time':event.time,'mode':event.get_mode(mode).deferred_value} for event in self.events if event.has_mode(mode,False) and event.time > current_time]
        self.mode_trajectories[mode] = ModeTrajectory(current+future)

    def set_mode_override(self,current_time:float,mode:str,value:bool):
        if self.mode_overrides[mode] != value:
            print('Changing override for {0} to {1}'.format(mode,value))
            self.mode_overrides[mode] = value
            if value:
                self.delete_all_override_modes_after(current_time,mode)
            self.refresh_mode_trajectory(current_time,mode)

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

    def delete_all_override_modes_after(self,time:float,mode:str,refresh:bool=False):
        [event.delete_mode(mode) for event in self.events if event >= time and event.has_mode(mode,True)]
        self.events = [event for event in self.events if not event.empty]

    def delete_all_deferred_modes_after(self,time:float,mode:str):
        [event.delete_mode(mode) for event in self.events if event >= time and event.has_mode(mode,False)]
        self.events = [event for event in self.events if not event.empty]

    def delete_all_poses_with_group_id(self,group_id:int,current_time:float):
        # self.events = [event for event in self.events if not event.group_id == group_id]
        print('deleting all poses with group_id: {}'.format(group_id))
        updated_arms = []
        new_events = []
        for event in self.events:
            new_poses = {}
            for pose in event.poses.keys():
                if event.poses[pose]['group_id'] != group_id:
                    #print(event.poses[pose]['group_id'])
                    if pose not in updated_arms:
                        updated_arms.append(pose)
                    new_poses[pose] = event.poses[pose]
            if len(new_poses) > 0:
                event.poses = new_poses
                new_events.append(event)
        self.events = new_events
        for arm in updated_arms:
            self.refresh_arm_trajectory(current_time,arm)

    def add_pose_at_time(self,current_time:float,time:float,arm:str,value:Pose,group_id:int):
        if time in self.times:
            event = self.get_event_at_time(time)

            if(event.poses.get(arm, None) is not None):
                self.delete_all_poses_with_group_id(event.poses[arm]['group_id'], current_time)
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
        self.refresh_arm_trajectory(current_time,arm)

    def add_annotation_at_time(self,current_time:float,time:float,annotation:str,value:str,group_id:int):
        if time in self.times:
            event = self.get_event_at_time(time)
            event.add_annotation(annotation,value,group_id)
        else:
            event = Event(time)
            event.add_annotation(annotation,value,group_id)
            self.events.append(event)
            self.events.sort()
        self.refresh_annotation_trajectory(current_time,annotation)

    def add_mode_at_time(self,current_time:float,time:float,mode:str,value:str,override:bool,group_id:int):
        if time in self.times:
            print('Time exists, adding to event')
            event = self.get_event_at_time(time)
            event.add_mode(mode,value,override,group_id)
        else:
            print('Creating new event')
            event = Event(time)
            event.add_mode(mode,value,override,group_id)
            self.events.append(event)
            self.events.sort()
        self.refresh_mode_trajectory(current_time,mode)

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
