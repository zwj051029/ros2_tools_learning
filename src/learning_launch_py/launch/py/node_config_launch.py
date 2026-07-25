from launch import LaunchDescription
from launch_ros.actions import Node
# 封装终端指令相关类--------------
# from launch.actions import ExecuteProcess
# from launch.substitutions import FindExecutable
# 参数声明与获取-----------------
# from launch.actions import DeclareLaunchArgument
# from launch.substitutions import LaunchConfiguration
# 文件包含相关-------------------
# from launch.actions import IncludeLaunchDescription
# from launch.launch_description_sources import PythonLaunchDescriptionSource
# 分组相关----------------------
# from launch_ros.actions import PushRosNamespace
# from launch.actions import GroupAction
# 事件相关----------------------
# from launch.event_handlers import OnProcessStart, OnProcessExit
# from launch.actions import ExecuteProcess, RegisterEventHandler,LogInfo
# 获取功能包下share目录路径-------
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    # turtle1 = Node(
    #     package = "turtlesim",
    #     executable = "turtlesim_node",
    #     name = "t1",
    #     namespace = "ns_1",
    #     exec_name = "my_label",
    #     respawn = True
    # )

    # turtle2 = Node(
    #     package = "turtlesim",
    #     executable = "turtlesim_node",
    #     name = "t2",
    #     remappings = [("/turtle1/cmd_vel", "/cmd_vel")]
    # )

    # turtle3 = Node(
    #     package = "turtlesim",
    #     executable = "turtlesim_node",
    #     # ros2 run turtlesim turtlesim_node --ros-args --remap __ns:=/ns_3 --remap __node:=t3
    #     ros_arguments = ["--remap", "__ns:=/ns_3", "--remap", "__node:=t3"]
    #     # 相当于 --ros-args
    # )

    turtle4 = Node(
        package = "turtlesim",
        executable = "turtlesim_node",
        parameters = [os.path.join(get_package_share_directory("learning_launch_py"), "config", "turtlesim.yaml")]
    )
    
    return LaunchDescription([turtle4])
