cmake_minimum_required(VERSION 2.8.3)
project(wisc_tools)

find_package(catkin REQUIRED COMPONENTS
  geometry_msgs
  roscpp
  rospy
  sensor_msgs
  std_msgs
)

find_package(catkin REQUIRED COMPONENTS std_msgs message_generation geometry_msgs)

catkin_python_setup()
