# ROS 2 工具学习工作空间

`ros2_tools_learning` 是一个面向 ROS 2 Humble 的工具链学习仓库，记录 Launch、Rosbag2、TF2、URDF 与 Xacro 的学习过程、可运行示例和专题复习笔记。

仓库采用 C++ 与 Python 对照学习方式：同一知识点尽量分别使用 `ament_cmake` 和 `ament_python` 组织，便于理解不同构建系统下的资源安装、节点注册和运行方式。

> 项目状态：学习内容已经整理完成，仓库进入归档维护阶段。

## 项目定位

本仓库主要解决以下学习问题：

- 如何使用 Launch 统一启动、配置和组织 ROS 2 节点。
- 如何通过 Rosbag2 录制、读取和回放话题数据。
- 如何广播、监听和转换机器人坐标系。
- 如何使用 URDF 与 Xacro 构建模块化机器人模型。
- 如何在 C++ 与 Python 节点之间验证 ROS 2 的跨语言通信。
- 如何将示例代码整理为便于长期复习的工程和文档。

本仓库适合：

- 正在学习 ROS 2 基础工具的开发者。
- 使用 Ubuntu 22.04 与 ROS 2 Humble 的学习者。
- 希望对照 C++ 和 Python API 的机器人方向开发者。
- 需要 Launch、Rosbag2、TF2、URDF 复习资料的读者。

本仓库不是可直接部署到真实机器人的生产系统，也不包含完整导航、控制、硬件驱动和物理仿真方案。

## 技术环境

| 项目 | 版本或说明 |
| --- | --- |
| 操作系统 | Ubuntu 22.04 LTS |
| ROS 2 | Humble Hawksbill |
| C++ | C++17 |
| Python | Python 3.10 |
| 构建工具 | `colcon` |
| C++ 构建类型 | `ament_cmake` |
| Python 构建类型 | `ament_python` |
| 可视化 | RViz2 |
| 示例程序 | `turtlesim` |

## 学习路线

建议按以下顺序阅读和运行：

```text
Launch
  ↓
Rosbag2
  ↓
TF2
  ↓
URDF / Xacro
```

### 1. Launch

学习多个节点的统一启动、节点配置、参数文件、命令执行、文件包含、命名空间、分组和事件处理。

### 2. Rosbag2

学习话题数据录制、Bag 存储、消息读取、标准回放，以及 C++/Python 编程 API。

### 3. TF2

学习静态与动态坐标广播、坐标系监听、坐标点发布、坐标转换和消息过滤。

### 4. URDF 与 Xacro

学习 Link、Joint、机器人树、网格模型、状态发布器，以及通过属性、宏和文件包含构建四轮机器人模型。

## 仓库结构

```text
ros2_tools_learning/
├── docs/
│   ├── launch.md
│   ├── rosbag.md
│   ├── tf.md
│   └── urdf.md
├── src/
│   ├── learning_launch_cpp/
│   ├── learning_launch_py/
│   ├── learning_rosbag_cpp/
│   ├── learning_rosbag_py/
│   ├── learning_tf_cpp/
│   ├── learning_tf_py/
│   └── learning_urdf_cpp/
├── .clang-format
├── .gitignore
├── .vscode/
└── README.md
```

构建后会在工作空间根目录生成：

```text
build/
install/
log/
```

这些目录属于本地构建产物，已通过 `.gitignore` 排除，不应提交到 Git。

## 功能包总览

| 功能包 | 类型 | 主要内容 |
| --- | --- | --- |
| [`learning_launch_cpp`](src/learning_launch_cpp/README.md) | `ament_cmake` | Python、XML、YAML Launch 示例及参数配置 |
| [`learning_launch_py`](src/learning_launch_py/README.md) | `ament_python` | 与 CMake 包行为一致的 Launch 资源安装示例 |
| [`learning_rosbag_cpp`](src/learning_rosbag_cpp/README.md) | C++ | 使用 `rosbag2_cpp` 录制与读取 `Twist` 消息 |
| [`learning_rosbag_py`](src/learning_rosbag_py/README.md) | Python | 使用 `rosbag2_py` 顺序写入与读取消息 |
| [`learning_tf_cpp`](src/learning_tf_cpp/README.md) | C++ | 静态/动态广播、监听、点发布与点变换 |
| [`learning_tf_py`](src/learning_tf_py/README.md) | Python | 静态/动态广播、监听与点发布 |
| [`learning_urdf_cpp`](src/learning_urdf_cpp/README.md) | `ament_cmake` | URDF、Xacro、网格、Launch 和 RViz 资源 |

## 专题文档

`docs/` 中的文档用于脱离代码进行系统复习。

| 文档 | 内容 |
| --- | --- |
| [Launch 知识点总结](docs/launch.md) | 三种格式、节点配置、参数、替换、包含、分组和事件 |
| [Rosbag2 知识点总结](docs/rosbag.md) | CLI、存储、QoS、时间、C++/Python API 和数据管理 |
| [TF2 知识点总结](docs/tf.md) | 坐标树、广播监听、变换方向、时间和 MessageFilter |
| [URDF 与 Xacro 知识点总结](docs/urdf.md) | Link、Joint、视觉/碰撞/惯性、Xacro 和模型验证 |

功能包 README 侧重“示例如何运行”，专题文档侧重“知识体系如何理解和复习”。

## 环境准备

### 1. 安装 ROS 2

请先按照 ROS 2 官方方式安装 Ubuntu 22.04 对应的 ROS 2 Humble Desktop。

确保基础环境可以加载：

```bash
source /opt/ros/humble/setup.bash
ros2 --help
```

### 2. 安装示例依赖

```bash
sudo apt update
sudo apt install \
  ros-humble-turtlesim \
  ros-humble-rosbag2 \
  ros-humble-tf-transformations \
  ros-humble-tf2-tools \
  ros-humble-xacro \
  ros-humble-robot-state-publisher \
  ros-humble-joint-state-publisher \
  ros-humble-joint-state-publisher-gui \
  ros-humble-rviz2 \
  liburdfdom-tools
```

如果已经安装 ROS 2 Humble Desktop，其中部分依赖可能已经存在。

### 3. 避免 Conda 环境干扰

构建 ROS 2 工作空间前，建议确认终端没有激活 Conda：

```bash
conda deactivate
```

如果终端提示符没有 Conda 环境，可以忽略该命令。

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/zwj051029/ros2_tools_learning.git
cd ros2_tools_learning
```

### 2. 安装功能包依赖

```bash
source /opt/ros/humble/setup.bash
rosdep install --from-paths src --ignore-src -r -y
```

如果当前系统尚未初始化 `rosdep`，需要先完成对应初始化配置。

### 3. 构建全部功能包

```bash
colcon build --symlink-install
```

### 4. 加载工作空间

```bash
source install/setup.bash
```

每次打开新终端后，都需要重新加载 ROS 2 和当前工作空间环境：

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_tools_learning/install/setup.bash
```

如果仓库不在主目录，请使用实际绝对路径。

## 按功能包构建

只构建指定功能包：

```bash
colcon build --packages-select learning_tf_cpp
```

构建多个功能包：

```bash
colcon build --packages-select \
  learning_tf_cpp \
  learning_tf_py
```

修改 CMake、`setup.py`、新增文件或资源安装规则后，应重新构建对应功能包。

## 示例运行

下面只提供每个专题的最短入口。完整命令、终端安排和预期结果请查看对应功能包 README。

### Launch

运行 CMake 功能包中的 Python Launch：

```bash
ros2 launch learning_launch_cpp basic_launch.py
```

运行 XML 或 YAML 格式：

```bash
ros2 launch learning_launch_cpp basic_launch.xml
ros2 launch learning_launch_cpp basic_launch.yaml
```

运行 Python 功能包中的同类示例：

```bash
ros2 launch learning_launch_py basic_launch.py
```

### Rosbag2

先启动小乌龟和键盘控制：

```bash
ros2 run turtlesim turtlesim_node
```

```bash
ros2 run turtlesim turtle_teleop_key
```

运行 C++ 录制节点：

```bash
ros2 run learning_rosbag_cpp bag_recoder
```

读取录制结果：

```bash
ros2 run learning_rosbag_cpp bag_player
```

Python 对应命令：

```bash
ros2 run learning_rosbag_py bag_recoder
ros2 run learning_rosbag_py bag_player
```

自定义节点分别使用相对目录 `my_bag_cpp` 和 `my_bag_py`。录制与读取命令应在包含对应 Bag 目录的位置执行。

### TF2

发布 `base_link -> laser` 静态关系：

```bash
ros2 run learning_tf_cpp static_tf_broadcaster \
  0.4 0 0.2 0 0 0 base_link laser
```

发布 `laser` 坐标系中的点：

```bash
ros2 run learning_tf_cpp point_publisher
```

转换到 `base_link`：

```bash
ros2 run learning_tf_cpp point_transformer
```

检查坐标关系：

```bash
ros2 run tf2_ros tf2_echo base_link laser
```

### URDF 与 Xacro

显示默认盒状机器人：

```bash
ros2 launch learning_urdf_cpp display.launch.py
```

显示完整四轮传感器机器人：

```bash
ros2 launch learning_urdf_cpp display.launch.py \
  model:=$(ros2 pkg prefix --share learning_urdf_cpp)/urdf/xacro/four_wheel_robot.urdf.xacro
```

## 节点与可执行程序

### Rosbag2 C++

| 可执行程序 | 节点名称 | 作用 |
| --- | --- | --- |
| `bag_recoder` | `bag_recoder_cpp` | 订阅并录制 `/turtle1/cmd_vel` |
| `bag_player` | `bag_player_cpp` | 读取 Bag 并打印 `Twist` 字段 |

### Rosbag2 Python

| 可执行程序 | 节点名称 | 作用 |
| --- | --- | --- |
| `bag_recoder` | `simple_bag_recorder_py` | 序列化并写入速度消息 |
| `bag_player` | `simple_bag_player_py` | 读取并打印 Bag 原始记录 |

### TF2 C++

| 可执行程序 | 节点名称 | 作用 |
| --- | --- | --- |
| `static_tf_broadcaster` | `static_tf_broadcaster_cpp` | 静态坐标广播 |
| `dynamic_tf_broadcaster` | `dynamic_tf_broadcaster_cpp` | 小乌龟动态坐标广播 |
| `tf_listener` | `tf_listener_cpp` | 坐标系关系查询 |
| `point_publisher` | `point_publisher_cpp` | 发布 `PointStamped` |
| `point_transformer` | `point_transformer_cpp` | 使用 MessageFilter 转换坐标点 |

### TF2 Python

| 可执行程序 | 节点名称 | 作用 |
| --- | --- | --- |
| `static_tf_broadcaster` | `static_tf_broadcaster_py` | Python 静态坐标广播 |
| `dynamic_tf_broadcaster` | `dynamic_tf_broadcaster_py` | Python 动态坐标广播 |
| `tf_listener` | `tf_listener_py` | 查询坐标关系 |
| `point_publisher` | `point_publisher_py` | 发布 `PointStamped` |

Launch 和 URDF 功能包当前不提供自定义业务节点，主要用于安装和管理启动、配置与模型资源。

## 设计约定

### 功能包命名

```text
learning_<tool>_cpp
learning_<tool>_py
```

- `_cpp` 通常对应 `ament_cmake` 或 C++ 示例。
- `_py` 对应 `ament_python` 或 Python 示例。

### 代码风格

- C++ 使用 C++17。
- C++ 缩进为 4 个空格。
- C++ 格式由根目录 `.clang-format` 统一管理。
- Python 使用小写蛇形命名。
- ROS 2 节点名称包含语言后缀，便于运行时辨认。

### 资源路径

- 运行资源通过功能包共享目录查找。
- 不在源码中依赖个人电脑的绝对路径。
- Launch、配置、URDF、Xacro、Mesh 和 RViz 文件必须通过构建系统安装。

## 验证方式

检查全部功能包是否可被发现：

```bash
colcon list
```

构建全部功能包：

```bash
source /opt/ros/humble/setup.bash
colcon build --symlink-install
```

查看指定包的可执行程序：

```bash
source install/setup.bash
ros2 pkg executables learning_tf_cpp
```

检查 Launch 参数而不长期启动图形节点：

```bash
ros2 launch learning_launch_cpp basic_launch.py --show-args
```

展开并验证最终 Xacro 模型：

```bash
xacro \
  $(ros2 pkg prefix --share learning_urdf_cpp)/urdf/xacro/four_wheel_robot.urdf.xacro \
  > /tmp/four_wheel_robot.urdf

check_urdf /tmp/four_wheel_robot.urdf
```

本仓库中的功能包和文档已按学习阶段进行过构建或解析验证，但仓库当前没有持续集成流水线和完整自动化集成测试。运行结果仍取决于本机 ROS 2 安装、中间件、图形环境和系统依赖。

## 常见问题

### 找不到功能包

```text
Package '<package_name>' not found
```

执行：

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
```

并确认目标功能包已经成功构建。

### 修改后仍运行旧内容

ROS 2 通常从 `install/` 目录运行安装结果。重新执行：

```bash
colcon build --packages-select <package_name>
source install/setup.bash
```

### Conda 导致 CMake 找不到 Python 依赖

如果构建日志显示使用了 Miniconda Python，并出现 `catkin_pkg` 等模块缺失：

```bash
conda deactivate
source /opt/ros/humble/setup.bash
```

然后重新构建。

### Rosbag 输出目录冲突

自定义 Writer 使用固定的相对目录。再次录制前应移动旧 Bag 或选择新的存储位置，不要误覆盖需要保留的数据。

### TF 查询失败

依次检查：

```bash
ros2 topic echo /tf_static
ros2 topic echo /tf
ros2 run tf2_ros tf2_echo <source_frame> <target_frame>
ros2 run tf2_tools view_frames
```

重点核对坐标系名称、父子关系、时间戳和 TF 树连通性。

### RViz 中不显示机器人

检查：

- `robot_state_publisher` 是否运行。
- `/robot_description` 是否存在。
- RViz RobotModel 是否启用。
- Fixed Frame 是否为模型中的有效 Link。
- Mesh 是否已安装且 `package://` 路径正确。

## 已知边界

- Launch 示例以 `turtlesim` 为主，用于学习语法而非机器人整机启动。
- 自定义 Rosbag2 Reader 侧重 API 学习，不具备标准 Player 的全部定时回放能力。
- Python TF2 包没有单独实现坐标点变换节点，可与 C++ 节点跨语言配合。
- URDF 示例以结构和 RViz 展示为主，尚未完整配置碰撞、惯性、Gazebo 和 `ros2_control`。
- 仓库未包含真实机器人驱动、导航栈、控制器和硬件接口。
- Bag 数据通常体积较大，不建议直接提交到 Git 仓库。

## 维护建议

本仓库已作为阶段性学习成果归档。后续如需继续扩展，建议：

1. 在独立仓库学习 Gazebo、Nav2、MoveIt 2 和 `ros2_control`。
2. 为可复用机器人模型补充 Collision、Inertial 和控制配置。
3. 为关键节点增加自动化测试和 Launch Test。
4. 清理各功能包模板中的描述与许可证占位内容。
5. 为大型 Bag 数据建立独立存储和版本说明。
6. 在真实机器人项目前固定 TF 命名、参数和消息接口规范。

## 许可证

当前仓库尚未提供独立的 `LICENSE` 文件，因此不要默认其内容属于某种开源许可证。代码和文档主要用于个人学习、复习与交流；如需复制、分发或用于其他项目，应先确认仓库后续采用的许可条款。

## 相关仓库

- ROS 2 四大通信与参数学习仓库：`ros2_learning`
- 当前工具学习仓库：`ros2_tools_learning`

## 总结

本仓库将 ROS 2 常用工具按照可运行示例、包级说明和专题笔记三个层次组织：

```text
源码示例     用于动手运行
功能包 README 用于理解当前示例
docs 专题笔记 用于长期复习
```

从 Launch 的系统编排，到 Rosbag2 的数据复现，再到 TF2 的坐标统一和 URDF/Xacro 的机器人结构描述，这些工具共同构成了 ROS 2 机器人开发的重要基础。
