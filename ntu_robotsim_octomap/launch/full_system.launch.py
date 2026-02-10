#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, TimerAction, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    nav2_params = LaunchConfiguration("nav2_params")

    this_pkg = FindPackageShare("ntu_robotsim_octomap")

    maze_launch = PathJoinSubstitution([this_pkg, "launch", "maze.launch.py"])
    robot_launch = PathJoinSubstitution([this_pkg, "launch", "single_robot_sim.launch.py"])
    octomap_launch = PathJoinSubstitution([this_pkg, "launch", "octomap_filtered.launch.py"])

    odom_to_tf_launch = PathJoinSubstitution([
        FindPackageShare("odom_to_tf_ros2"),
        "launch",
        "odom_to_tf.launch.py"
    ])

    nav2_launch = PathJoinSubstitution([
        FindPackageShare("nav2_bringup"),
        "launch",
        "navigation_launch.py"
    ])

    default_nav2_params = PathJoinSubstitution([this_pkg, "config", "nav2_octomap_params.yaml"])

    start_maze = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(maze_launch)
    )

    start_robot = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(robot_launch)
    )

    start_odom_to_tf = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(odom_to_tf_launch),
        launch_arguments={
            "use_sim_time": "true"
        }.items()
    )

    start_octomap = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(octomap_launch),
        launch_arguments={
            "frame_id": "odom",
            "base_frame_id": "base_link"
        }.items()
    )

    start_nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(nav2_launch),
        launch_arguments={
            "use_sim_time": "true",
            "params_file": nav2_params,
            "autostart": "true"
        }.items()
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            "nav2_params",
            default_value=default_nav2_params,
            description="Path to Nav2 params yaml (OctoMap integrated)"
        ),

        start_maze,

        TimerAction(period=2.0, actions=[start_robot]),

        TimerAction(period=4.0, actions=[start_odom_to_tf]),

        TimerAction(period=6.0, actions=[start_octomap]),

        TimerAction(period=8.0, actions=[start_nav2]),
    ])

