
example_action_1a = {
    '_id':'5f0f29848cb32182289ebc29',
    'name':'Grasp (Enforced Agent=Panda)',
    'parameters':['agent','object'],
    'definitions':[{'name':'force_value',
                    'item':'object',
                    'property':'grasping_force',
                    'fallback':0},
                   {'name':'priority',
                    'value':0},
                   {'name':'grip_spacing',
                    'value':None}],
    'subactions':[{'id':'5f0f29928cb32182289ebc2a','parameters':{'force':'force_value','spacing':'grip_spacing','agent':'agent','priority':'priority'}}],
    'preconditions':[{'thing':'agent','property'{'name':'model','value':'Panda'},'operation':'=='}],
    'postconditions':[{'thing':'agent','property':{'name':'grasp_state','value':'closed'},'operation':'=='}],
}

example_action_1b = {
    '_id':'5f1b2eb44ad66e28348447a7',
    'name':'Grasp (Enforced Agent=UR3)',
    'parameters':['agent','object'],
    'definitions':[{'name':'force_value',
                    'item':'object',
                    'property':'grasping_force',
                    'fallback':0},
                   {'name':'priority',
                    'value':0},
                   {'name':'grip_spacing',
                    'value':None}],
    'subactions':[{'id':'5f1b317e4ad66e28348447a9','parameters':{'force':'force_value','spacing':'grip_spacing','agent':'agent','priority':'priority'}}],
    'preconditions':[{'thing':'agent','property'{'name':'model','value':'UR3'},'operation':'=='}],
    'postconditions':[{'thing':'agent','property':{'name':'grasp_state','value':'closed'},'operation':'=='}],
}


example_action_2 = {
    '_id':'5f0f29848cb32182289ebc29',
    'name':'Move',
    'parameters':['agent','destination'],
    'definitions':[{'name':'goal_pose',
                    'item':'destination',
                    'property':'pose',
                    'fallback':None},
                    {'name':'priority',
                    'value':0}],
    'subactions':[{'id':'5f0f29928cb32182289ebc2a','parameters':{'agent':'agent','pose':'goal_pose','priority':'priority'}}],
    'preconditions':[],
    'postconditions':[{'thing':'agent','property':{'name':'ee_position','value':'goal_pose'},'operation':'=='}],
}

example_action_3 = {
    '_id':'5f1afee64ad66e28348447a6',
    'name':'Grasp: Branch On Agent',
    'parameters':['agent','object'],
    'definitions':[{'name':'priority',
                    'value':0}],
    'subactions':[{'flow':'branch',
                   'calls':[{'id':'5f0f29928cb32182289ebc2a',
                             'parameters':{'agent':'agent',
                                           'object':'object',
                                           'priority':'priority'}},
                            {'id':'5f1b2eb44ad66e28348447a7',
                            'parameters':{'agent':'agent',
                                          'object':'object',
                                          'priority':'priority'}}]
                  }],
    'preconditions':[],
    'postconditions':[{'thing':'agent','property':{'name':'ee_position','value':'goal_pose'},'operation':'=='}],
}

example_action_3 = {
    '_id':'5f1afee64ad66e28348447a6'
}

example_panda_primitive_1 = {
    '_id':'5f0f29928cb32182289ebc2a',
    'name':'panda_update_gripper',
    'parameters':['force','spacing','priority']
}

example_ur3_primitive_1 = {
    '_id':'5f1b317e4ad66e28348447a9',
    'name':'ur3_update_gripper',
    'parameters':['force','spacing','priority']
}

example_primitive_2 = {
    '_id':'5f0f29928cb32182289ebc2a',
    'name':'move_ee',
    'parameters':['agent','pose','priority']
}

example_agent_1 = {
    '_id':'5f0f2c748cb32182289ebc2b',
    'name':'Panda',
    'properties':[{'name':'model','value':'Panda'},
                  {'name':'grasp_state','value':'open'},
                  {'name':'ee_position','value':{'position':{'x':0,'y':0,'z':0},
                                                 'orientation':{'w':1,'x':0,'y':0,'z':0}}
                                                          }]
}

example_agent_2 = {
    '_id':'5f1b2ed34ad66e28348447a8',
    'name':'UR3',
    'properties':[{'name':'model','value':'UR3'},
                  {'name':'grasp_state','value':'open'},
                  {'name':'ee_position','value':{'position':{'x':0,'y':0,'z':0},
                                                 'orientation':{'w':1,'x':0,'y':0,'z':0}}
                                                          }]
}

example_thing_2 = {
    '_id':'5f0f5e5d8cb32182289ebc2c',
    'name':'Ball',
    'properties':[{'name':'grasping_force':'value':1},
                  {'name':'grasped','value':False},
                  {'name':'pose','value':{'position':{'x':0,'y':0,'z':0},
                                          'orientation':{'w':1,'x':0,'y':0,'z':0}}
                                                      }]
}
