# ROS 2 URDF 与 Xacro 机器人建模学习示例

## 功能包说明

`learning_urdf_cpp` 用于学习 ROS 2 机器人描述与可视化，内容涵盖 URDF 基础语法、几何体与网格模型、Link、Joint、`base_footprint`、四轮机器人建模，以及 Xacro 属性、宏和文件拆分。

功能包使用 `ament_cmake` 管理和安装模型资源。虽然名称带有 `_cpp` 后缀，但当前包不编译自定义 C++ 节点，主要包含：

- URDF 与 Xacro 机器人模型。
- STL 网格资源。
- 统一的模型显示 Launch 文件。
- RViz2 显示配置。

## 环境要求

| 项目 | 要求 |
| --- | --- |
| 操作系统 | Ubuntu 22.04 |
| ROS 2 | Humble Hawksbill |
| 构建类型 | `ament_cmake` |
| 模型格式 | URDF、Xacro |
| 状态发布 | `robot_state_publisher`、`joint_state_publisher` |
| 可视化工具 | RViz2 |
| 启动工具 | `ros2launch` |

如果缺少相关工具，可以安装：

```bash
sudo apt install \
  ros-humble-xacro \
  ros-humble-robot-state-publisher \
  ros-humble-joint-state-publisher \
  ros-humble-joint-state-publisher-gui \
  ros-humble-rviz2
```

## 目录结构

```text
learning_urdf_cpp/
├── launch/
│   └── display.launch.py
├── meshes/
│   └── burger_base.stl
├── rviz/
│   └── urdf.rviz
├── urdf/
│   ├── urdf/
│   │   ├── base_footprint.urdf
│   │   ├── box_robot.urdf
│   │   ├── box_robot_copy.urdf
│   │   ├── four_wheel_robot.urdf
│   │   ├── joint.urdf
│   │   └── link.urdf
│   └── xacro/
│       ├── four_wheel_robot.urdf.xacro
│       ├── four_wheel_robot_base.urdf.xacro
│       ├── four_wheel_robot_camera.urdf.xacro
│       ├── four_wheel_robot_lidar.urdf.xacro
│       └── wheel_macro_demo.urdf.xacro
├── CMakeLists.txt
├── package.xml
└── README.md
```

`CMakeLists.txt` 将以下目录完整安装到功能包共享目录：

```text
install/learning_urdf_cpp/share/learning_urdf_cpp/
├── launch/
├── meshes/
├── rviz/
└── urdf/
```

因此新增或修改模型资源后，需要重新构建功能包，确保 `install/` 中的副本得到更新。

## 模型文件总览

### URDF 示例

| 文件 | 学习内容 |
| --- | --- |
| `box_robot.urdf` | 使用 `box` 创建单 Link 盒状机器人 |
| `box_robot_copy.urdf` | 盒状模型的尺寸修改与文件加载练习 |
| `link.urdf` | `visual`、基础几何体、材质、原点和 STL 网格引用 |
| `joint.urdf` | 两个 Link、连续关节、父子关系、关节原点和旋转轴 |
| `base_footprint.urdf` | 使用虚拟地面投影坐标系组织底盘与相机 |
| `four_wheel_robot.urdf` | 完整描述底盘和四个连续关节车轮 |

### Xacro 示例

| 文件 | 学习内容 |
| --- | --- |
| `wheel_macro_demo.urdf.xacro` | 使用属性和宏批量生成四个车轮 Link |
| `four_wheel_robot_base.urdf.xacro` | 参数化底盘尺寸，并用带参数宏创建四个车轮 |
| `four_wheel_robot_camera.urdf.xacro` | 定义相机 Link 及其固定关节 |
| `four_wheel_robot_lidar.urdf.xacro` | 定义激光雷达 Link 及其固定关节 |
| `four_wheel_robot.urdf.xacro` | 使用 `xacro:include` 组合底盘、相机和激光雷达 |

`wheel_macro_demo.urdf.xacro` 主要演示宏展开，生成的四个车轮 Link 之间没有 Joint 连接，因此它不是用于完整机器人显示的最终模型。

## 构建

在工作空间根目录执行：

```bash
source /opt/ros/humble/setup.bash
colcon build --packages-select learning_urdf_cpp
source install/setup.bash
```

查询安装后的功能包共享目录：

```bash
ros2 pkg prefix --share learning_urdf_cpp
```

## 显示 Launch 文件

`display.launch.py` 统一启动以下三个组件：

| 组件 | 作用 |
| --- | --- |
| `robot_state_publisher` | 读取 `robot_description`，发布机器人各 Link 之间的 TF |
| `joint_state_publisher` | 为可运动关节发布 `/joint_states` |
| `rviz2` | 加载 `rviz/urdf.rviz` 并显示 RobotModel |

Launch 文件声明了 `model` 参数，默认值为：

```text
urdf/urdf/box_robot.urdf
```

模型文件通过以下逻辑转换为 `robot_description` 参数：

```python
ParameterValue(Command(['xacro ', LaunchConfiguration('model')]))
```

`xacro` 能够处理 `.urdf.xacro`，也可以直接读取普通 `.urdf`，因此同一个 Launch 文件可以显示两种格式的模型。

RViz 配置使用：

```text
Fixed Frame: base_link
Robot Description Topic: /robot_description
```

所加载的模型应包含 `base_link`。如果改用不含该 Link 的模型，需要同步修改 RViz 的 Fixed Frame。

## 基础运行

### 显示默认盒状机器人

```bash
source install/setup.bash
ros2 launch learning_urdf_cpp display.launch.py
```

预期现象：

- 启动 `robot_state_publisher`。
- 启动 `joint_state_publisher`。
- 打开 RViz2。
- 显示一个尺寸为 `1.0 x 0.5 x 0.1` 的盒状模型。

### 指定模型文件

推荐使用命令替换获取安装后的共享目录：

```bash
ros2 launch learning_urdf_cpp display.launch.py \
  model:=$(ros2 pkg prefix --share learning_urdf_cpp)/urdf/urdf/joint.urdf
```

`model:=` 与路径之间不能插入空格，否则路径会被解析为另一个 Launch 参数。

也可以使用源码目录中的绝对路径，但正常运行和发布仓库时更推荐使用安装后的共享目录。

## URDF 基础语法

### Robot

每个 URDF 都以 `<robot>` 作为根元素：

```xml
<robot name="box_robot">
    ...
</robot>
```

`name` 用于标识机器人模型。

### Link

`<link>` 表示机器人中的刚体部件，例如底盘、车轮、相机或激光雷达：

```xml
<link name="base_link">
    <visual>...</visual>
</link>
```

当前示例主要使用 `<visual>` 描述 RViz 中的外观。

### Visual

`<visual>` 常用子元素包括：

| 元素 | 作用 |
| --- | --- |
| `<geometry>` | 描述形状或网格 |
| `<origin>` | 设置视觉模型相对于 Link 坐标系的位置和姿态 |
| `<material>` | 设置颜色或引用已定义材质 |

### 几何体

示例覆盖了常见几何形式：

```xml
<box size="1.0 0.5 0.1"/>
<sphere radius="0.5"/>
<cylinder radius="0.025" length="0.02"/>
```

尺寸与位置默认使用米，`rpy` 默认使用弧度。

### 网格模型

`link.urdf` 使用 STL 文件显示机器人底座：

```xml
<mesh
    filename="package://learning_urdf_cpp/meshes/burger_base.stl"
    scale="0.01 0.01 0.01"/>
```

`package://` URI 会从已安装的功能包共享资源中定位文件，避免把本机绝对路径写入模型。

`scale` 分别控制 X、Y、Z 三个方向的缩放比例。网格模型过大或过小时，应先检查模型原始单位和缩放值。

## Joint 关节

Joint 用于连接父 Link 与子 Link：

```xml
<joint name="base_to_camera_joint" type="continuous">
    <parent link="base_link"/>
    <child link="camera_link"/>
    <origin xyz="0.2 0.0 0.075" rpy="0.0 0.0 0.0"/>
    <axis xyz="0.0 0.0 1.0"/>
</joint>
```

各部分作用如下：

| 元素 | 作用 |
| --- | --- |
| `type` | 关节类型 |
| `<parent>` | 父 Link |
| `<child>` | 子 Link |
| `<origin>` | 子 Link 关节坐标系相对于父 Link 的位置与姿态 |
| `<axis>` | 旋转或移动的轴向 |

当前工程主要使用两种关节：

| 类型 | 特点 | 示例 |
| --- | --- | --- |
| `fixed` | 不能运动，父子关系固定 | 底盘、相机、激光雷达 |
| `continuous` | 可以绕指定轴无限旋转 | 相机练习关节、四个车轮关节 |

## `base_footprint` 的作用

`base_footprint` 通常表示机器人底盘在地面上的投影坐标系。它适合作为移动机器人在平面上定位和导航时的参考，而 `base_link` 通常位于机器人实体底盘中心附近。

`base_footprint.urdf` 中的关系为：

```text
base_footprint
└── base_link
    └── camera_link
```

`base_footprint` 使用半径为 `0.001` 的球体，仅用于让 Link 拥有一个几乎不可见的视觉元素。它通过固定关节连接到 `base_link`。

## 四轮机器人 URDF

`four_wheel_robot.urdf` 使用普通 URDF 完整描述四轮底盘，坐标树为：

```text
base_footprint
└── base_link
    ├── front_left_wheel_link
    ├── front_right_wheel_link
    ├── rear_left_wheel_link
    └── rear_right_wheel_link
```

模型主要尺寸如下：

| 部件 | 尺寸 |
| --- | --- |
| 底盘 | `0.20 x 0.12 x 0.07` 米 |
| 车轮半径 | `0.025` 米 |
| 车轮宽度 | `0.02` 米 |

四个车轮均使用圆柱体。视觉模型绕 X 轴旋转约 `1.5708` 弧度，使圆柱轴线与车轮旋转方向一致；对应 Joint 使用 Y 轴作为旋转轴。

运行命令：

```bash
ros2 launch learning_urdf_cpp display.launch.py \
  model:=$(ros2 pkg prefix --share learning_urdf_cpp)/urdf/urdf/four_wheel_robot.urdf
```

## Xacro 基础

Xacro 在 URDF XML 的基础上提供属性、表达式、宏和文件包含，适合减少重复内容并拆分复杂机器人模型。

### 属性与表达式

底盘文件集中定义尺寸：

```xml
<xacro:property name="base_length" value="0.20"/>
<xacro:property name="base_width" value="0.12"/>
<xacro:property name="base_height" value="0.07"/>
```

使用 `${...}` 引用属性或执行计算：

```xml
<box size="${base_length} ${base_width} ${base_height}"/>
```

修改属性后，所有引用位置都会同步变化。

### 宏

`four_wheel_robot_base.urdf.xacro` 定义了车轮宏：

```xml
<xacro:macro name="wheel" params="wheel_name x_sign y_sign">
    ...
</xacro:macro>
```

参数用途如下：

| 参数 | 作用 |
| --- | --- |
| `wheel_name` | 生成唯一的 Link 和 Joint 名称 |
| `x_sign` | 决定车轮位于前方还是后方 |
| `y_sign` | 决定车轮位于左侧还是右侧 |

宏被调用四次，从同一份定义生成四个车轮：

```xml
<xacro:wheel wheel_name="front_left" x_sign="1" y_sign="1"/>
<xacro:wheel wheel_name="front_right" x_sign="1" y_sign="-1"/>
<xacro:wheel wheel_name="rear_left" x_sign="-1" y_sign="1"/>
<xacro:wheel wheel_name="rear_right" x_sign="-1" y_sign="-1"/>
```

### 文件包含

最终模型 `four_wheel_robot.urdf.xacro` 通过以下内容组合多个模块：

```xml
<xacro:include filename="four_wheel_robot_base.urdf.xacro"/>
<xacro:include filename="four_wheel_robot_camera.urdf.xacro"/>
<xacro:include filename="four_wheel_robot_lidar.urdf.xacro"/>
```

拆分后的职责为：

- `four_wheel_robot_base.urdf.xacro`：底盘、材质、四个车轮和公共尺寸。
- `four_wheel_robot_camera.urdf.xacro`：前部相机及其固定关节。
- `four_wheel_robot_lidar.urdf.xacro`：顶部激光雷达及其固定关节。

因为被包含文件共享同一个 Xacro 处理上下文，相机和雷达文件可以使用底盘文件中定义的 `base_length`、`base_height` 和材质。

## 完整 Xacro 机器人

最终机器人坐标树为：

```text
base_footprint
└── base_link
    ├── front_left_wheel_link
    ├── front_right_wheel_link
    ├── rear_left_wheel_link
    ├── rear_right_wheel_link
    ├── camera_link
    └── lidar_link
```

显示完整模型：

```bash
ros2 launch learning_urdf_cpp display.launch.py \
  model:=$(ros2 pkg prefix --share learning_urdf_cpp)/urdf/xacro/four_wheel_robot.urdf.xacro
```

预期现象：

- 蓝色长方体底盘。
- 四个黑色圆柱车轮。
- 底盘前部的红色相机。
- 底盘顶部的深蓝色圆柱激光雷达。

## 模型检查

### 展开 Xacro

将最终 Xacro 展开为普通 URDF：

```bash
xacro \
  $(ros2 pkg prefix --share learning_urdf_cpp)/urdf/xacro/four_wheel_robot.urdf.xacro \
  > /tmp/four_wheel_robot.urdf
```

查看展开结果：

```bash
less /tmp/four_wheel_robot.urdf
```

### 检查 URDF 结构

如果系统安装了 `check_urdf`，可以执行：

```bash
check_urdf /tmp/four_wheel_robot.urdf
```

它可以检查 XML、Link、Joint 和整棵机器人树的基本结构。

### 检查 ROS 2 数据

Launch 启动后查看机器人描述参数：

```bash
ros2 param get /robot_state_publisher robot_description
```

查看关节状态：

```bash
ros2 topic echo /joint_states
```

查看机器人 TF：

```bash
ros2 topic echo /tf_static
ros2 topic echo /tf
```

## Joint State 与 Robot State Publisher

两类发布器承担不同职责：

| 组件 | 输入或依据 | 输出 |
| --- | --- | --- |
| `joint_state_publisher` | URDF 中可运动关节 | `/joint_states` |
| `robot_state_publisher` | `robot_description` 与 `/joint_states` | `/tf`、`/tf_static` |

固定关节关系可以直接从模型计算；连续关节的动态姿态需要对应的 Joint State。

功能包已声明 `joint_state_publisher_gui` 运行依赖，但当前 Launch 启动的是普通 `joint_state_publisher`。如需通过滑块手动调节关节，应在启动配置中改用 GUI 版本，并避免同时运行两个 Joint State 发布器。

## 模型适用范围

当前模型重点用于学习 URDF/Xacro 语法和 RViz 可视化，主要定义了 `<visual>`。它们尚未完整包含：

- `<collision>` 碰撞模型。
- `<inertial>` 质量和惯性参数。
- Gazebo 仿真插件。
- `transmission` 传动配置。
- `ros2_control` 控制接口。

因此这些文件适合在 RViz 中观察机器人结构和 TF，但还不是可以直接用于可靠物理仿真的完整机器人描述。

## 常见问题

### 找不到功能包或 Launch 文件

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
```

如果刚修改或新增模型资源，应重新构建功能包。

### 修改源码模型后 RViz 没有变化

Launch 默认从 `install/learning_urdf_cpp/share/learning_urdf_cpp` 读取模型。修改 `src/` 后需要重新执行：

```bash
colcon build --packages-select learning_urdf_cpp
source install/setup.bash
```

### `model` 参数格式错误

正确写法：

```bash
model:=$(ros2 pkg prefix --share learning_urdf_cpp)/urdf/urdf/link.urdf
```

不要写成两个独立参数：

```text
model:=<功能包路径> /urdf/urdf/link.urdf
```

路径中间的空格会让 Launch 把后半部分识别为格式不合法的额外参数。

### RViz 启动但没有显示模型

依次检查：

- RobotModel 显示项是否启用。
- Description Topic 是否为 `/robot_description`。
- Fixed Frame 是否是模型中存在的 Link，当前配置为 `base_link`。
- `robot_state_publisher` 是否正常运行。
- 终端是否出现 Xacro、XML 或资源路径错误。

### STL 网格无法显示

检查以下内容：

- `meshes/burger_base.stl` 是否已安装到功能包共享目录。
- URI 是否使用 `package://learning_urdf_cpp/...`。
- `scale` 是否合适。
- 修改资源后是否重新构建并刷新环境。

### Xacro 提示属性未定义

最终入口文件应先包含定义公共属性的 `four_wheel_robot_base.urdf.xacro`，再包含依赖这些属性的相机和激光雷达文件。改变包含顺序时需要注意属性的可见性。

### 出现多个根 Link

完整 URDF 必须通过 Joint 将所有 Link 连接成一棵树。`wheel_macro_demo.urdf.xacro` 只生成独立车轮，用于宏语法练习，不应当作最终完整机器人模型。

### 车轮方向不正确

圆柱默认沿 Z 轴延伸。示例通过约 `1.5708` 弧度的 Roll 将车轮视觉模型旋转，并将连续关节轴设置为 Y 轴。应同时检查 `<visual><origin>` 和 `<joint><axis>`。

## 学习要点

- URDF 中 `robot`、`link`、`visual`、`geometry`、`origin` 和 `material` 的作用。
- `box`、`sphere`、`cylinder` 与 STL `mesh` 的使用方法。
- Joint 的父子 Link、原点、轴向和关节类型。
- `base_footprint` 与 `base_link` 在移动机器人中的常见职责。
- 使用 `robot_state_publisher` 将机器人描述转换为 TF。
- 使用 `joint_state_publisher` 提供可运动关节状态。
- Launch 参数、`Command` 与 `ParameterValue` 加载 URDF/Xacro 的过程。
- Xacro 属性、数学表达式、宏参数和文件包含。
- 通过宏减少四个车轮结构中的重复定义。
- 将底盘、相机与激光雷达拆分为可维护的模型模块。
- 使用 RViz、`xacro`、`check_urdf` 和 ROS 2 CLI 排查模型问题。
- 区分可视化模型与具备碰撞、惯性和控制配置的仿真模型。
