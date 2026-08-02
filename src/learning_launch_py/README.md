# ROS 2 Launch 学习示例（ament_python）

## 功能包说明

`learning_launch_py` 用于学习 ROS 2 Launch 系统，通过同一组 `turtlesim` 案例对照演示 Python、XML 和 YAML 三种启动文件格式。

功能包使用 `ament_python` 构建，因此名称带有 `_py` 后缀；当前包没有自定义 Python 节点，主要负责安装和管理 Launch 文件及参数配置。

对应的 `ament_cmake` 功能包为 `learning_launch_cpp`。

## 环境要求

| 项目 | 要求 |
| --- | --- |
| 操作系统 | Ubuntu 22.04 |
| ROS 2 | Humble Hawksbill |
| 构建工具 | `colcon`、`ament_python` |
| Python 构建工具 | `setuptools` |
| 示例节点 | `turtlesim` |
| 启动工具 | `ros2launch` |

如果缺少 `turtlesim`，可以安装：

```bash
sudo apt install ros-humble-turtlesim
```

## 目录结构

```text
learning_launch_py/
├── config/
│   └── turtlesim.yaml
├── launch/
│   ├── py/
│   │   ├── basic_launch.py
│   │   ├── command_launch.py
│   │   ├── event_launch.py
│   │   ├── group_launch.py
│   │   ├── include_launch.py
│   │   ├── node_config_launch.py
│   │   └── parameters_launch.py
│   ├── xml/
│   │   ├── basic_launch.xml
│   │   ├── command_launch.xml
│   │   ├── group_launch.xml
│   │   ├── include_launch.xml
│   │   ├── node_config_launch.xml
│   │   └── parameters_launch.xml
│   └── yaml/
│       ├── basic_launch.yaml
│       ├── command_launch.yaml
│       ├── group_launch.yaml
│       ├── include_launch.yaml
│       ├── node_config_launch.yaml
│       └── parameters_launch.yaml
├── learning_launch_py/
│   └── __init__.py
├── resource/
│   └── learning_launch_py
├── test/
├── package.xml
├── setup.cfg
├── setup.py
└── README.md
```

## 安装机制

`setup.py` 通过 `data_files` 将资源安装到功能包的共享目录：

```text
install/learning_launch_py/share/learning_launch_py/
├── config/
├── launch/
│   ├── py/
│   ├── xml/
│   └── yaml/
└── package.xml
```

其中的 `glob()` 会收集符合以下规则的文件：

```text
launch/py/*_launch.py
launch/xml/*_launch.xml
launch/yaml/*_launch.yaml
config/*.yaml
```

新增 Launch 文件时，应遵循对应的文件名后缀，并在修改后重新构建功能包。

当前 `entry_points['console_scripts']` 为空，因为本功能包没有需要通过 `ros2 run` 启动的自定义 Python 节点。

## 示例总览

| 示例 | Python | XML | YAML | 学习内容 |
| --- | --- | --- | --- | --- |
| 基础启动 | `basic_launch.py` | `basic_launch.xml` | `basic_launch.yaml` | 同时创建多个节点并设置节点名称 |
| 节点配置 | `node_config_launch.py` | `node_config_launch.xml` | `node_config_launch.yaml` | 从参数文件加载节点配置 |
| 命令执行 | `command_launch.py` | `command_launch.xml` | `command_launch.yaml` | 在 Launch 中执行 ROS 2 CLI 命令 |
| 启动参数 | `parameters_launch.py` | `parameters_launch.xml` | `parameters_launch.yaml` | 声明、读取和传递 Launch 参数 |
| 文件包含 | `include_launch.py` | `include_launch.xml` | `include_launch.yaml` | 包含并复用其他启动文件 |
| 分组设置 | `group_launch.py` | `group_launch.xml` | `group_launch.yaml` | 使用分组和命名空间组织节点 |
| 事件处理 | `event_launch.py` | - | - | 根据进程启动和退出事件触发动作 |

## 构建

在工作空间根目录执行：

```bash
source /opt/ros/humble/setup.bash
colcon build --packages-select learning_launch_py
source install/setup.bash
```

修改 Launch 文件或参数文件后，需要重新构建，确保最新文件安装到工作空间的 `install/` 目录。

## 运行方式

### Python 格式

```bash
ros2 launch learning_launch_py basic_launch.py
```

### XML 格式

```bash
ros2 launch learning_launch_py basic_launch.xml
```

### YAML 格式

```bash
ros2 launch learning_launch_py basic_launch.yaml
```

三个命令实现相同的基础行为：创建名为 `t1` 和 `t2` 的两个 `turtlesim_node` 节点。

## 核心案例

### 1. 节点配置

```bash
ros2 launch learning_launch_py node_config_launch.py
ros2 launch learning_launch_py node_config_launch.xml
ros2 launch learning_launch_py node_config_launch.yaml
```

三个启动文件都会加载：

```text
config/turtlesim.yaml
```

配置文件将 `/turtlesim` 节点的背景颜色设置为绿色：

```yaml
background_r: 0
background_g: 255
background_b: 0
```

Python 示例中还保留了节点名称、命名空间、进程标签、自动重启、话题重映射和 `ros_arguments` 的写法，便于对照学习。

### 2. 命令执行

```bash
ros2 launch learning_launch_py command_launch.py
ros2 launch learning_launch_py command_launch.xml
ros2 launch learning_launch_py command_launch.yaml
```

启动流程包括：

1. 启动 `turtlesim_node`。
2. 调用 `/spawn` 服务创建 `my_turtle`。
3. 持续输出 `/turtle1/pose` 话题。

Python 使用 `ExecuteProcess`，XML 和 YAML 使用 `executable` 描述外部命令。

### 3. 启动参数

```bash
ros2 launch learning_launch_py parameters_launch.py r:=255 g:=0 b:=0
ros2 launch learning_launch_py parameters_launch.xml r:=255 g:=0 b:=0
ros2 launch learning_launch_py parameters_launch.yaml r:=255 g:=0 b:=0
```

`r`、`g` 和 `b` 的默认值均为 `255`。传入不同数值可以修改 `turtlesim` 背景颜色。

查看启动文件支持的参数：

```bash
ros2 launch learning_launch_py parameters_launch.py --show-args
```

### 4. 文件包含

```bash
ros2 launch learning_launch_py include_launch.py
ros2 launch learning_launch_py include_launch.xml
ros2 launch learning_launch_py include_launch.yaml
```

三个文件分别包含对应格式的 `parameters_launch`，演示启动逻辑的拆分与复用。Python 版本使用：

- `IncludeLaunchDescription`
- `PythonLaunchDescriptionSource`
- `get_package_share_directory()`

XML 和 YAML 版本使用 `find-pkg-share` 查找功能包的安装路径。

### 5. 分组与命名空间

```bash
ros2 launch learning_launch_py group_launch.py
ros2 launch learning_launch_py group_launch.xml
ros2 launch learning_launch_py group_launch.yaml
```

节点分组如下：

```text
/g1/t1
/g1/t2
/g2/t3
```

分组能够为一组节点统一设置命名空间，适合多机器人或相同组件的多实例部署。

### 6. 事件处理

```bash
ros2 launch learning_launch_py event_launch.py
```

该案例使用：

- `OnProcessStart`：`turtlesim_node` 启动后调用 `/spawn` 服务。
- `OnProcessExit`：`turtlesim_node` 退出后打印退出日志。
- `RegisterEventHandler`：将事件条件和响应动作注册到 Launch 系统。

事件示例目前只提供 Python 格式的启动文件。

## 运行检查

启动案例后，可以在新终端检查节点和命名空间：

```bash
source install/setup.bash
ros2 node list
```

检查参数是否加载：

```bash
ros2 param get /turtlesim background_r
ros2 param get /turtlesim background_g
ros2 param get /turtlesim background_b
```

检查生成的乌龟和位姿话题：

```bash
ros2 service list | grep spawn
ros2 topic echo /turtle1/pose
```

按 `Ctrl+C` 可以关闭由 Launch 启动的全部进程。

## 三种格式对比

| 格式 | 优点 | 适用场景 |
| --- | --- | --- |
| Python | 可编程能力强，支持条件、事件和复杂组合 | 中大型项目、动态启动逻辑 |
| XML | 结构直观，标签语义清晰 | 配置较固定、强调可读性的启动文件 |
| YAML | 内容紧凑，配置感较强 | 简单节点编排和格式对照学习 |

实际项目通常优先使用 Python Launch；XML 和 YAML 适合配置较简单的场景。

## 常见问题

### 找不到功能包或启动文件

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
```

如果刚修改或新增文件，应先重新构建功能包。

### 新增的 Launch 文件没有被安装

确认文件名符合 `setup.py` 中 `glob()` 的匹配规则，然后重新执行：

```bash
colcon build --packages-select learning_launch_py
source install/setup.bash
```

### `turtlesim` 节点启动失败

确认已安装：

```bash
ros2 pkg prefix turtlesim
```

### 参数没有生效

检查 YAML 文件中的节点键名是否与实际节点完整名称一致。当前配置文件使用 `/turtlesim`，因此适用于默认名称的 `turtlesim_node`。

### 多个窗口或节点名称冲突

基础和分组案例会同时创建多个 `turtlesim` 实例，这是预期行为。节点重名时应通过 `name` 或命名空间区分。

## 学习要点

- `ament_python` 功能包中非 Python 模块资源的安装方法。
- `setup.py`、`data_files` 与 `glob()` 的作用。
- `LaunchDescription` 与 Launch Action 的组织方式。
- `Node` 的包名、可执行文件、节点名、命名空间、参数和重映射配置。
- `ExecuteProcess` 与外部命令执行。
- `DeclareLaunchArgument`、`LaunchConfiguration` 与运行时参数覆盖。
- 启动文件包含、功能包共享目录查询和逻辑复用。
- `GroupAction`、`PushRosNamespace` 与多实例组织。
- 进程启动、退出事件及事件处理器。
- Python、XML、YAML 三种 Launch 描述格式的对应关系。
