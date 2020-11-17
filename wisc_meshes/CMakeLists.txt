cmake_minimum_required(VERSION 3.5)
project(wisc_meshes)

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY
   meshes
  DESTINATION
   share/${PROJECT_NAME}
  )

ament_package()
