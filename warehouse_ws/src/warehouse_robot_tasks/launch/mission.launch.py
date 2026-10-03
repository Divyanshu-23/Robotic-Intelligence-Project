import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    navigation_share = get_package_share_directory(
        'warehouse_robot_navigation'
    )
    navigation_launch = os.path.join(
        navigation_share, 'launch', 'navigation.launch.py'
    )

    use_sim_time = LaunchConfiguration('use_sim_time')
    headless = LaunchConfiguration('headless')
    rviz = LaunchConfiguration('rviz')

    navigation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(navigation_launch),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'headless': headless,
            'rviz': rviz,
        }.items(),
    )
    mission_planner = Node(
        package='warehouse_robot_tasks',
        executable='mission_planner',
        name='mission_planner',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('headless', default_value='false'),
        DeclareLaunchArgument('rviz', default_value='true'),
        navigation,
        mission_planner,
    ])
