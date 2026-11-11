from glob import glob

from setuptools import find_packages, setup

package_name = 'lecture_demo'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        # Lets ROS 2 find the package (`ros2 pkg list`, `ros2 run`, ...).
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # Installs every launch file, so `ros2 launch lecture_demo <file>` can find it.
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='student',
    maintainer_email='student@example.com',
    description='Demo nodes, launch files and exercises for the ROS 2 lecture '
                '(TurtleBot3 in Gazebo)',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        # Every line is  'command_name = python_module:function'  and makes the node
        # available as  `ros2 run lecture_demo <command_name>`.
        # After adding a line here you must rebuild (cb) for it to appear.
        'console_scripts': [
            # Demos (finished code)
            'scan_listener = lecture_demo.scan_listener:main',
            'square_driver = lecture_demo.square_driver:main',
            'edge_detector = lecture_demo.edge_detector:main',
            # Exercises (code with TODOs for the students)
            'exercise_scan_listener = lecture_demo.exercise_scan_listener:main',
            'exercise_square_driver = lecture_demo.exercise_square_driver:main',
            'exercise_edge_detector = lecture_demo.exercise_edge_detector:main',
        ],
    },
)
