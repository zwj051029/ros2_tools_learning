from launch import LaunchDescription
from launch_ros.actions import Node
# 封装终端指令相关类--------------
# from launch.actions import ExecuteProcess
# from launch.substitutions import FindExecutable
# 参数声明与获取-----------------
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
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
# from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    del_r = DeclareLaunchArgument(name = "r", default_value = "255")
    del_g = DeclareLaunchArgument(name = "g", default_value = "255")
    del_b = DeclareLaunchArgument(name = "b", default_value = "255")

    turtle = Node(
        package = "turtlesim",
        executable = "turtlesim_node",
        parameters = [{
            "background_r": LaunchConfiguration("r"),
            "background_g": LaunchConfiguration("g"),
            "background_b": LaunchConfiguration("b")
        }]
    )
    
    return LaunchDescription([del_r, del_g, del_b, turtle])