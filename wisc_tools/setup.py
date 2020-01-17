from setuptools import setup, find_packages

package_name = 'wisc_tools'

setup(
 name=package_name,
 version='0.0.0',
 data_files=[
     ('share/ament_index/resource_index/packages',['resource/' + package_name]),
     ('share/' + package_name, ['package.xml']),
 ],
 install_requires=['setuptools'],
 packages=find_packages("src"),
 package_dir={"": "src"},
 zip_safe=True,
 maintainer='Andrew Schoen',
 maintainer_email='schoen@cs.wisc.edu',
 description='The wisc_tools package',
 license='Apache License, Version 2.0',
 tests_require=['pytest'],
 entry_points={
     'console_scripts': []
   },
)

# from distutils.core import setup
# from catkin_pkg.python_setup import generate_distutils_setup
#
# setup_args = generate_distutils_setup(
# 	packages=['wiscutils'],
#     scripts=[''],
# 	package_dir={'':'src'}
# 	)
#
# setup(**setup_args)
