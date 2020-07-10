import rclpy
from rclpy.node import Node
# from wisc_script.handling import Manager
from flask import Flask
from flask_pymongo import PyMongo

# This will probably all change.

class WiscProgramNode(Node):
    '''
    Node that handles and interfaces with REST/ROS calls
    '''
    def __init__(self):
        super(WiscProgramNode,self).__init__('wisc_program')
        self.app = Flask(__name__)
        self.app.config['MONGO_URI'] = 'mongodb+srv://admin:9VmeVmJFGxbDtKqB@programming-n2ugh.mongodb.net/programming?retryWrites=true&w=majority'
        self.mongo = PyMongo(self.app)
        self.db = self.mongo.db

        #self.manager = Manager(self.db)


def main(args=None):
    rclpy.init(args=args)

    node = WiscProgramNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
