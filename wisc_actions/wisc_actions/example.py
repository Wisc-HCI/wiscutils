from wisc_actions.elements import ImperativeProgram
from wisc_actions.elements import Property, PropertyOperation
from wisc_actions.elements import LiteralDefinition


def test_definition():
    namespace = {}
    d = LiteralDefinition('x', 2)  # x = 2
    print('x:', d.get(namespace))
    d.set(namespace, 5)  # x = 5
    print('after set x:', d.get('x'))


test_definition()

input('New Imperative Program [Enter]')
my_program = ImperativeProgram.new("Panda Script")
print('\n{0}\n\n'.format(my_program))

input('Default Main Function [Enter]')
main_fn = my_program.get_action_by_id(my_program.main)
print('\n{0}\n\n'.format(main_fn))

input('Adding A Ball to the State [Enter]')
new_ball = my_program.create_thing(
    'Orange Ball', [Property('is_ball', True), Property('grip_force', 3)])
print('\n{0}\n\n'.format(new_ball))

input('Adding A Robot to the State [Enter]')
panda_robot = my_program.create_thing(
    'Panda', [Property('model', 'Panda'), Property('gripping', False)])
print('\n{0}\n\n'.format(panda_robot))

input('View the updated Program [Enter]')
print('\n{0}\n\n'.format(my_program))

input('Creating a Primitive [Enter]')
new_primitive = my_program.create_primitive(
    'panda_update_gripper', parameters=['force', 'spacing', 'priority'])
print('\n{0}\n\n'.format(new_primitive))

input('View the updated Program [Enter]')
print('\n{0}\n\n'.format(my_program))

input('Creating a Call to the Primitive [Enter]')
call_to_primitive = new_primitive.create_call(
    {'force': 'grip_force', 'spacing': 'grip_spacing', 'priority': 'priority'})
print('\n{0}\n\n'.format(call_to_primitive))

input('Creating a wrapper for the Primitive [Enter]')
new_action = my_program.create_action(
    'Panda Grasp', parameters=['agent', 'object'])
new_action.create_definition(
    name='grip_force', item='object', property='grip_force', fallback=1)
new_action.create_definition(name='grip_spacing', value=None)
new_action.create_definition(name='priority', value=0)
new_action.create_postcondition(thing='agent', property=Property(
    'gripping', True), operation=PropertyOperation.EQUALS)
new_action.subactions.append(call_to_primitive)
print('\n{0}\n\n'.format(new_action))

input('Creating a Call to the Action [Enter]')
call_to_action = new_action.create_call({'agent': 'agent', 'object': 'object'})
print('\n{0}\n\n'.format(call_to_action))

input('Updated Main Function [Enter]')
main_fn.subactions.append(call_to_action)
print('\n{0}\n\n'.format(main_fn))


input('Complete Program [Enter]')
print('\n{0}\n\n'.format(my_program))
