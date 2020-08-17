import rclpy
from rclpy.node import Node
# from wisc_script.handling import Manager
from flask import Flask
# from flask_pymongo import PyMongo

# This will probably all change.


class WiscProgramNode(Node):
    '''
    Node that handles and interfaces with REST/ROS calls
    '''

    def __init__(self):
        super(WiscProgramNode, self).__init__('wisc_program')
        self.app = Flask(__name__)


def main(args=None):
    try:
        rclpy.init(args=args)

        node = WiscProgramNode()
        rclpy.spin(node)
        node.destroy_node()
        rclpy.shutdown()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
