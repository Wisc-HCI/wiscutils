
example_action_1a = {
    '_id':'5f0f29848cb32182289ebc29',
    'name':'Grasp',
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
    'preconditions':[],
    'postconditions':[{'thing':'agent','property':{'name':'grasp_state','value':'closed'}}],
}

example_action_1b = {
    '_id':'5f0f29848cb32182289ebc29',
    'name':'Grasp (Hardcoded Agent)',
    'parameters':['object'],
    'definitions':[{'name':'force_value',
                    'item':'object',
                    'property':'grasping_force',
                    'fallback':0},
                   {'name':'priority',
                    'value':0},
                   {'name':'grip_spacing',
                    'value':None},
                   {'name':'agent',
                    'value':'5f0f2c748cb32182289ebc2b'}],
    'subactions':[{'id':'5f0f29928cb32182289ebc2a','parameters':{'force':'force_value','spacing':'grip_spacing','agent':'agent','priority':'priority'}}],
    'preconditions':[],
    'postconditions':[{'thing':'agent','property':{'name':'grasp_state','value':'closed'}}],
}

example_action_2 = {
    '_id':'5f0f29848cb32182289ebc29',
    'name':'Move',
    'parameters':['agent','destination'],
    'definitions':[{'name':'force_value',
                    'property':{'method':'access',
                            'property':'pose',
                            'value':'force',
                            'fallback':0}},
                   {'value':'priority',
                    'from':{'method':'define',
                            'value':0}}],
    'subactions':[{'id':'5f0f29928cb32182289ebc2a','parameters':{'force':'force_value','spacing':None,'agent':'agent','priority':0}}],
    'preconditions':[],
    'postconditions':[{'thing':'agent','property':{'name':'grasp_state','values':{'state':'closed'}}}],
}

example_primitive_1 = {
    '_id':'5f0f29928cb32182289ebc2a',
    'name':'update_gripper',
    'parameters':['force','spacing','agent','priority']
}

example_thing_1 = {
    '_id':'5f0f2c748cb32182289ebc2b',
    'name':'Panda',
    'properties':[{'name':'grasp_state','value':'open'},
                  {'name':'ee_position','value':{'position':{'x':0,'y':0,'z':0},
                                                 'quaternion':{'w':1,'x':0,'y':0,'z':0}}
                                                          }]
}

example_thing_2 = {
    '_id':'5f0f5e5d8cb32182289ebc2c',
    'name':'Ball',
    'properties':[{'name':'grasping_force':'value':1},
                  {'name':'grasped','value':False},
                  {'name':'pose','value':{'position':{'x':0,'y':0,'z':0},
                                          'quaternion':{'w':1,'x':0,'y':0,'z':0}}
                                                      }]
}