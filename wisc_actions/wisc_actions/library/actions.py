from wisc_actions.elements import *

## Move
move = Action('move',
              parameters=[
                  # HL Params
                  Term('agent'),
                  Term('arm'),
                  Term('destination'),
                  # LL Params
                  Term('pose_set'),
                  Term('joint_states'),
                  Term('max_velocity'),
                  Term('force'),
                  Term('selection_vector'),
                  Term('constraint_frame')
              ],
              subactions=[
                  # If the pose_set or destination is defined, perform a move_ee

                  # If the joint_states are defined, perform a move_joint


              ],
              preconditions=[

              ],
              postconditions=[

              ])

## Transport
transport = Action('transport',
                   parameters=[

                   ],
                   subactions=[

                   ],
                   preconditions=[

                   ],
                   postconditions=[

                   ])

## Pick
pick = Action('pick',
              parameters=[
                  # HL Params
                  Term('agent'),
                  Term('arm'),
                  Term('object'),
                  # LL Params
                  Term('force'),
                  Term('spacing')
              ],
              subactions=[
                  # Access the poses of the object and agent
                  Assign(Term('object_pose'),Term('object').access('pose')),
                  Assign(Term('agent_pose'),Term('agent').access(Term('pose_state')).access(Term('arm'))),
                  # If the agent isn't there, move.
                  Branch(Condition(Term('object_pose'),Term('agent_pose'),Operation.EQUALS),
                        move.call()),
                  # Grasp the object
                  grasp.call()
              ],
              preconditions=[

              ],
              postconditions=[

              ])

## Place
place = Action('place')



## Insert
insert = Action('insert')

## Screw
screw = Action('screw')

## Wipe
wipe = Action('wipe')
