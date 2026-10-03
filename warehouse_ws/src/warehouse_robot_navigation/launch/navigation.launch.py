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
    pkg_nav2_bringup = get_package_share_directory('nav2_bringup')

    # Paths
    default_map_file = os.path.join(pkg_navigation, 'maps', 'warehouse_map.yaml')
    default_params_file = os.path.join(pkg_navigation, 'config', 'nav2_params.yaml')
    default_rviz_config = os.path.join(pkg_nav2_bringup, 'rviz', 'nav2_default_view.rviz')

    # Launch Configurations
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    map_yaml_file = LaunchConfiguration('map', default=default_map_file)
    params_file = LaunchConfiguration('params_file', default=default_params_file)
    autostart = LaunchConfiguration('autostart', default='true')
    headless = LaunchConfiguration('headless', default='false')
    rviz = LaunchConfiguration('rviz', default='true')

    # 1. Gazebo Simulation & Robot Spawning
    warehouse_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo, 'launch', 'warehouse_sim.launch.py')
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'headless': headless,
            'rviz': 'false'
        }.items()
    )

    # 2. Nav2 Bringup (AMCL + Map Server + Planners + Controllers + BT Navigator)
    nav2_bringup = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_nav2_bringup, 'launch', 'bringup_launch.py')
        ),
        launch_arguments={
            'map': map_yaml_file,
            'params_file': params_file,
            'use_sim_time': use_sim_time,
            'autostart': autostart
        }.items()
    )

    # 3. RViz2 Navigation Interface
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', default_rviz_config],
        condition=IfCondition(rviz),
        parameters=[{'use_sim_time': use_sim_time}]
    )

    return LaunchDescription([
        DeclareLaunchArgument('map', default_value=default_map_file, description='Full path to map file to load'),
        DeclareLaunchArgument('params_file', default_value=default_params_file, description='Full path to the ROS2 parameters file to use'),
        DeclareLaunchArgument('use_sim_time', default_value='true', description='Use simulation (Gazebo) clock if true'),
        DeclareLaunchArgument('autostart', default_value='true', description='Automatically startup the nav2 stack'),
        DeclareLaunchArgument('headless', default_value='false', description='Run Gazebo headless'),
        DeclareLaunchArgument('rviz', default_value='true', description='Open RViz2 Navigation interface'),
        warehouse_sim,
        nav2_bringup,
        rviz_node
    ])
