import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    pkg_navigation = get_package_share_directory('warehouse_robot_navigation')
    pkg_gazebo = get_package_share_directory('warehouse_robot_gazebo')
    pkg_slam_toolbox = get_package_share_directory('slam_toolbox')

    # Launch Configurations
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    rviz = LaunchConfiguration('rviz', default='true')
    headless = LaunchConfiguration('headless', default='false')

    slam_params_file = os.path.join(pkg_navigation, 'config', 'slam_params.yaml')
    rviz_config_file = os.path.join(pkg_navigation, 'rviz', 'slam.rviz')

    # 1. Gazebo Simulation & Robot Spawning
    warehouse_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo, 'launch', 'warehouse_sim.launch.py')
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'headless': headless,
            'rviz': 'false'  # We open RViz with SLAM config below
        }.items()
    )

    # 2. SLAM Toolbox (Online Asynchronous)
    slam_toolbox = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_slam_toolbox, 'launch', 'online_async_launch.py')
        ),
        launch_arguments={
            'slam_params_file': slam_params_file,
            'use_sim_time': use_sim_time
        }.items()
    )

    # 3. RViz2 for SLAM Visualization
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_file],
        condition=IfCondition(rviz),
        parameters=[{'use_sim_time': use_sim_time}]
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true', description='Use simulation clock'),
        DeclareLaunchArgument('rviz', default_value='true', description='Open RViz2 with SLAM layout'),
        DeclareLaunchArgument('headless', default_value='false', description='Run Gazebo headless'),
        warehouse_sim,
        slam_toolbox,
        rviz_node
    ])
