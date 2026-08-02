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
from ament_index_python.packages import get_package_share_directory
from launch_ros.parameter_descriptions import ParameterValue
from launch.substitutions import Command

def generate_launch_description():
    # ros2 launch learning_urdf_cpp display.launch.py model:=`ros2 pkg prefix --share learning_urdf_cpp`/urdf/urdf/box_robot_copy.urdf
    model = DeclareLaunchArgument(name = "model", default_value = get_package_share_directory("learning_urdf_cpp") + "/urdf/urdf/box_robot.urdf")
    robot_description = ParameterValue(Command(["xacro ", LaunchConfiguration("model")]))
    robot_state_publisher = Node(
        package = "robot_state_publisher",
        executable = "robot_state_publisher",
        parameters = [{"robot_description": robot_description}]
    )

    joint_state_publisher = Node(
        package = "joint_state_publisher",
        executable = "joint_state_publisher"
    )

    rviz = Node(
        package = "rviz2",
        executable = "rviz2",
        arguments = ["-d", get_package_share_directory("learning_urdf_cpp") + "/rviz/urdf.rviz"]
    )
    
    return LaunchDescription([model, robot_state_publisher, joint_state_publisher, rviz])