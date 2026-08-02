# ROS 2 TF2 C++ 学习示例

## 功能包说明

`learning_tf_cpp` 用于学习 ROS 2 中的 TF2 坐标变换机制，涵盖静态坐标系广播、动态坐标系广播、坐标系监听、带坐标系点的发布，以及基于消息过滤器的坐标点变换。

功能包提供 5 个 C++ 节点，可以组合为三组练习：

1. 发布并监听静态坐标关系。
2. 根据 `turtlesim` 位姿发布动态坐标关系。
3. 将 `laser` 坐标系中的点变换到 `base_link` 坐标系。

## 环境要求

| 项目 | 要求 |
| --- | --- |
| 操作系统 | Ubuntu 22.04 |
| ROS 2 | Humble Hawksbill |
| 构建类型 | `ament_cmake` |
| C++ 标准 | C++17 |
| TF 核心库 | `tf2`、`tf2_ros` |
| 几何消息支持 | `geometry_msgs`、`tf2_geometry_msgs` |
| 消息同步 | `message_filters` |
| 动态广播示例 | `turtlesim` |

如果缺少 `turtlesim`，可以安装：

```bash
sudo apt install ros-humble-turtlesim
```

## 目录结构

```text
learning_tf_cpp/
├── src/
│   ├── dynamic_tf_broadcaster.cpp
│   ├── point_publisher.cpp
│   ├── point_transformer.cpp
│   ├── static_tf_broadcaster.cpp
│   └── tf_listener.cpp
├── CMakeLists.txt
├── package.xml
└── README.md
```

## 节点总览

| 可执行程序 | 节点名称 | 主要功能 |
| --- | --- | --- |
| `static_tf_broadcaster` | `static_tf_broadcaster_cpp` | 根据命令行参数发布静态 TF |
| `dynamic_tf_broadcaster` | `dynamic_tf_broadcaster_cpp` | 根据小乌龟实时位姿发布动态 TF |
| `tf_listener` | `tf_listener_cpp` | 查询 `laser` 到 `camera` 的坐标变换 |
| `point_publisher` | `point_publisher_cpp` | 发布 `laser` 坐标系中的动态点 |
| `point_transformer` | `point_transformer_cpp` | 将点从 `laser` 变换到 `base_link` |

## TF2 基础概念

### 坐标系树

TF2 将多个坐标系组织成一棵树。每个非根坐标系只能有一个直接父坐标系，例如：

```text
world
└── base_link
    └── laser
```

TF2 可以沿树中的路径组合多段变换，因此只要两个坐标系位于同一棵树中，就可以查询它们之间的关系。

### 父坐标系与子坐标系

`geometry_msgs/msg/TransformStamped` 中两个关键字段为：

```cpp
transform.header.frame_id = "父坐标系";
transform.child_frame_id = "子坐标系";
```

`transform.transform` 描述子坐标系原点和姿态相对于父坐标系的位置。

坐标系名称应在同一 TF 树中保持唯一，并尽量使用能够表达机器人结构的名称。通常不在 frame ID 前添加 `/`。

### 静态变换与动态变换

| 类型 | 发布工具 | ROS 2 话题 | 适用对象 |
| --- | --- | --- | --- |
| 静态变换 | `StaticTransformBroadcaster` | `/tf_static` | 安装后相对位置固定的传感器或部件 |
| 动态变换 | `TransformBroadcaster` | `/tf` | 随时间运动的机器人、关节或目标 |

静态 TF 只需发布一次，TF2 会以适合静态数据的方式保存和传递；动态 TF 需要随位姿变化持续更新。

## 构建

在工作空间根目录执行：

```bash
source /opt/ros/humble/setup.bash
colcon build --packages-select learning_tf_cpp
source install/setup.bash
```

`CMakeLists.txt` 会编译并安装 5 个可执行程序，同时配置以下主要依赖：

- `rclcpp`
- `tf2`
- `tf2_ros`
- `geometry_msgs`
- `turtlesim`
- `tf2_geometry_msgs`
- `message_filters`

修改源码后，需要重新构建并刷新 `install/setup.bash`。

## 静态坐标系广播

### 命令格式

`static_tf_broadcaster` 接收 8 个参数：

```text
x y z roll pitch yaw parent_frame child_frame
```

运行格式：

```bash
ros2 run learning_tf_cpp static_tf_broadcaster \
  <x> <y> <z> <roll> <pitch> <yaw> <parent_frame> <child_frame>
```

其中：

| 参数 | 含义 |
| --- | --- |
| `x y z` | 子坐标系原点在父坐标系中的平移位置，单位为米 |
| `roll` | 绕 X 轴旋转，单位为弧度 |
| `pitch` | 绕 Y 轴旋转，单位为弧度 |
| `yaw` | 绕 Z 轴旋转，单位为弧度 |
| `parent_frame` | 父坐标系名称 |
| `child_frame` | 子坐标系名称 |

代码通过 `tf2::Quaternion::setRPY()` 将欧拉角转换为四元数，再使用 `StaticTransformBroadcaster::sendTransform()` 发布。

### 基础示例

发布 `base_link -> laser` 的静态关系：

```bash
source install/setup.bash
ros2 run learning_tf_cpp static_tf_broadcaster \
  0.4 0 0.2 0 0 0 base_link laser
```

该命令表示：

- `laser` 是 `base_link` 的子坐标系。
- `laser` 原点位于 `base_link` 的 `(0.4, 0.0, 0.2)`。
- 两个坐标系方向相同，没有相对旋转。

节点会持续运行，以便后启动的监听器也能获得静态变换。按 `Ctrl+C` 结束。

### 查看静态变换

在新终端执行：

```bash
source /opt/ros/humble/setup.bash
ros2 run tf2_ros tf2_echo base_link laser
```

还可以检查静态 TF 话题：

```bash
ros2 topic echo /tf_static
```

## 动态坐标系广播

`dynamic_tf_broadcaster` 订阅：

```text
话题：/turtle1/pose
类型：turtlesim/msg/Pose
```

每次收到位姿后，它都会发布：

```text
world -> turtle1
```

对应关系为：

```text
translation.x = pose.x
translation.y = pose.y
translation.z = 0.0
yaw = pose.theta
```

由于四元数不能直接使用平面朝向角，代码先通过 `setRPY(0.0, 0.0, pose.theta)` 将 `theta` 转换为四元数。

### 完整运行流程

终端 1，启动小乌龟：

```bash
ros2 run turtlesim turtlesim_node
```

终端 2，启动键盘控制：

```bash
ros2 run turtlesim turtle_teleop_key
```

终端 3，启动动态广播：

```bash
source install/setup.bash
ros2 run learning_tf_cpp dynamic_tf_broadcaster
```

终端 4，查看动态变换：

```bash
ros2 run tf2_ros tf2_echo world turtle1
```

移动小乌龟时，平移和旋转数据应持续变化。

## 坐标系监听

`tf_listener` 创建以下对象：

- `tf2_ros::Buffer`：缓存 TF 数据并提供查询接口。
- `tf2_ros::TransformListener`：订阅 `/tf` 和 `/tf_static`，将变换写入 Buffer。
- 1 秒定时器：周期查询坐标关系并输出日志。

查询代码为：

```cpp
buffer_->lookupTransform("camera", "laser", tf2::TimePointZero);
```

参数含义如下：

```text
target_frame = camera
source_frame = laser
time         = 最新可用变换
```

它用于获得把 `laser` 坐标系中的数据转换到 `camera` 坐标系所需的变换。

### 监听测试

终端 1，发布 `camera -> laser`：

```bash
source install/setup.bash
ros2 run learning_tf_cpp static_tf_broadcaster \
  0.3 0.1 0.2 0 0 0 camera laser
```

终端 2，启动监听节点：

```bash
source install/setup.bash
ros2 run learning_tf_cpp tf_listener
```

正常情况下，节点每秒输出一次 `camera` 与 `laser` 之间的平移关系。

如果目标坐标系或源坐标系尚未出现在 Buffer 中，节点会捕获 `tf2::LookupException` 并打印警告。当前回调只显式捕获该异常，因此测试时还应保证两个已有坐标系位于同一棵 TF 树中。

## 坐标点发布与变换

这组示例演示 TF2 不仅可以查询坐标关系，还能把带坐标系和时间戳的实际几何数据转换到目标坐标系。

### 1. 发布坐标点

`point_publisher` 每 0.1 秒向相对话题 `point` 发布一条 `geometry_msgs/msg/PointStamped`：

```text
frame_id = laser
x        = 0.0 开始，每次增加 0.05
y        = 0.0
z        = -0.5
```

启动命令：

```bash
source install/setup.bash
ros2 run learning_tf_cpp point_publisher
```

查看消息：

```bash
ros2 topic echo /point
```

### 2. 等待可用变换

`point_transformer` 使用以下组件：

- `message_filters::Subscriber<PointStamped>` 订阅 `/point`。
- `tf2_ros::Buffer` 缓存坐标变换。
- `tf2_ros::TransformListener` 接收 TF。
- `tf2_ros::MessageFilter<PointStamped>` 等待消息时间戳对应的变换可用。
- `tf2_ros::CreateTimerROS` 为 Buffer 提供 ROS 2 定时器接口。

消息过滤器的目标坐标系为 `base_link`，队列长度为 10，等待超时为 1 秒。只有点消息能够变换到 `base_link` 时，才会触发变换回调。

### 3. 执行坐标变换

回调中调用：

```cpp
out_point = buffer_->transform(*msg, "base_link");
```

输入点的 `frame_id` 为 `laser`，因此最终执行的是：

```text
laser 坐标系中的点 -> base_link 坐标系中的点
```

`tf2_geometry_msgs` 为 `PointStamped` 提供了 TF2 所需的类型转换支持。

### 4. 完整测试流程

终端 1，发布静态变换：

```bash
source install/setup.bash
ros2 run learning_tf_cpp static_tf_broadcaster \
  0.4 0 0.2 0 0 0 base_link laser
```

终端 2，发布 `laser` 坐标系中的点：

```bash
source install/setup.bash
ros2 run learning_tf_cpp point_publisher
```

终端 3，启动坐标点变换节点：

```bash
source install/setup.bash
ros2 run learning_tf_cpp point_transformer
```

第一个输入点为：

```text
laser: (0.00, 0.00, -0.50)
```

由于 `laser` 相对于 `base_link` 平移 `(0.4, 0.0, 0.2)` 且没有旋转，预期第一个输出点为：

```text
base_link: (0.40, 0.00, -0.30)
```

后续输入点的 X 每次增加 `0.05`，因此输出 X 应依次为 `0.45`、`0.50`、`0.55` 等；Y 保持 `0.00`，Z 保持 `-0.30`。

## TF 树检查

查看当前系统中的 TF 话题：

```bash
ros2 topic list | grep tf
```

预期通常包含：

```text
/tf
/tf_static
```

查看指定坐标系关系：

```bash
ros2 run tf2_ros tf2_echo base_link laser
```

如果安装了 `tf2_tools`，还可以生成 TF 树报告：

```bash
ros2 run tf2_tools view_frames
```

命令会在当前目录生成用于观察坐标系连接关系的文件。

## 常见问题

### 找不到功能包或可执行程序

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
```

如果刚修改源码，应重新构建后再刷新工作空间环境。

### 静态广播提示参数数量不合法

节点必须接收 8 个参数：

```text
x y z roll pitch yaw parent_frame child_frame
```

缺少或多出任意参数都会直接退出。

当前示例使用 `atof()` 转换数值参数。无法解析的字符串会得到 `0.0`，所以运行前应自行确认平移量和欧拉角均为有效数字。

### 旋转结果与预期不一致

`roll`、`pitch` 和 `yaw` 使用弧度，不是角度。例如 90 度应换算为约 `1.5708` 弧度。

### 监听器持续提示坐标变换不存在

检查以下事项：

- 广播节点是否正在运行。
- 坐标系名称是否完全一致，包括大小写。
- 两个坐标系是否位于同一棵 TF 树中。
- `header.frame_id` 和 `child_frame_id` 是否写反。
- 同一个子坐标系是否被多个节点设置了不同父坐标系。

### `point_transformer` 没有输出

依次确认：

```bash
ros2 topic echo /point
ros2 run tf2_ros tf2_echo base_link laser
```

点消息必须带有 `laser` 的 `frame_id`，并且 TF 树中必须存在从 `laser` 到 `base_link` 的有效变换。消息过滤器在条件不满足时不会调用变换回调。

### 坐标变换方向与预期相反

需要区分两个问题：

```text
广播：子坐标系相对于父坐标系是什么位置？
变换：源坐标系中的数据要转换到哪个目标坐标系？
```

`lookupTransform(target, source, time)` 和 `transform(data, target)` 都把数据从源坐标系表达转换为目标坐标系表达。

### TF 数据冲突或跳变

一个子坐标系在同一 TF 树中只能有一个父坐标系。不要同时运行多个广播节点，以不同变换发布相同的 `child_frame_id`。

## 学习要点

- TF2 坐标系树、父子关系和坐标变换方向。
- `/tf` 与 `/tf_static` 的用途和区别。
- `TransformStamped` 中时间戳、父坐标系、子坐标系、平移与旋转字段。
- 使用 `tf2::Quaternion` 将 RPY 欧拉角转换为四元数。
- `StaticTransformBroadcaster` 与 `TransformBroadcaster` 的使用场景。
- `Buffer`、`TransformListener` 与 `lookupTransform()` 的职责。
- `tf2::TimePointZero` 表示查询最新可用变换。
- 使用 `PointStamped` 携带坐标系和时间信息。
- `tf2_geometry_msgs` 对几何消息变换的支持。
- `message_filters` 与 `tf2_ros::MessageFilter` 对消息和 TF 可用性的协调。
- 使用 `tf2_echo`、TF 话题和 TF 树工具排查坐标关系。
