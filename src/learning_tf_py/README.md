# ROS 2 TF2 Python 学习示例

## 功能包说明

`learning_tf_py` 用于学习 ROS 2 中 TF2 坐标变换机制的 Python 实现，涵盖静态坐标系广播、动态坐标系广播、坐标系监听和带坐标系点的发布。

功能包提供 4 个 Python 节点，可以组合为以下练习：

1. 根据命令行参数发布静态坐标关系。
2. 根据 `turtlesim` 实时位姿发布动态坐标关系。
3. 监听并查询 `laser` 与 `camera` 之间的坐标变换。
4. 发布带时间戳和来源坐标系的 `PointStamped` 消息。

当前功能包没有 Python 版坐标点变换节点。Python 发布的点可以由 `learning_tf_cpp` 中的 `point_transformer` 处理，用于验证 ROS 2 节点的跨语言通信能力。

## 环境要求

| 项目 | 要求 |
| --- | --- |
| 操作系统 | Ubuntu 22.04 |
| ROS 2 | Humble Hawksbill |
| 构建类型 | `ament_python` |
| Python 构建工具 | `setuptools` |
| ROS 2 客户端库 | `rclpy` |
| TF 广播与监听 | `tf2_ros` |
| 欧拉角转换 | `tf_transformations` |
| 几何消息 | `geometry_msgs` |
| 动态广播示例 | `turtlesim` |

如果缺少示例依赖，可以安装：

```bash
sudo apt install ros-humble-turtlesim ros-humble-tf-transformations
```

## 目录结构

```text
learning_tf_py/
├── learning_tf_py/
│   ├── __init__.py
│   ├── dynamic_tf_broadcaster.py
│   ├── point_publisher.py
│   ├── static_tf_broadcaster.py
│   └── tf_listener.py
├── resource/
│   └── learning_tf_py
├── test/
│   ├── test_copyright.py
│   ├── test_flake8.py
│   └── test_pep257.py
├── package.xml
├── setup.cfg
├── setup.py
└── README.md
```

## 节点总览

| 控制台脚本 | 节点名称 | 主要功能 |
| --- | --- | --- |
| `static_tf_broadcaster` | `static_tf_broadcaster_py` | 根据命令行参数发布静态 TF |
| `dynamic_tf_broadcaster` | `dynamic_tf_broadcaster_py` | 根据小乌龟实时位姿发布动态 TF |
| `tf_listener` | `tf_listener_py` | 查询 `laser` 到 `camera` 的坐标变换 |
| `point_publisher` | `point_publisher_py` | 发布 `laser` 坐标系中的动态点 |

`setup.py` 通过 `console_scripts` 将 4 个 `main()` 函数注册为可由 `ros2 run` 启动的程序。

## TF2 基础概念

### 坐标系树

TF2 将多个坐标系组织成一棵树。例如，机器人底盘和激光雷达可以表示为：

```text
world
└── base_link
    └── laser
```

每个非根坐标系只能有一个直接父坐标系。只要两个坐标系位于同一棵树中，TF2 就可以沿路径组合变换并查询它们之间的关系。

### 父坐标系与子坐标系

`geometry_msgs/msg/TransformStamped` 中两个关键字段为：

```python
transform.header.frame_id = '父坐标系'
transform.child_frame_id = '子坐标系'
```

`transform.transform` 描述子坐标系原点和姿态相对于父坐标系的位置。

坐标系名称应在同一 TF 树中保持唯一，并尽量体现机器人结构。通常不在 frame ID 前添加 `/`。

### 静态变换与动态变换

| 类型 | Python 类 | ROS 2 话题 | 适用对象 |
| --- | --- | --- | --- |
| 静态变换 | `StaticTransformBroadcaster` | `/tf_static` | 安装位置固定的传感器或部件 |
| 动态变换 | `TransformBroadcaster` | `/tf` | 随时间运动的机器人、关节或目标 |

静态 TF 发布一次即可；动态 TF 需要在位姿发生变化时持续更新。

## 构建

在工作空间根目录执行：

```bash
source /opt/ros/humble/setup.bash
colcon build --packages-select learning_tf_py
source install/setup.bash
```

修改 Python 源码或 `setup.py` 后，需要重新构建并刷新 `install/setup.bash`。

## 静态坐标系广播

### 命令格式

`static_tf_broadcaster` 接收 8 个参数：

```text
x y z roll pitch yaw parent_frame child_frame
```

运行格式：

```bash
ros2 run learning_tf_py static_tf_broadcaster \
  <x> <y> <z> <roll> <pitch> <yaw> <parent_frame> <child_frame>
```

参数含义如下：

| 参数 | 含义 |
| --- | --- |
| `x y z` | 子坐标系原点在父坐标系中的平移位置，单位为米 |
| `roll` | 绕 X 轴旋转，单位为弧度 |
| `pitch` | 绕 Y 轴旋转，单位为弧度 |
| `yaw` | 绕 Z 轴旋转，单位为弧度 |
| `parent_frame` | 父坐标系名称 |
| `child_frame` | 子坐标系名称 |

代码使用 `float()` 解析数值参数，再通过：

```python
tf_transformations.quaternion_from_euler(roll, pitch, yaw)
```

将欧拉角转换为四元数，最后调用 `StaticTransformBroadcaster.sendTransform()` 发布变换。

### 基础示例

发布 `base_link -> laser` 的静态关系：

```bash
source install/setup.bash
ros2 run learning_tf_py static_tf_broadcaster \
  0.4 0 0.2 0 0 0 base_link laser
```

该命令表示：

- `laser` 是 `base_link` 的子坐标系。
- `laser` 原点位于 `base_link` 的 `(0.4, 0.0, 0.2)`。
- 两个坐标系方向相同，没有相对旋转。

节点会持续运行，以便后启动的监听器也能获得静态变换。按 `Ctrl+C` 可以正常结束节点。

### 查看静态变换

在新终端执行：

```bash
source /opt/ros/humble/setup.bash
ros2 run tf2_ros tf2_echo base_link laser
```

也可以直接查看静态 TF 话题：

```bash
ros2 topic echo /tf_static
```

## 动态坐标系广播

`dynamic_tf_broadcaster` 订阅：

```text
话题：/turtle1/pose
类型：turtlesim/msg/Pose
```

每次收到小乌龟位姿后，它都会发布：

```text
world -> turtle1
```

字段对应关系为：

```text
translation.x = pose.x
translation.y = pose.y
translation.z = 0.0
yaw = pose.theta
```

代码通过 `quaternion_from_euler(0.0, 0.0, pose.theta)` 将平面朝向角转换为四元数。

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
ros2 run learning_tf_py dynamic_tf_broadcaster
```

终端 4，查看动态变换：

```bash
ros2 run tf2_ros tf2_echo world turtle1
```

移动小乌龟时，平移和旋转数据应持续变化。

## 坐标系监听

`tf_listener` 创建以下对象：

- `tf2_ros.Buffer`：缓存 TF 数据并提供查询接口。
- `tf2_ros.TransformListener`：订阅 `/tf` 和 `/tf_static`，将变换写入 Buffer。
- 1 秒定时器：周期检查并查询坐标关系。

节点首先调用：

```python
self.buffer_.can_transform('camera', 'laser', Time())
```

参数含义如下：

```text
target_frame = camera
source_frame = laser
time         = 最新可用变换
```

只有 `can_transform()` 返回 `True`，节点才继续调用：

```python
self.buffer_.lookup_transform('camera', 'laser', Time())
```

查询结果用于把 `laser` 坐标系中的数据转换到 `camera` 坐标系。当前变换不可用时，节点只打印“转换异常”警告，并在下一次定时器触发时继续检查。

### 监听测试

终端 1，发布 `camera -> laser`：

```bash
source install/setup.bash
ros2 run learning_tf_py static_tf_broadcaster \
  0.3 0.1 0.2 0 0 0 camera laser
```

终端 2，启动监听节点：

```bash
source install/setup.bash
ros2 run learning_tf_py tf_listener
```

正常情况下，节点每秒输出一次 `camera` 与 `laser` 之间的平移关系。

## 坐标点发布

`point_publisher` 每 1 秒向相对话题 `point` 发布一条 `geometry_msgs/msg/PointStamped`。

消息初始值为：

```text
frame_id = laser
x        = 0.0
y        = 0.0
z        = 0.3
```

每次发布后，下一条消息的 X 增加 `0.05`，Y 和 Z 保持不变。时间戳来自节点时钟：

```python
msg.header.stamp = self.get_clock().now().to_msg()
```

启动节点：

```bash
source install/setup.bash
ros2 run learning_tf_py point_publisher
```

查看消息：

```bash
ros2 topic echo /point
```

`PointStamped` 与普通 `Point` 的主要区别是它额外携带时间戳和 `frame_id`，TF2 因此能够判断这个点属于哪个坐标系，以及应该使用哪个时刻的坐标关系。

## 跨语言坐标点变换

当前 Python 功能包没有 `point_transformer`，但 ROS 2 的消息和话题接口与编程语言无关，可以使用 C++ 节点完成变换。

终端 1，使用 Python 发布静态 TF：

```bash
source install/setup.bash
ros2 run learning_tf_py static_tf_broadcaster \
  0.4 0 0.2 0 0 0 base_link laser
```

终端 2，使用 Python 发布点：

```bash
source install/setup.bash
ros2 run learning_tf_py point_publisher
```

终端 3，使用 C++ 节点执行变换：

```bash
source install/setup.bash
ros2 run learning_tf_cpp point_transformer
```

第一个输入点为：

```text
laser: (0.00, 0.00, 0.30)
```

由于 `laser` 相对于 `base_link` 平移 `(0.4, 0.0, 0.2)` 且没有旋转，预期第一个输出点为：

```text
base_link: (0.40, 0.00, 0.50)
```

后续输出 X 应依次为 `0.45`、`0.50`、`0.55` 等；Y 保持 `0.00`，Z 保持 `0.50`。

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

## Python 资源管理

4 个节点都使用相同的退出结构：

```python
try:
    rclpy.spin(node)
except KeyboardInterrupt:
    pass
finally:
    node.destroy_node()
    if rclpy.ok():
        rclpy.shutdown()
```

各部分作用如下：

1. `rclpy.spin(node)` 持续处理订阅、定时器和 TF 回调。
2. `KeyboardInterrupt` 接收用户按下 `Ctrl+C` 产生的中断。
3. `destroy_node()` 主动释放节点资源。
4. `rclpy.ok()` 防止重复关闭已经失效的上下文。
5. `rclpy.shutdown()` 正常关闭 ROS 2 Python 客户端。

## 与 C++ 示例的主要区别

| 对比项 | Python 示例 | C++ 示例 |
| --- | --- | --- |
| 客户端库 | `rclpy` | `rclcpp` |
| 欧拉角转四元数 | `tf_transformations.quaternion_from_euler()` | `tf2::Quaternion::setRPY()` |
| 查询前检查 | 使用 `can_transform()` | 直接查询并捕获异常 |
| 点发布周期 | 1 秒 | 0.1 秒 |
| 点的 Z 初始值 | `0.3` | `-0.5` |
| 点变换节点 | 当前未实现 | 使用 `MessageFilter` 实现 |

## 常见问题

### 找不到功能包或控制台脚本

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
```

如果刚修改源码或 `setup.py`，应重新构建后再刷新工作空间环境。

### 静态广播提示参数数量不合法

节点必须接收 8 个参数：

```text
x y z roll pitch yaw parent_frame child_frame
```

缺少或多出任意参数时，节点不会开始广播。

### 数值参数导致 `ValueError`

Python 示例使用 `float()` 转换前 6 个参数。输入无法转换为浮点数的文本时会抛出 `ValueError`，当前代码没有在节点内部捕获该异常，因此应确保参数都是有效数值。

### 旋转结果与预期不一致

`roll`、`pitch` 和 `yaw` 使用弧度，不是角度。例如 90 度应换算为约 `1.5708` 弧度。

### 监听器持续提示转换异常

检查以下事项：

- 广播节点是否正在运行。
- 坐标系名称是否完全一致，包括大小写。
- 两个坐标系是否位于同一棵 TF 树中。
- `header.frame_id` 和 `child_frame_id` 是否写反。
- 同一个子坐标系是否被多个节点设置了不同父坐标系。

### `/point` 有消息但没有发生坐标变换

`point_publisher` 只负责发布点，不会自行转换或发布变换结果。需要额外启动能够消费 `PointStamped` 并调用 TF2 的变换节点，例如 `learning_tf_cpp point_transformer`。

### 坐标变换方向与预期相反

需要区分两个问题：

```text
广播：子坐标系相对于父坐标系是什么位置？
变换：源坐标系中的数据要转换到哪个目标坐标系？
```

`lookup_transform(target, source, time)` 用于获得从源坐标系表达转换到目标坐标系表达所需的变换。

### TF 数据冲突或跳变

一个子坐标系在同一 TF 树中只能有一个父坐标系。不要同时运行多个广播节点，以不同变换发布相同的 `child_frame_id`。

## 学习要点

- TF2 坐标系树、父子关系和坐标变换方向。
- `/tf` 与 `/tf_static` 的用途和区别。
- `TransformStamped` 中时间戳、父坐标系、子坐标系、平移与旋转字段。
- 使用 `tf_transformations` 将 RPY 欧拉角转换为四元数。
- `StaticTransformBroadcaster` 与 `TransformBroadcaster` 的使用场景。
- `Buffer`、`TransformListener`、`can_transform()` 与 `lookup_transform()` 的职责。
- 空的 `rclpy.time.Time()` 表示查询最新可用变换。
- 使用 `PointStamped` 携带坐标系和时间信息。
- Python 节点的初始化、持续运行与优雅退出流程。
- `setup.py` 中 `console_scripts` 与 `ros2 run` 的对应关系。
- Python 发布节点与 C++ 变换节点之间的跨语言协作。
- 使用 `tf2_echo`、TF 话题和 TF 树工具排查坐标关系。
