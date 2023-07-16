import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess, IncludeLaunchDescription, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

import xacro
import yaml


def load_file(package_name, file_path):
    package_path = get_package_share_directory(package_name)
    absolute_file_path = os.path.join(package_path, file_path)
    try:
        with open(absolute_file_path, 'r') as file:
            return file.read()
    except EnvironmentError:
        # parent of IOError, OSError *and* WindowsError where available
        return None


def load_yaml(package_name, file_path):
    package_path = get_package_share_directory(package_name)
    absolute_file_path = os.path.join(package_path, file_path)
    try:
        with open(absolute_file_path, 'r') as file:
            return yaml.safe_load(file)
    except EnvironmentError:
        # parent of IOError, OSError *and* WindowsError where available
        return None


def generate_launch_description():
    # moveit_cpp.yaml is passed by filename for now since it's node specific

    gazebo = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory('rpi_robot_description'), 'launch'), 
                    '/empty_world.launch.py'])
             )

    rpi_robot_description_path = os.path.join(
        get_package_share_directory('rpi_robot_description'))

    rviz_config_dir = os.path.join(
        get_package_share_directory('rpi_robot_description'),
        'config',
        'view_bot.rviz'
    )

    xacro_file = os.path.join(rpi_robot_description_path,
                              'urdf',
                              'rpi_robot.urdf.xacro')

    doc = xacro.parse(open(xacro_file))
    xacro.process_doc(doc)
    robot_description_config = doc.toxml()
    robot_description = {'robot_description': robot_description_config}

    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[robot_description]
    )

    node_joint_state_publisher = Node(
            package='joint_state_publisher',
            executable='joint_state_publisher',
            output='screen',
        )

    spawn_entity = Node(package='gazebo_ros', executable='spawn_entity.py',
                        arguments=['-topic', 'robot_description',
                                   '-entity', 'rpi_robot'],
                        output='screen')

    display_rviz = Node(package='rviz2', executable='rviz2',
                        name='rviz2',
                        arguments=['-d', rviz_config_dir],
                        output='screen')

    return LaunchDescription([
      ###gazebo,
      ###node_joint_state_publisher,
      node_robot_state_publisher,
      ###spawn_entity,
      display_rviz
    ])
