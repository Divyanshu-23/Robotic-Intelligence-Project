import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node

def generate_launch_description():
    pkg_gazebo = get_package_share_directory('warehouse_robot_gazebo')
    pkg_description = get_package_share_directory('warehouse_robot_description')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')

    # Simulation world
    world_file = os.path.join(pkg_gazebo, 'worlds', 'warehouse.sdf')

    # Launch Arguments
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    rviz = LaunchConfiguration('rviz', default='false')
    headless = LaunchConfiguration('headless', default='false')

    # Ensure Gazebo finds resource models if needed
    gz_resource_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=[os.path.join(pkg_gazebo, 'worlds')]
    )

    # Launch Gazebo Harmonic
    # -r: start immediately; -s: headless server only
    gz_args = PythonExpression([
        "'-s -r \"' + '", world_file, "' + '\"' if '", headless, "' == 'true' else '-r \"' + '", world_file, "' + '\"'"
    ])
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': gz_args}.items(),
    )

    # Robot State Publisher (RSP)
    robot_state_publisher = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_description, 'launch', 'rsp.launch.py')
        ),
        launch_arguments={'use_sim_time': use_sim_time}.items()
    )

    # Spawn Entity into Gazebo via ros_gz_sim create
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        output='screen',
        arguments=[
            '-topic', 'robot_description',
            '-name', 'warehouse_robot',
            '-x', '-6.5',
            '-y', '-5.5',
            '-z', '0.08',
            '-Y', '0.0'
        ]
    )

    # ROS <-> Gazebo Bridge
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        output='screen',
        arguments=[
            # Simulation Clock (Gazebo -> ROS)
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            # Velocity Command (ROS -> Gazebo)
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            # Odometry (Gazebo -> ROS)
            '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            # TF (Gazebo -> ROS)
            '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
            # Joint States (Gazebo -> ROS)
            '/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model',
            # 2D LiDAR (Gazebo -> ROS)
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
            # Camera Image & Info (Gazebo -> ROS)
            '/camera/image_raw@sensor_msgs/msg/Image[gz.msgs.Image',
            '/camera/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo'
        ],
        parameters=[{
            'use_sim_time': use_sim_time
        }]
    )

    # Optional RViz2
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        condition=IfCondition(rviz),
        parameters=[{'use_sim_time': use_sim_time}]
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true', description='Use simulation clock'),
        DeclareLaunchArgument('rviz', default_value='false', description='Open RViz2'),
        DeclareLaunchArgument('headless', default_value='false', description='Run Gazebo headless without GUI'),
        gz_resource_path,
        gz_sim,
        robot_state_publisher,
        spawn_robot,
        bridge,
        rviz_node
    ])
