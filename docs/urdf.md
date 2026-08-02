# ROS 2 URDF 与 Xacro 机器人建模知识点总结

## 1. URDF 是什么

URDF 全称为 Unified Robot Description Format，是一种基于 XML 的机器人描述格式。

它主要用于描述：

- 机器人由哪些刚体部件组成。
- 各部件之间通过什么关节连接。
- 每个部件的外观、碰撞形状、质量和惯性。
- 关节的位置、方向、运动类型和限制。
- 网格模型、材质和颜色。
- 机器人整体的树形结构。

URDF 不负责实现机器人的运动控制逻辑。它描述的是“机器人是什么结构”，而节点和控制器负责“机器人如何运动”。

一句话理解：

```text
URDF 是机器人机械结构、坐标关系和物理属性的统一说明书。
```

## 2. URDF 在 ROS 2 中的位置

典型数据流：

```text
URDF / Xacro 文件
        │
        ▼
robot_description 参数
        │
        ▼
robot_state_publisher
        │               ▲
        │               │ /joint_states
        ▼               │
   /tf、/tf_static   joint_state_publisher
        │
        ▼
RViz、导航、感知、控制和其他 TF2 使用者
```

核心关系：

- URDF 定义 Link 和 Joint。
- `joint_state_publisher` 提供可运动关节的当前位置。
- `robot_state_publisher` 根据 URDF 和关节状态计算 TF。
- RViz 根据 TF 和视觉模型显示机器人。

## 3. URDF 的基本结构

最小模型：

```xml
<?xml version="1.0"?>
<robot name="simple_robot">
    <link name="base_link">
        <visual>
            <geometry>
                <box size="1.0 0.5 0.2"/>
            </geometry>
        </visual>
    </link>
</robot>
```

根元素必须是 `<robot>`：

```xml
<robot name="robot_name">
    ...
</robot>
```

机器人内部最重要的两个元素：

```text
Link   刚体部件
Joint  连接两个 Link 的关节
```

## 4. Link

Link 表示机器人中的一个刚体，例如：

- 底盘。
- 车轮。
- 相机外壳。
- 激光雷达。
- 机械臂连杆。
- 末端执行器。

典型结构：

```xml
<link name="base_link">
    <visual>...</visual>
    <collision>...</collision>
    <inertial>...</inertial>
</link>
```

三个组成部分：

| 元素 | 作用 |
| --- | --- |
| `<visual>` | 决定在 RViz 或仿真界面中的外观 |
| `<collision>` | 决定物理仿真和碰撞检测使用的形状 |
| `<inertial>` | 描述质量、质心和惯性张量 |

只写 `<visual>` 的模型可以用于基础 RViz 展示，但不能直接视为可靠的物理仿真模型。

## 5. Visual

`<visual>` 描述 Link 的显示效果：

```xml
<visual>
    <origin xyz="0 0 0" rpy="0 0 0"/>
    <geometry>
        <box size="0.5 0.3 0.1"/>
    </geometry>
    <material name="blue">
        <color rgba="0.1 0.4 0.8 1.0"/>
    </material>
</visual>
```

`visual/origin` 表示视觉几何体相对于当前 Link 坐标系的位置和姿态。

一个 Link 可以包含多个 `<visual>`，但复杂模型通常更适合拆成多个 Link，或者使用完整网格文件。

## 6. Collision

`<collision>` 描述碰撞检测使用的形状：

```xml
<collision>
    <origin xyz="0 0 0" rpy="0 0 0"/>
    <geometry>
        <box size="0.5 0.3 0.1"/>
    </geometry>
</collision>
```

碰撞模型不一定与视觉模型完全相同。

工程中常用简化碰撞体：

```text
复杂外观网格  -> 简单 Box、Cylinder 或低面数网格
```

原因：

- 降低碰撞检测计算量。
- 提高仿真实时性。
- 减少不规则网格造成的接触不稳定。
- 让模型更容易调试。

碰撞体应尽量覆盖真实机器人外形，但不必保留所有视觉细节。

## 7. Inertial

`<inertial>` 描述物理属性：

```xml
<inertial>
    <origin xyz="0 0 0" rpy="0 0 0"/>
    <mass value="5.0"/>
    <inertia
        ixx="0.1" ixy="0.0" ixz="0.0"
        iyy="0.2" iyz="0.0"
        izz="0.3"/>
</inertial>
```

含义：

| 元素 | 作用 |
| --- | --- |
| `inertial/origin` | 质心和惯性坐标系相对于 Link 坐标系的位置与姿态 |
| `<mass>` | Link 质量，单位为千克 |
| `<inertia>` | 绕质心表示的 3 x 3 惯性张量 |

惯性矩阵：

```text
| ixx  ixy  ixz |
| ixy  iyy  iyz |
| ixz  iyz  izz |
```

惯性参数不能随便填写。错误、全零或不满足物理条件的惯性可能导致仿真抖动、爆炸或模型无法加载。

## 8. 常见形状惯性公式

以下公式假设质心位于几何中心，且惯性坐标轴与形状主轴重合。

### 长方体

质量为 `m`，X、Y、Z 方向尺寸分别为 `x`、`y`、`z`：

```text
Ixx = m * (y^2 + z^2) / 12
Iyy = m * (x^2 + z^2) / 12
Izz = m * (x^2 + y^2) / 12
```

### 实心圆柱

质量为 `m`，半径为 `r`，圆柱长度为 `h`，轴线沿 Z 轴：

```text
Ixx = Iyy = m * (3*r^2 + h^2) / 12
Izz = m * r^2 / 2
```

### 实心球

质量为 `m`，半径为 `r`：

```text
Ixx = Iyy = Izz = 2 * m * r^2 / 5
```

如果形状旋转、质心偏移或由多个部件组合，应使用正确的坐标变换和平行轴定理计算，而不是直接套用中心公式。

## 9. Geometry 基础几何体

URDF 支持常见几何体。

### Box

```xml
<box size="1.0 0.5 0.2"/>
```

`size` 顺序为：

```text
X 长度 Y 宽度 Z 高度
```

### Sphere

```xml
<sphere radius="0.1"/>
```

### Cylinder

```xml
<cylinder radius="0.05" length="0.02"/>
```

圆柱默认轴线沿 Z 轴。

### Mesh

```xml
<mesh
    filename="package://robot_description/meshes/base.stl"
    scale="0.001 0.001 0.001"/>
```

尺寸默认使用米，角度默认使用弧度。

## 10. Mesh 网格模型

网格适合表达复杂外观。

常见格式：

| 格式 | 特点 |
| --- | --- |
| STL | 主要保存几何表面，不包含完整材质信息 |
| DAE | 可以保存颜色、纹理和场景信息 |

推荐使用功能包 URI：

```text
package://<package_name>/meshes/<file_name>
```

不要在仓库中写死：

```text
/home/user/workspace/src/.../model.stl
```

绝对路径换电脑或移动仓库后会失效。

### 网格单位

URDF 以米为单位，但建模软件可能导出毫米模型。

例如把毫米缩放为米：

```xml
<mesh filename="..." scale="0.001 0.001 0.001"/>
```

模型看不见时，可能不是路径错误，而是模型大到超出视野或小到几乎不可见。

### 网格坐标原点

网格文件自身包含顶点坐标。URDF 中的 `<origin>` 是在网格原有坐标基础上继续平移和旋转。

建模阶段应尽量统一：

- 单位。
- 坐标轴方向。
- 几何原点。
- 文件命名。

## 11. Material

可以在 Visual 内直接定义材质：

```xml
<material name="blue">
    <color rgba="0.1 0.4 0.8 1.0"/>
</material>
```

也可以在 `<robot>` 下统一定义并复用：

```xml
<material name="blue">
    <color rgba="0.1 0.4 0.8 1.0"/>
</material>

<link name="base_link">
    <visual>
        ...
        <material name="blue"/>
    </visual>
</link>
```

RGBA 分别表示红、绿、蓝和透明度，范围通常为 `0.0` 到 `1.0`。

颜色主要影响可视化效果，不代表碰撞或物理属性。

## 12. Origin

`<origin>` 常见于 Visual、Collision、Inertial 和 Joint。

```xml
<origin xyz="0.2 0.0 0.1" rpy="0.0 0.0 1.5708"/>
```

### `xyz`

```text
X Y Z 平移，单位为米
```

### `rpy`

```text
Roll Pitch Yaw，单位为弧度
```

同样的 `<origin>` 在不同位置含义不同：

| 所在位置 | 含义 |
| --- | --- |
| `visual/origin` | 视觉几何体相对于 Link 坐标系 |
| `collision/origin` | 碰撞几何体相对于 Link 坐标系 |
| `inertial/origin` | 质心和惯性坐标系相对于 Link 坐标系 |
| `joint/origin` | 子 Link 关节坐标系相对于父 Link |

不要把 Visual 偏移误当成 Link 本身的坐标关系。真正连接两个 Link 的变换由 Joint 决定。

## 13. Joint

Joint 连接父 Link 和子 Link：

```xml
<joint name="base_to_camera_joint" type="fixed">
    <parent link="base_link"/>
    <child link="camera_link"/>
    <origin xyz="0.2 0.0 0.075" rpy="0 0 0"/>
</joint>
```

关键元素：

| 元素 | 作用 |
| --- | --- |
| `name` | 关节唯一名称 |
| `type` | 关节类型 |
| `<parent>` | 父 Link |
| `<child>` | 子 Link |
| `<origin>` | 子关节坐标系相对于父 Link 的位姿 |
| `<axis>` | 运动轴 |
| `<limit>` | 位置、速度和力限制 |
| `<dynamics>` | 阻尼和摩擦 |
| `<mimic>` | 跟随另一个关节 |

## 14. Joint 类型

### Fixed

```xml
<joint name="camera_joint" type="fixed">
```

父子 Link 关系固定，适合传感器、外壳和焊接部件。

### Revolute

绕指定轴旋转，有上下限：

```xml
<joint name="arm_joint" type="revolute">
    <axis xyz="0 0 1"/>
    <limit lower="-1.57" upper="1.57" effort="20" velocity="1.0"/>
</joint>
```

### Continuous

绕指定轴无限旋转，没有位置上下限，常用于车轮：

```xml
<joint name="wheel_joint" type="continuous">
    <axis xyz="0 1 0"/>
    <limit effort="10" velocity="20"/>
</joint>
```

### Prismatic

沿指定轴直线移动，有位置范围：

```xml
<joint name="slider_joint" type="prismatic">
    <axis xyz="1 0 0"/>
    <limit lower="0.0" upper="0.5" effort="100" velocity="0.2"/>
</joint>
```

### Floating

允许 6 自由度运动。

### Planar

允许在平面内运动。

不同工具和控制系统对 `floating`、`planar` 的支持程度可能不同，移动机器人通常不会仅依赖一个 URDF 浮动关节表示底盘全局位姿，而是通过定位、里程计和 TF 发布动态关系。

## 15. Joint Axis

```xml
<axis xyz="0 1 0"/>
```

表示运动轴沿 Joint 坐标系的 Y 轴。

常见示例：

```text
0 0 1  绕 Z 轴旋转或沿 Z 轴移动
0 1 0  绕 Y 轴旋转或沿 Y 轴移动
1 0 0  绕 X 轴旋转或沿 X 轴移动
```

轴向在 Joint 坐标系中表达。如果 `joint/origin` 带旋转，轴在父 Link 中的实际方向也会随之改变。

## 16. Joint Limit

```xml
<limit
    lower="-1.57"
    upper="1.57"
    effort="20.0"
    velocity="1.0"/>
```

含义：

| 字段 | 作用 |
| --- | --- |
| `lower` | 最小位置，旋转关节单位为弧度，移动关节单位为米 |
| `upper` | 最大位置 |
| `effort` | 最大力或力矩 |
| `velocity` | 最大速度 |

`revolute` 和 `prismatic` 必须认真配置范围。`continuous` 没有位置上下限，但仿真和控制通常仍需要 `effort` 与 `velocity`。

## 17. Joint Dynamics

```xml
<dynamics damping="0.1" friction="0.05"/>
```

- `damping`：与速度相关的阻尼。
- `friction`：静态或库仑摩擦相关参数。

这些值对仿真稳定性和关节运动有影响，但具体表现还取决于仿真器和物理引擎。

## 18. Mimic Joint

某个关节跟随另一个关节：

```xml
<mimic joint="left_finger_joint" multiplier="-1.0" offset="0.0"/>
```

常用于平行夹爪等机械结构。

关系可以理解为：

```text
当前关节位置 = 目标关节位置 * multiplier + offset
```

实际控制支持取决于使用的状态发布器和控制框架，不能只添加 `<mimic>` 就假设控制器会自动处理所有联动逻辑。

## 19. URDF 必须是一棵树

合法机器人模型通常满足：

- 有且只有一个根 Link。
- 除根 Link 外，每个 Link 有一个父 Joint。
- Joint 的父 Link 和子 Link 都已定义。
- Link 与 Joint 名称唯一。
- 不形成闭环。

错误示例：四个 Link 被分别创建，但没有 Joint 连接。解析器会发现多个根 Link。

URDF 原生树结构不适合直接表达闭链机构。闭链机器人可能需要简化模型、额外约束或由仿真器扩展机制处理。

## 20. 根 Link

根 Link 是整棵机器人树的起点。

例如：

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

这里 `base_footprint` 是根 Link。

解析模型时可以通过 `check_urdf` 查看根 Link 和子树结构。

## 21. `base_footprint` 与 `base_link`

移动机器人中常见：

```text
base_footprint
└── base_link
```

### `base_footprint`

- 表示机器人在地面上的二维投影。
- 通常 Roll、Pitch 为 0。
- 常用于平面导航和机器人足迹计算。

### `base_link`

- 固定在机器人实体底盘上。
- 通常位于底盘几何中心或设计参考点。
- 可以相对地面存在高度。

示例固定关节：

```xml
<joint name="base_joint" type="fixed">
    <parent link="base_footprint"/>
    <child link="base_link"/>
    <origin xyz="0 0 0.05" rpy="0 0 0"/>
</joint>
```

`base_footprint` 可以没有明显实体外观，常使用极小几何体或不配置 Visual。

## 22. 机器人坐标约定

移动机器人常采用：

```text
X 轴向前
Y 轴向左
Z 轴向上
```

角度正方向遵循右手定则。

建模时应统一：

- 底盘朝向。
- 车轮轴方向。
- 传感器朝向。
- 网格模型导出坐标系。
- `base_link` 参考点。

如果视觉模型方向错误，先分清需要修改的是：

```text
visual/origin
joint/origin
joint/axis
网格文件自身坐标
```

不要通过反复试数值掩盖坐标定义问题。

## 23. 车轮建模

圆柱默认轴线沿 Z 轴，而轮式机器人车轮轴常沿 Y 轴。

可以旋转视觉圆柱：

```xml
<visual>
    <geometry>
        <cylinder radius="0.025" length="0.02"/>
    </geometry>
    <origin xyz="0 0 0" rpy="1.5708 0 0"/>
</visual>
```

并设置关节轴：

```xml
<axis xyz="0 1 0"/>
```

注意两者职责不同：

- `visual/origin` 只调整显示几何体。
- `joint/axis` 决定关节实际运动方向。

## 24. `robot_description`

ROS 2 通常把完整 URDF XML 文本放入节点参数：

```text
robot_description
```

`robot_state_publisher` 读取该参数并建立机器人运动学树。

检查参数：

```bash
ros2 param get /robot_state_publisher robot_description
```

如果参数为空、XML 不合法或模型树有问题，机器人状态发布器可能无法正常工作。

## 25. `robot_state_publisher`

主要职责：

- 解析 `robot_description`。
- 发布固定关节 TF。
- 订阅 `/joint_states`。
- 根据活动关节位置计算并发布动态 TF。

概念流程：

```text
固定关节 -> /tf_static
活动关节 + /joint_states -> /tf
```

`robot_state_publisher` 不负责计算机器人动力学，也不会自动控制真实关节。

## 26. `joint_state_publisher`

主要职责是根据 URDF 中的可运动关节发布：

```text
/joint_states
sensor_msgs/msg/JointState
```

消息包含：

```text
关节名称
位置
速度
力或力矩
```

普通版本可以发布默认或配置的关节状态；GUI 版本提供滑块用于手动调节。

```bash
ros2 run joint_state_publisher_gui joint_state_publisher_gui
```

不要同时运行多个 Joint State 发布器向同一组关节发布互相冲突的数据。

Joint State Publisher 是模型展示和测试工具，不等于真实机器人驱动或 `ros2_control` 控制器。

## 27. RViz 显示

显示 URDF 常见步骤：

1. 将 URDF/Xacro 加载为 `robot_description`。
2. 启动 `robot_state_publisher`。
3. 对活动关节启动 Joint State Publisher。
4. 启动 RViz2。
5. 添加或启用 `RobotModel` 显示项。
6. 设置正确的 Fixed Frame。

关键配置：

```text
RobotModel Description Topic: /robot_description
Fixed Frame: 模型中存在且 TF 可达的坐标系
```

RViz 能显示模型，只能说明视觉资源和 TF 基本可用，不代表碰撞、惯性和控制配置正确。

## 28. 使用 Launch 加载模型

典型 Python Launch：

```python
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    model_arg = DeclareLaunchArgument(
        'model',
        default_value='/absolute/or/substituted/path/robot.urdf.xacro'
    )

    robot_description = ParameterValue(
        Command(['xacro ', LaunchConfiguration('model')]),
        value_type=str
    )

    state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description}]
    )

    return LaunchDescription([
        model_arg,
        state_publisher
    ])
```

`Command` 在启动时运行 Xacro，`ParameterValue` 明确把输出作为字符串参数。

## 29. 指定模型路径

推荐通过功能包共享目录获取路径：

```bash
ros2 launch learning_urdf_cpp display.launch.py \
  model:=$(ros2 pkg prefix --share learning_urdf_cpp)/urdf/urdf/joint.urdf
```

必须保持：

```text
model:=<完整路径>
```

错误写法：

```text
model:=<前半段路径> /后半段路径
```

空格会让 Launch 把后半段识别为额外参数。

## 30. Xacro 是什么

Xacro 是 XML Macros 的缩写，在 URDF XML 基础上提供：

- 属性。
- 数学表达式。
- 参数。
- 宏。
- 条件。
- 文件包含。

它用于减少重复代码并把复杂机器人拆成多个模块。

Xacro 最终会被展开为普通 URDF，真正被 `robot_state_publisher` 解析的仍是展开后的 XML。

## 31. Xacro 根元素

```xml
<?xml version="1.0"?>
<robot
    name="my_robot"
    xmlns:xacro="http://wiki.ros.org/xacro">
    ...
</robot>
```

`xmlns:xacro` 声明 Xacro 命名空间。

## 32. Xacro 属性

定义属性：

```xml
<xacro:property name="base_length" value="0.20"/>
<xacro:property name="base_width" value="0.12"/>
<xacro:property name="base_height" value="0.07"/>
```

使用属性：

```xml
<box size="${base_length} ${base_width} ${base_height}"/>
```

好处：

- 尺寸集中管理。
- 修改一个值即可影响多个位置。
- 减少魔法数字。
- 表达部件之间的尺寸关系。

## 33. Xacro 表达式

`${...}` 中可以执行数学计算：

```xml
<xacro:property name="PI" value="3.1415927"/>

<origin
    xyz="${base_length / 2} 0 ${base_height / 2}"
    rpy="${PI / 2} 0 0"/>
```

表达式适合计算：

- 车轮位置。
- 传感器安装高度。
- 对称部件坐标。
- 由总尺寸推导的偏移。

## 34. Xacro 参数

声明外部参数：

```xml
<xacro:arg name="use_lidar" default="true"/>
```

读取参数：

```text
$(arg use_lidar)
```

命令行传入：

```bash
xacro robot.urdf.xacro use_lidar:=false
```

需要区分：

```text
${expression}   Xacro 属性和表达式
$(arg name)     Xacro 外部参数
```

## 35. Xacro 宏

定义车轮宏：

```xml
<xacro:macro name="wheel" params="wheel_name x_sign y_sign">
    <link name="${wheel_name}_wheel_link">
        ...
    </link>

    <joint name="${wheel_name}_wheel_joint" type="continuous">
        ...
    </joint>
</xacro:macro>
```

调用：

```xml
<xacro:wheel wheel_name="front_left" x_sign="1" y_sign="1"/>
<xacro:wheel wheel_name="front_right" x_sign="1" y_sign="-1"/>
<xacro:wheel wheel_name="rear_left" x_sign="-1" y_sign="1"/>
<xacro:wheel wheel_name="rear_right" x_sign="-1" y_sign="-1"/>
```

宏不仅减少代码，还可以通过参数保证命名和结构一致。

每次展开生成的 Link 和 Joint 名称必须唯一。

## 36. Xacro 文件包含

```xml
<xacro:include filename="robot_base.urdf.xacro"/>
<xacro:include filename="robot_camera.urdf.xacro"/>
<xacro:include filename="robot_lidar.urdf.xacro"/>
```

推荐按职责拆分：

```text
robot.urdf.xacro          最终入口
robot_base.urdf.xacro     底盘和车轮
robot_sensors.urdf.xacro  传感器
robot_control.xacro       控制配置
robot_gazebo.xacro        仿真扩展
```

相对包含路径通常相对于当前 Xacro 文件位置解析，移动文件后应同步检查包含路径。

包含顺序可能影响属性和宏是否已经定义。

## 37. Xacro 条件

```xml
<xacro:if value="$(arg use_lidar)">
    <!-- 雷达 Link 与 Joint -->
</xacro:if>
```

```xml
<xacro:unless value="$(arg use_lidar)">
    <!-- 不使用雷达时的内容 -->
</xacro:unless>
```

条件可以让同一套模型适配不同机器人配置，例如：

- 是否安装相机。
- 是否安装雷达。
- 仿真与真实硬件差异。
- 不同底盘尺寸。

条件过多会让模型难以理解。产品差异很大时，应考虑拆分清晰的顶层入口。

## 38. Xacro 宏参数设计

宏参数应表达真正变化的部分。

车轮宏可能接收：

```text
名称
父 Link
安装位置
左右符号
前后符号
半径
宽度
```

不要把所有常量都变成参数，否则调用处会变得复杂。公共尺寸适合使用属性，实例差异适合使用宏参数。

## 39. 展开 Xacro

在终端查看展开结果：

```bash
xacro robot.urdf.xacro
```

保存为普通 URDF：

```bash
xacro robot.urdf.xacro > /tmp/robot.urdf
```

带参数展开：

```bash
xacro robot.urdf.xacro use_lidar:=true > /tmp/robot.urdf
```

Xacro 报错时，先单独运行展开命令，比直接从复杂 Launch 日志中定位更容易。

## 40. 使用 `check_urdf`

```bash
check_urdf robot.urdf
```

对于 Xacro：

```bash
xacro robot.urdf.xacro > /tmp/robot.urdf
check_urdf /tmp/robot.urdf
```

它可以检查：

- XML 是否可解析。
- Link 和 Joint 引用是否存在。
- 根 Link。
- 机器人树结构。
- 部分关节配置问题。

成功解析不代表碰撞和惯性参数一定合理，还需要仿真和工程检查。

## 41. 生成结构图

如果安装了 URDF 工具，可以使用：

```bash
urdf_to_graphiz robot.urdf
```

它会根据模型生成 Link 和 Joint 关系图，适合检查复杂模型结构。

对于 Xacro，先展开为 URDF 再生成图。

## 42. 功能包目录组织

推荐：

```text
robot_description/
├── launch/
│   └── display.launch.py
├── meshes/
│   ├── visual/
│   └── collision/
├── rviz/
│   └── display.rviz
├── urdf/
│   ├── robot.urdf.xacro
│   ├── robot_base.xacro
│   └── robot_sensors.xacro
├── CMakeLists.txt
├── package.xml
└── README.md
```

复杂项目可以按部件继续拆分，但顶层入口应明确。

## 43. 安装模型资源

`ament_cmake`：

```cmake
install(
  DIRECTORY launch urdf meshes rviz
  DESTINATION share/${PROJECT_NAME}
)
```

构建后资源位于：

```text
install/<package>/share/<package>/
```

查询共享目录：

```bash
ros2 pkg prefix --share <package_name>
```

新增或修改模型后重新构建：

```bash
colcon build --packages-select <package_name>
source install/setup.bash
```

如果源码已修改但 RViz 仍显示旧模型，通常是因为 Launch 正在读取 `install/` 中的旧副本。

## 44. `package.xml` 常见运行依赖

机器人描述显示包常见：

```xml
<exec_depend>xacro</exec_depend>
<exec_depend>robot_state_publisher</exec_depend>
<exec_depend>joint_state_publisher</exec_depend>
<exec_depend>joint_state_publisher_gui</exec_depend>
<exec_depend>rviz2</exec_depend>
<exec_depend>ros2launch</exec_depend>
```

应根据 Launch 和模型真正使用的工具声明依赖。

## 45. 从 RViz 模型到仿真模型

一个能在 RViz 显示的模型，至少说明：

- XML/Xacro 基本可解析。
- 视觉资源路径可用。
- Link 和 Joint 树基本成立。
- TF 能够建立。

但仿真通常还需要：

```text
collision
inertial
合理的 joint limit 和 dynamics
接触和摩擦参数
Gazebo 或其他仿真器扩展
传感器插件
transmission
ros2_control 配置
控制器参数
```

不要把“RViz 看起来正常”当成“物理模型正确”。

## 46. Transmission 与 `ros2_control`

URDF 可以包含与传动和控制相关的扩展配置。

概念关系：

```text
URDF Joint
    │
    ├── transmission
    │
    └── ros2_control hardware interface
            │
            ▼
      controller_manager
            │
            ▼
         控制器
```

`joint_state_publisher` 只用于提供关节状态示例；真实机器人和仿真控制通常由硬件接口与控制器发布关节状态并接收控制命令。

控制部分应在掌握 URDF 结构后单独学习，不能只靠 Joint 类型自动获得运动能力。

## 47. Gazebo 扩展

仿真器通常需要额外标签，例如：

- 材质。
- 摩擦系数。
- 传感器插件。
- 执行器插件。
- 接触参数。
- 控制接口。

这些内容不是基础 URDF 树的全部组成部分，常放在单独 Xacro 文件中，再由顶层模型包含。

这样可以保持：

```text
机器人几何结构
仿真专用配置
真实硬件控制配置
```

之间的职责清晰。

## 48. 常见问题

### XML 语法错误

常见原因：

- 标签没有闭合。
- 属性引号缺失。
- 元素嵌套位置错误。
- Xacro 命名空间遗漏。

先执行：

```bash
xacro robot.urdf.xacro > /tmp/robot.urdf
check_urdf /tmp/robot.urdf
```

### 出现多个根 Link

说明存在没有通过 Joint 连接的 Link 子树。

检查：

- 是否漏写 Joint。
- Joint 的父子 Link 名称是否拼错。
- 宏是否只生成了 Link，没有生成连接关节。
- 条件展开后是否遗漏关键连接。

### Link 或 Joint 重名

每个名称必须唯一。Xacro 宏应通过参数生成不同名称，例如：

```text
front_left_wheel_link
front_right_wheel_link
```

### RViz 中模型不显示

检查：

1. `robot_state_publisher` 是否运行。
2. `robot_description` 是否有内容。
3. RViz RobotModel 是否启用。
4. Description Topic 是否正确。
5. Fixed Frame 是否存在。
6. TF 树是否连通。
7. Visual 是否定义了 Geometry。

### 模型显示在奇怪位置

检查：

- Joint Origin。
- Visual Origin。
- 网格自身原点。
- RViz Fixed Frame。
- 根 Link 设计。

先判断是 Link 坐标错了，还是仅视觉几何体偏了。

### 模型方向不正确

检查：

- `rpy` 使用的是弧度。
- 网格导出轴向。
- 圆柱默认轴线。
- Joint Axis。
- 是否把 Roll、Pitch、Yaw 顺序写错。

### 网格显示过大或过小

检查模型原始单位并设置：

```xml
scale="0.001 0.001 0.001"
```

不要通过修改相机视角掩盖错误单位。

### 找不到 Mesh

检查：

- 是否使用 `package://` URI。
- 文件名大小写是否一致。
- Mesh 是否被安装到共享目录。
- 是否重新构建并刷新环境。
- 文件路径中是否包含错误层级。

### 活动关节不动

检查：

- 是否有 `/joint_states`。
- Joint 名称是否匹配。
- Joint 类型是否可运动。
- Joint State Publisher 或真实驱动是否运行。
- 关节位置是否在限制范围内。

### 仿真模型抖动或飞走

检查：

- 质量是否为正数且合理。
- 惯性张量是否合理。
- 碰撞体是否互相严重穿透。
- Joint Limit 和 Dynamics 是否合理。
- 模型初始位置是否与地面冲突。
- 控制器增益是否过大。
- 网格碰撞体是否过于复杂。

### Xacro 属性未定义

检查：

- 属性名称拼写。
- 属性定义是否在使用之前可见。
- 包含顺序。
- 属性是 `${...}` 还是外部参数 `$(arg ...)`。

### Launch 参数路径格式错误

正确：

```bash
model:=$(ros2 pkg prefix --share package_name)/urdf/robot.urdf.xacro
```

`model:=` 后必须是一个完整参数值。

### 修改模型后没有变化

重新执行：

```bash
colcon build --packages-select <package_name>
source install/setup.bash
```

然后确认 Launch 实际加载的路径。

## 49. 建模工作流建议

### 第一步：建立坐标规范

明确：

- `base_link` 在哪里。
- X、Y、Z 朝向。
- 单位。
- 根 Link。
- 传感器命名。

### 第二步：从简单几何体开始

先使用 Box、Cylinder、Sphere 建立 Link 与 Joint 树，确认 TF 和尺寸关系正确。

### 第三步：检查树结构

```bash
xacro robot.urdf.xacro > /tmp/robot.urdf
check_urdf /tmp/robot.urdf
```

### 第四步：在 RViz 中检查

关注：

- 部件位置。
- 坐标轴方向。
- Joint 运动方向。
- Fixed Frame。
- TF 树。

### 第五步：替换视觉网格

保持 Link 坐标和 Joint 关系不变，再逐步引入 Mesh。

### 第六步：添加碰撞和惯性

使用简化碰撞体与经过计算的质量、惯性参数。

### 第七步：加入仿真与控制

添加仿真扩展、传感器插件、`ros2_control` 和控制器配置。

### 第八步：验证真实行为

不要只检查外观，还要验证：

- 接触稳定性。
- 关节方向。
- 速度与力限制。
- 传感器坐标系。
- 控制器响应。

## 50. 工程设计建议

- Link 和 Joint 使用小写蛇形命名。
- Link 名称使用 `_link` 后缀，Joint 使用 `_joint` 后缀。
- 公共尺寸定义为 Xacro 属性。
- 重复结构使用宏。
- 大模型按底盘、传感器、执行器、控制和仿真拆分。
- 最终只保留少量清晰的顶层入口。
- Mesh 使用 `package://` URI。
- Visual 与 Collision 分别设计。
- 惯性参数通过计算或 CAD 数据获得。
- 每次改动先展开 Xacro，再检查 URDF 树。
- 为不同型号提供参数，而不是复制大量几乎相同的文件。
- 在 README 中记录模型入口、坐标约定和启动命令。

## 51. 学习仓库中的对应示例

`learning_urdf_cpp` 是一个 `ament_cmake` 机器人描述资源包，没有自定义 C++ 节点。

### URDF 示例

| 文件 | 重点 |
| --- | --- |
| `box_robot.urdf` | 单 Link Box |
| `box_robot_copy.urdf` | 尺寸修改与加载练习 |
| `link.urdf` | 几何体、材质、Origin 和 STL Mesh |
| `joint.urdf` | 连续关节、父子关系和 Axis |
| `base_footprint.urdf` | `base_footprint -> base_link -> camera_link` |
| `four_wheel_robot.urdf` | 普通 URDF 四轮底盘 |

### Xacro 示例

| 文件 | 重点 |
| --- | --- |
| `wheel_macro_demo.urdf.xacro` | 属性和车轮宏 |
| `four_wheel_robot_base.urdf.xacro` | 参数化底盘和四轮宏 |
| `four_wheel_robot_camera.urdf.xacro` | 相机模块 |
| `four_wheel_robot_lidar.urdf.xacro` | 雷达模块 |
| `four_wheel_robot.urdf.xacro` | 最终组合入口 |

最终模型树：

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

## 52. 仓库模型运行命令

### 默认盒状机器人

```bash
source install/setup.bash
ros2 launch learning_urdf_cpp display.launch.py
```

### Joint 示例

```bash
ros2 launch learning_urdf_cpp display.launch.py \
  model:=$(ros2 pkg prefix --share learning_urdf_cpp)/urdf/urdf/joint.urdf
```

### 普通 URDF 四轮机器人

```bash
ros2 launch learning_urdf_cpp display.launch.py \
  model:=$(ros2 pkg prefix --share learning_urdf_cpp)/urdf/urdf/four_wheel_robot.urdf
```

### 完整 Xacro 四轮传感器机器人

```bash
ros2 launch learning_urdf_cpp display.launch.py \
  model:=$(ros2 pkg prefix --share learning_urdf_cpp)/urdf/xacro/four_wheel_robot.urdf.xacro
```

### 检查最终模型

```bash
xacro \
  $(ros2 pkg prefix --share learning_urdf_cpp)/urdf/xacro/four_wheel_robot.urdf.xacro \
  > /tmp/four_wheel_robot.urdf

check_urdf /tmp/four_wheel_robot.urdf
```

## 53. 复习速查表

### 必须记住的核心元素

```text
robot      机器人根元素
link       刚体部件
joint      Link 之间的连接
visual     显示外观
collision  碰撞形状
inertial   质量、质心和惯性
origin     相对位置与姿态
axis       关节运动轴
limit      关节范围、速度和力限制
```

### 必须分清

```text
visual/origin    几何外观相对 Link
collision/origin 碰撞体相对 Link
inertial/origin  质心和惯性坐标系相对 Link
joint/origin     子关节坐标系相对父 Link

RViz 可显示       不等于仿真物理正确
joint_state_publisher 不等于真实控制器
URDF 描述结构      TF2 提供运行时坐标关系
```

### Xacro 必须记住

```text
${...}                 属性和表达式
$(arg name)            外部参数
xacro:property         定义属性
xacro:macro            定义宏
xacro:include          包含文件
xacro:if / unless      条件展开
```

### 标准检查顺序

```text
1. xacro 展开为 URDF
2. check_urdf 检查树结构
3. 确认只有一个根 Link
4. 检查 Link 和 Joint 名称
5. 检查 Joint Origin 与 Axis
6. 启动 robot_state_publisher
7. 检查 robot_description 和 /joint_states
8. 在 RViz 中检查 RobotModel 和 TF
9. 仿真前检查 Collision、Mass 和 Inertia
```

### 一句话总结

```text
URDF 描述机器人由哪些刚体和关节组成，Xacro让这份描述可参数化、可复用、可拆分，而状态发布器把模型和关节状态转换成运行时 TF。
```
