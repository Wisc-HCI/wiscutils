from wisc_actions.elements import *

## Move EE To Position
move_ee = Primitive('move_ee',[Term('agent'),
                               Term('pose_states'),
                               Term('max_velocity')])

## Move Joint
move_joint = Primitive('move_joint',[Term('agent'),
                                     Term('joint_states'),
                                     Term('max_velocity')])

## Move to Contact
move_to_contact = Primitive('move_to_contact',[Term('agent'),
                                               Term('arm'),
                                               Term('force'),
                                               Term('selection_vector'),
                                               Term('constraint_frame')])

## Grasp
grasp = Primitive('grasp',[Term('agent'),
                           Term('arm'),
                           Term('force'),
                           Term('spacing'),
                           Term('max_velocity')])

## Release
release = Primitive('release',[Term('agent'),
                               Term('arm'),
                               Term('spacing'),
                               Term('max_velocity')])


## Move Force (e.g. Push)
move_force = Primitive('move_force',[Term('agent'),
                                     Term('arm'),
                                     Term('force'),
                                     Term('selection_vector'),
                                     Term('constraint_frame')])

## Hole Search
hole_search = Primitive('hole_search',[Term('agent'),
                                       Term('arm'),
                                       Term('plane'),
                                       Term('force'),
                                       Term('delta_z'),
                                       Term('delta_f'),
                                       Term('strategy')])
