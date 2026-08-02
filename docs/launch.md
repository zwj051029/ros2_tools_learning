# ROS 2 Launch 知识点总结

## 1. Launch 是什么

ROS 2 Launch 是一套用于启动和组织多个 ROS 2 节点及相关进程的工具。

如果只使用 `ros2 run`，一个终端通常只能方便地管理一个节点。实际机器人系统往往同时包含驱动、感知、定位、规划、控制、可视化等多个节点，还需要统一配置参数、命名空间、话题重映射和启动顺序。Launch 可以把这些操作写成可重复执行的启动描述。

一个 Launch 文件通常负责：

- 启动一个或多个 ROS 2 节点。
- 设置节点名称和命名空间。
- 加载参数或参数文件。
- 重映射话题、服务和动作名称。
- 执行普通系统命令或 ROS 2 CLI 命令。
- 声明运行时可修改的启动参数。
- 包含并复用其他 Launch 文件。
- 对多个节点进行分组配置。
- 根据进程启动、退出等事件执行后续动作。
- 统一关闭由本次 Launch 启动的进程。

Launch 的核心价值可以概括为：

```text
把一组分散的终端命令，变成可配置、可复用、可维护的系统启动入口。
```

## 2. Launch 与 `ros2 run` 的区别

| 对比项 | `ros2 run` | `ros2 launch` |
| --- | --- | --- |
| 主要用途 | 启动单个可执行程序 | 编排多个节点和进程 |
| 配置能力 | 通过命令行逐项传入 | 在文件中集中管理 |
| 参数与重映射 | 每次手动输入 | 可以预设并允许覆盖 |
| 启动顺序 | 人工控制 | 可以通过事件和定时动作控制 |
| 复用能力 | 较弱 | 可以包含其他 Launch 文件 |
| 关闭方式 | 分别关闭各终端 | 一次 `Ctrl+C` 统一关闭 |

学习单个节点时适合使用 `ros2 run`；启动完整机器人系统时通常使用 `ros2 launch`。

## 3. 三种 Launch 格式

ROS 2 Humble 支持 Python、XML 和 YAML 三种 Launch 描述格式。

| 格式 | 常用后缀 | 特点 | 适用场景 |
| --- | --- | --- | --- |
| Python | `.launch.py` 或 `_launch.py` | 可编程能力最强，支持复杂逻辑和事件 | 中大型项目、动态配置 |
| XML | `.launch.xml` 或 `_launch.xml` | 标签语义直观，结构清晰 | 启动逻辑固定的项目 |
| YAML | `.launch.yaml` 或 `_launch.yaml` | 内容紧凑，配置感较强 | 简单编排和格式学习 |

三种格式描述的是同一类启动行为，但表达方式不同。实际项目中通常优先选择 Python，因为它能够直接使用条件、循环、函数、事件处理和复杂替换逻辑。

## 4. Python Launch 基本结构

Python 启动文件必须提供：

```python
def generate_launch_description():
    ...
```

该函数返回一个 `LaunchDescription`，其中保存本次启动需要执行的 Action。

最小示例：

```python
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    turtle = Node(
        package='turtlesim',
        executable='turtlesim_node',
        name='t1'
    )

    return LaunchDescription([turtle])
```

理解这段代码时，可以分成三层：

```text
LaunchDescription
└── Action
    └── Node
```

- `LaunchDescription`：整份启动描述。
- Action：启动系统需要执行的动作。
- `Node`：专门用于启动 ROS 2 节点的 Action。

## 5. XML 与 YAML 基本结构

### XML

```xml
<launch>
    <node pkg="turtlesim" exec="turtlesim_node" name="t1"/>
</launch>
```

### YAML

```yaml
launch:
- node:
    pkg: turtlesim
    exec: turtlesim_node
    name: t1
```

三个示例都用于启动 `turtlesim` 包中的 `turtlesim_node`，并将 ROS 2 节点名称设置为 `t1`。

## 6. 节点配置

Python 中常见的 `Node` 配置如下：

```python
node = Node(
    package='demo_nodes_cpp',
    executable='talker',
    name='talker_node',
    namespace='robot1',
    output='screen',
    parameters=[{'publish_rate': 10.0}],
    remappings=[('chatter', 'status')]
)
```

常见字段含义：

| 字段 | 作用 |
| --- | --- |
| `package` | 功能包名称 |
| `executable` | 可执行程序或 `console_scripts` 名称 |
| `name` | 运行时 ROS 2 节点名称 |
| `namespace` | 节点所属命名空间 |
| `output` | 日志输出位置，常用 `screen` |
| `parameters` | 参数字典或参数文件列表 |
| `remappings` | 名称重映射规则列表 |
| `arguments` | 传递给可执行程序的普通命令行参数 |
| `ros_arguments` | ROS 专用命令行参数 |
| `respawn` | 进程异常退出后是否重新启动 |
| `respawn_delay` | 自动重启前等待时间 |

### 三种名称不要混淆

```text
功能包名称       package
可执行程序名称   executable
ROS 2 节点名称  name
```

例如：

```python
Node(
    package='learning_topic_cpp',
    executable='cpp_string_pub',
    name='string_publisher'
)
```

运行时：

- `learning_topic_cpp` 用于定位功能包。
- `cpp_string_pub` 用于定位安装后的程序。
- `string_publisher` 才是 `ros2 node list` 中显示的节点名称。

## 7. 命名空间

命名空间用于组织节点及其相对名称，尤其适合多机器人系统。

```python
Node(
    package='turtlesim',
    executable='turtlesim_node',
    name='sim',
    namespace='robot1'
)
```

节点完整名称为：

```text
/robot1/sim
```

节点使用相对话题名称时，话题通常也会进入同一命名空间。绝对名称以 `/` 开头，不会自动添加节点命名空间。

## 8. 参数配置

### 直接传递参数字典

```python
Node(
    package='turtlesim',
    executable='turtlesim_node',
    parameters=[{
        'background_r': 0,
        'background_g': 255,
        'background_b': 0
    }]
)
```

### 加载 YAML 参数文件

```python
import os
from ament_index_python.packages import get_package_share_directory

config_file = os.path.join(
    get_package_share_directory('learning_launch_cpp'),
    'config',
    'turtlesim.yaml'
)

node = Node(
    package='turtlesim',
    executable='turtlesim_node',
    parameters=[config_file]
)
```

ROS 2 参数文件常见结构：

```yaml
/turtlesim:
  ros__parameters:
    background_r: 0
    background_g: 255
    background_b: 0
```

注意：

- YAML 中的节点键名应与实际节点完整名称匹配。
- `ros__parameters` 拼写和双下划线不能省略。
- 修改参数文件后，需要重新安装资源或使用符号链接构建。
- Launch 参数和 ROS 2 节点参数不是同一个概念。

## 9. Launch 参数

Launch 参数用于让同一份启动文件在运行时接收不同配置。

### 声明参数

```python
from launch.actions import DeclareLaunchArgument

r_arg = DeclareLaunchArgument(
    'r',
    default_value='255',
    description='背景红色通道'
)
```

### 获取参数

```python
from launch.substitutions import LaunchConfiguration

r = LaunchConfiguration('r')
```

### 使用参数

```python
node = Node(
    package='turtlesim',
    executable='turtlesim_node',
    parameters=[{'background_r': r}]
)
```

完整返回：

```python
return LaunchDescription([
    r_arg,
    node
])
```

运行时覆盖：

```bash
ros2 launch learning_launch_cpp parameters_launch.py r:=255 g:=0 b:=0
```

查看支持的 Launch 参数：

```bash
ros2 launch learning_launch_cpp parameters_launch.py --show-args
```

### Launch 参数与节点参数的区别

| 对比项 | Launch 参数 | ROS 2 节点参数 |
| --- | --- | --- |
| 声明位置 | Launch 描述 | 节点内部或参数配置 |
| 获取方式 | `LaunchConfiguration` | `get_parameter()` 等节点 API |
| 生命周期 | 启动描述展开期间 | 节点运行期间 |
| 主要用途 | 控制启动过程和生成配置 | 控制节点业务行为 |

Launch 参数可以被传递给节点参数，但两者仍属于不同层次。

## 10. Substitution 替换对象

Launch 文件在解析阶段不一定立即知道所有值，因此使用 Substitution 表示“运行时再求值”的内容。

常见替换对象：

| 对象 | 作用 |
| --- | --- |
| `LaunchConfiguration` | 读取 Launch 参数 |
| `EnvironmentVariable` | 读取环境变量 |
| `Command` | 执行命令并使用标准输出 |
| `PathJoinSubstitution` | 组合路径 |
| `FindPackageShare` | 查找功能包共享目录 |

例如加载 Xacro：

```python
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.parameter_descriptions import ParameterValue

robot_description = ParameterValue(
    Command(['xacro ', LaunchConfiguration('model')])
)
```

Substitution 不是普通字符串。需要实际值时，应让 Launch 系统在正确的上下文中完成解析。

## 11. 功能包共享目录

源码位于 `src/`，构建后运行资源通常位于 `install/`。Launch 文件应通过功能包索引查找安装路径，不应写死个人电脑的绝对路径。

Python 常用方式：

```python
from ament_index_python.packages import get_package_share_directory

share_dir = get_package_share_directory('learning_launch_cpp')
```

XML 和 YAML 常用替换：

```text
$(find-pkg-share learning_launch_cpp)
```

这样仓库移动到其他目录或其他电脑后仍然可以工作。

## 12. 名称重映射

重映射用于改变节点使用的话题、服务或动作名称，而不需要修改节点源码。

Python 示例：

```python
Node(
    package='demo_nodes_cpp',
    executable='talker',
    remappings=[
        ('chatter', 'robot_status')
    ]
)
```

常见用途：

- 让发布方与不同名称的订阅方连接。
- 为多个机器人复用相同节点。
- 接入已有系统的命名规范。
- 在仿真与真实硬件之间切换数据源。

## 13. 执行普通进程

`Node` 专门启动 ROS 2 节点，`ExecuteProcess` 可以启动任意系统命令。

```python
from launch.actions import ExecuteProcess

echo_pose = ExecuteProcess(
    cmd=['ros2', 'topic', 'echo', '/turtle1/pose'],
    output='screen'
)
```

还可以调用服务：

```python
spawn = ExecuteProcess(
    cmd=[
        'ros2', 'service', 'call',
        '/spawn',
        'turtlesim/srv/Spawn',
        '{x: 2.0, y: 3.0, name: my_turtle}'
    ],
    output='screen'
)
```

适合 `ExecuteProcess` 的内容包括：

- ROS 2 CLI 命令。
- 普通可执行程序。
- 调试或数据转换工具。
- 与机器人系统一起启动的辅助进程。

不要依赖复杂的 Shell 字符串拼接。优先把命令和参数拆成列表，减少引号和转义问题。

## 14. 包含其他 Launch 文件

复杂系统应把不同子系统拆成多个 Launch 文件，再通过包含关系组合。

Python 示例：

```python
import os
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory

included_launch = IncludeLaunchDescription(
    PythonLaunchDescriptionSource(
        os.path.join(
            get_package_share_directory('learning_launch_cpp'),
            'launch', 'py', 'parameters_launch.py'
        )
    ),
    launch_arguments={
        'r': '0',
        'g': '0',
        'b': '0'
    }.items()
)
```

包含机制的好处：

- 减少重复启动配置。
- 将驱动、导航、感知等子系统分开维护。
- 顶层 Launch 只负责系统组合。
- 同一子系统可以被仿真和真实机器人复用。

## 15. 分组与命名空间

`GroupAction` 可以对一组 Action 统一施加配置。

```python
from launch.actions import GroupAction
from launch_ros.actions import PushRosNamespace

robot1_group = GroupAction([
    PushRosNamespace('robot1'),
    Node(
        package='turtlesim',
        executable='turtlesim_node',
        name='sim'
    )
])
```

最终节点名称为：

```text
/robot1/sim
```

分组适合：

- 多机器人系统。
- 相同组件的多实例部署。
- 为一组节点统一设置命名空间。
- 将同一套节点配置复用到不同机器人。

## 16. 事件处理

Launch 可以在某个事件发生后执行指定动作。

常见事件处理器：

| 事件处理器 | 触发时机 |
| --- | --- |
| `OnProcessStart` | 目标进程启动后 |
| `OnProcessExit` | 目标进程退出后 |
| `OnProcessIO` | 目标进程产生标准输出或错误输出时 |
| `OnShutdown` | Launch 系统关闭时 |

注册事件处理器：

```python
from launch.actions import RegisterEventHandler, LogInfo
from launch.event_handlers import OnProcessExit

exit_handler = RegisterEventHandler(
    OnProcessExit(
        target_action=turtle,
        on_exit=[LogInfo(msg='turtlesim 已退出')]
    )
)
```

事件处理可以用于：

- 等待某进程启动后再执行初始化命令。
- 进程退出后打印日志或关闭系统。
- 组织有先后依赖关系的启动流程。
- 根据执行结果触发清理动作。

“进程已启动”不等于“节点已经完成业务初始化”或“服务已经可用”。如果必须等待服务、动作服务器或生命周期状态，应使用对应的状态检测机制，而不是只依赖固定延时。

## 17. 定时与条件启动

### 延时执行

```python
from launch.actions import TimerAction

delayed_node = TimerAction(
    period=2.0,
    actions=[node]
)
```

`TimerAction` 适合简单的延时启动，但它不能真正证明依赖组件已经准备完成。

### 条件启动

```python
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration

rviz = Node(
    package='rviz2',
    executable='rviz2',
    condition=IfCondition(LaunchConfiguration('use_rviz'))
)
```

常见条件包括：

- `IfCondition`
- `UnlessCondition`

条件启动可以让同一份 Launch 文件适应调试、部署、仿真和无界面运行等不同场景。

## 18. 三种格式常用语法对照

### 启动节点

Python：

```python
Node(package='turtlesim', executable='turtlesim_node', name='t1')
```

XML：

```xml
<node pkg="turtlesim" exec="turtlesim_node" name="t1"/>
```

YAML：

```yaml
- node:
    pkg: turtlesim
    exec: turtlesim_node
    name: t1
```

### 声明参数

Python：

```python
DeclareLaunchArgument('color', default_value='255')
```

XML：

```xml
<arg name="color" default="255"/>
```

YAML：

```yaml
- arg:
    name: color
    default: '255'
```

### 获取参数

Python：

```python
LaunchConfiguration('color')
```

XML 和 YAML：

```text
$(var color)
```

### 查找功能包共享目录

Python：

```python
get_package_share_directory('package_name')
```

XML 和 YAML：

```text
$(find-pkg-share package_name)
```

## 19. 功能包中的安装配置

Launch 文件只有被安装到功能包共享目录后，`ros2 launch` 才能稳定找到它们。

### `ament_cmake`

```cmake
install(
  DIRECTORY launch config
  DESTINATION share/${PROJECT_NAME}
)
```

### `ament_python`

```python
from glob import glob

data_files=[
    ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
    ('share/' + package_name + '/config', glob('config/*.yaml')),
]
```

如果文件分为 `launch/py`、`launch/xml` 和 `launch/yaml`，应分别配置对应安装目录和匹配规则。

常见错误是源码中已经创建文件，但没有写安装规则。此时编辑器能看到文件，`ros2 launch` 却无法找到它。

## 20. 构建与运行流程

标准流程：

```bash
source /opt/ros/humble/setup.bash
colcon build --packages-select <package_name>
source install/setup.bash
ros2 launch <package_name> <launch_file>
```

开发 Python 或资源文件时，可以考虑：

```bash
colcon build --symlink-install --packages-select <package_name>
```

符号链接构建能够减少部分 Python 和资源文件修改后的重复复制，但修改 `setup.py`、CMake 配置或新增文件时仍应重新构建。

## 21. 常用检查命令

查看功能包共享目录：

```bash
ros2 pkg prefix --share <package_name>
```

查看 Launch 参数：

```bash
ros2 launch <package_name> <launch_file> --show-args
```

查看当前节点：

```bash
ros2 node list
```

查看节点详情：

```bash
ros2 node info /node_name
```

查看参数：

```bash
ros2 param list /node_name
ros2 param get /node_name <parameter_name>
```

查看话题和服务：

```bash
ros2 topic list
ros2 service list
```

查看 Launch 文件能否被解析而不真正长期运行节点：

```bash
ros2 launch <package_name> <launch_file> --show-args
```

## 22. 常见问题

### 找不到功能包

```text
Package '<name>' not found
```

检查：

1. 功能包是否成功构建。
2. 当前终端是否执行了 `source install/setup.bash`。
3. 功能包名称是否正确。
4. 是否在错误的工作空间中构建或刷新环境。

### 找不到 Launch 文件

检查：

1. 文件是否被 CMake 或 `setup.py` 安装。
2. 文件名是否符合 `glob()` 匹配规则。
3. 修改后是否重新构建。
4. `install/<package>/share/<package>/` 中是否存在该文件。

### 修改后仍运行旧内容

常见原因是 Launch 从 `install/` 读取旧副本。重新构建并刷新：

```bash
colcon build --packages-select <package_name>
source install/setup.bash
```

### 参数文件没有生效

检查：

- YAML 的节点键名是否与实际节点名称和命名空间匹配。
- 是否存在 `ros__parameters`。
- 参数类型是否正确。
- 加载的是源码文件还是安装目录中的旧文件。

### 节点名称冲突

同名节点会让命令行查询和日志辨认变得困难。通过 `name` 或 `namespace` 区分多个实例。

### Launch 参数格式错误

正确格式：

```text
name:=value
```

`:=` 两侧不要随意加入导致参数分裂的空格。路径中含空格时需要正确引用整个参数。

### `ExecuteProcess` 引号错误

优先使用参数列表：

```python
cmd=['ros2', 'topic', 'echo', '/topic_name']
```

避免把整条复杂命令塞进一个字符串后依赖 Shell 再次解析。

### 关闭 Launch 后仍有进程

正常情况下，`Ctrl+C` 会关闭 Launch 管理的进程。如果程序自行创建了脱离 Launch 管理的后台进程，可能无法被统一回收。启动外部命令时应明确其进程生命周期。

## 23. 工程组织建议

推荐结构：

```text
package_name/
├── config/
│   └── *.yaml
├── launch/
│   ├── bringup.launch.py
│   ├── simulation.launch.py
│   └── visualization.launch.py
├── rviz/
├── urdf/
├── CMakeLists.txt 或 setup.py
└── package.xml
```

命名建议：

- 文件名使用小写蛇形命名。
- 使用 `.launch.py` 明确表示 Python Launch 文件。
- 顶层系统启动常用 `bringup.launch.py`。
- 仿真、真实硬件和可视化入口按职责拆分。
- Launch 参数名应清晰，例如 `use_sim_time`、`use_rviz`、`robot_namespace`。

设计原则：

- 一个文件只承担清晰的启动职责。
- 重复子系统提取为可包含的 Launch 文件。
- 路径通过功能包索引获取，不写死绝对路径。
- 参数放入配置文件，不在 Launch 中堆积大量业务数据。
- 为重要 Launch 参数提供默认值和描述。
- 多机器人实例优先使用分组和命名空间。
- 启动顺序依赖应基于真实状态，而不是只依靠固定延时。

## 24. 学习仓库中的对应示例

本仓库提供两套相同行为的 Launch 学习包：

| 功能包 | 构建类型 | 说明 |
| --- | --- | --- |
| `learning_launch_cpp` | `ament_cmake` | 演示 CMake 功能包中的 Launch 资源安装 |
| `learning_launch_py` | `ament_python` | 演示 Python 功能包中的 Launch 资源安装 |

两者都包含：

- 基础多节点启动。
- 节点参数文件加载。
- ROS 2 CLI 命令执行。
- Launch 参数声明与覆盖。
- Launch 文件包含。
- 节点分组与命名空间。
- Python 格式的事件处理。
- Python、XML、YAML 三种格式对照。

## 25. 复习速查表

### 必须记住

```text
Node                启动 ROS 2 节点
ExecuteProcess      启动普通进程
DeclareLaunchArgument 声明 Launch 参数
LaunchConfiguration 读取 Launch 参数
IncludeLaunchDescription 包含其他 Launch
GroupAction         对一组 Action 统一配置
PushRosNamespace    为一组节点添加命名空间
RegisterEventHandler 注册事件响应
```

### 必须分清

```text
package     功能包名称
executable  可执行程序名称
name        ROS 2 节点名称

Launch 参数  控制启动描述
节点参数     控制节点运行行为

arguments      普通程序参数
ros_arguments  ROS 2 专用参数
```

### 标准排查顺序

```text
1. source /opt/ros/humble/setup.bash
2. 构建目标功能包
3. source install/setup.bash
4. ros2 launch ... --show-args
5. 检查 install 中是否存在启动文件和配置
6. 检查节点、参数、话题和命名空间
7. 阅读 Launch 与节点日志
```

### 一句话总结

```text
Launch 负责描述“系统应该如何启动和组合”，节点代码负责实现“系统启动后具体做什么”。
```
