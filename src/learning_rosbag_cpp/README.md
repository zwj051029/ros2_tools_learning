# ROS 2 Rosbag2 C++ 学习示例

## 功能包说明

`learning_rosbag_cpp` 用于学习如何在 ROS 2 C++ 节点中调用 `rosbag2_cpp` API，实现话题数据的录制与读取。

本功能包以 `turtlesim` 的速度指令为示例：

- `bag_recoder` 订阅 `/turtle1/cmd_vel`，将 `geometry_msgs/msg/Twist` 消息写入 Bag。
- `bag_player` 读取 Bag 中保存的消息，并通过节点日志输出线速度与角速度。

> 源码和可执行程序使用名称 `recoder`，运行时应保持该拼写。英文中更常见的拼写是 `recorder`，但本文档不修改现有工程命名。

## 环境要求

| 项目 | 要求 |
| --- | --- |
| 操作系统 | Ubuntu 22.04 |
| ROS 2 | Humble Hawksbill |
| 构建类型 | `ament_cmake` |
| C++ 标准 | C++17 |
| Rosbag2 API | `rosbag2_cpp` |
| 消息接口 | `geometry_msgs/msg/Twist` |
| 示例程序 | `turtlesim`、`turtle_teleop_key` |

如果缺少 `turtlesim`，可以安装：

```bash
sudo apt install ros-humble-turtlesim
```

## 目录结构

```text
learning_rosbag_cpp/
├── src/
│   ├── bag_player.cpp
│   └── bag_recoder.cpp
├── CMakeLists.txt
├── package.xml
└── README.md
```

## 节点说明

| 可执行程序 | 节点名称 | 作用 |
| --- | --- | --- |
| `bag_recoder` | `bag_recoder_cpp` | 订阅速度话题并将序列化消息写入 Bag |
| `bag_player` | `bag_player_cpp` | 读取 Bag 中的 `Twist` 消息并输出日志 |

## 数据流向

录制阶段的数据流向如下：

```text
turtle_teleop_key
        │
        │ /turtle1/cmd_vel
        │ geometry_msgs/msg/Twist
        ▼
   bag_recoder
        │
        ▼
   my_bag_cpp/
```

读取阶段的数据流向如下：

```text
my_bag_cpp/
        │
        ▼
    bag_player
        │
        ▼
线速度与角速度日志
```

`bag_player` 当前只读取并打印消息，不会将数据重新发布到 `/turtle1/cmd_vel`，因此它与 `ros2 bag play` 的行为不同。

## 核心实现

### 1. 创建 Writer

录制节点使用独占智能指针管理 Writer：

```cpp
writer_ = std::make_unique<rosbag2_cpp::Writer>();
writer_->open("my_bag_cpp");
```

`std::unique_ptr` 表示 Writer 由当前节点独占管理。节点销毁时，Writer 会随智能指针自动释放。

`my_bag_cpp` 是相对路径，因此 Bag 会创建在执行 `ros2 run` 命令时所在的目录中。

### 2. 订阅序列化消息

录制节点订阅：

```text
话题名称：/turtle1/cmd_vel
消息类型：geometry_msgs/msg/Twist
队列深度：10
```

回调参数使用 `rclcpp::SerializedMessage`，可以把接收到的序列化数据直接交给 Writer，无需先还原为普通 `Twist` 对象。

### 3. 写入消息

每次收到速度指令后，节点调用 `write()` 保存消息：

```cpp
writer_->write(
    msg,
    "/turtle1/cmd_vel",
    "geometry_msgs/msg/Twist",
    this->now()
);
```

四个参数分别表示：

1. 待写入的序列化消息。
2. 消息所属的话题名称。
3. 完整消息类型名称。
4. 当前消息的记录时间戳。

话题名称和消息类型必须与实际数据一致，否则后续解析可能失败。

### 4. 创建 Reader

读取节点打开同一个 Bag：

```cpp
reader_ = std::make_unique<rosbag2_cpp::Reader>();
reader_->open("my_bag_cpp");
```

随后通过 `has_next()` 判断是否还有消息，并使用 `read_next<Twist>()` 将下一条记录反序列化为 `Twist`。

### 5. 输出读取结果

读取节点输出两个与小乌龟运动直接相关的字段：

```text
msg.linear.x   前进或后退的线速度
msg.angular.z  绕 Z 轴旋转的角速度
```

Bag 中的全部消息读取完毕后，不会继续产生新日志。由于节点随后进入 `rclcpp::spin()`，需要按 `Ctrl+C` 结束进程。

## 构建

在工作空间根目录执行：

```bash
source /opt/ros/humble/setup.bash
colcon build --packages-select learning_rosbag_cpp
source install/setup.bash
```

`CMakeLists.txt` 完成以下工作：

- 查找 `rclcpp`、`rosbag2_cpp` 和 `geometry_msgs` 依赖。
- 编译 `bag_recoder` 与 `bag_player` 两个可执行程序。
- 将可执行程序安装到 `lib/learning_rosbag_cpp`。
- 启用 C++17 和常用编译警告。

## 完整运行流程

建议所有命令都在工作空间根目录执行，以便录制节点和读取节点使用同一个 `my_bag_cpp` 路径。

### 1. 启动小乌龟

终端 1：

```bash
source /opt/ros/humble/setup.bash
ros2 run turtlesim turtlesim_node
```

### 2. 启动键盘控制

终端 2：

```bash
source /opt/ros/humble/setup.bash
ros2 run turtlesim turtle_teleop_key
```

保持该终端处于激活状态，通过方向键产生速度指令。

### 3. 启动录制节点

终端 3，在工作空间根目录执行：

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 run learning_rosbag_cpp bag_recoder
```

移动小乌龟一段时间后，在录制终端按 `Ctrl+C`。当前目录下应生成：

```text
my_bag_cpp/
├── metadata.yaml
└── *.db3
```

再次录制前，应先确认当前目录不存在同名的 `my_bag_cpp`，或者为旧数据更换名称、移动位置。

### 4. 查看 Bag 信息

```bash
ros2 bag info my_bag_cpp
```

正常情况下可以看到存储格式、持续时间、消息数量以及以下话题信息：

```text
Topic: /turtle1/cmd_vel
Type: geometry_msgs/msg/Twist
```

### 5. 使用自定义节点读取

```bash
source install/setup.bash
ros2 run learning_rosbag_cpp bag_player
```

预期日志类似：

```text
[INFO] [...] [bag_player_cpp]: 数据回放方创建成功!
[INFO] [...] [bag_player_cpp]: 线速度: 2.00, 角速度: 0.00
[INFO] [...] [bag_player_cpp]: 线速度: 0.00, 角速度: 2.00
```

实际数值与录制时按下的方向键有关。

### 6. 使用 ROS 2 CLI 回放

如需按照 Bag 中的时间顺序重新发布话题，可以使用：

```bash
ros2 bag play my_bag_cpp
```

运行 `turtlesim_node` 后执行该命令，小乌龟会接收重新发布的速度指令。自定义 `bag_player` 只打印内容，而该命令会真正发布录制的话题消息。

## 运行检查

检查录制节点是否订阅了目标话题：

```bash
ros2 node info /bag_recoder_cpp
```

查看速度话题的消息类型：

```bash
ros2 topic type /turtle1/cmd_vel
```

预期输出：

```text
geometry_msgs/msg/Twist
```

观察实时速度消息：

```bash
ros2 topic echo /turtle1/cmd_vel
```

检查 Bag 是否包含消息：

```bash
ros2 bag info my_bag_cpp
```

## `bag_player` 与 `ros2 bag play` 的区别

| 对比项 | `bag_player` | `ros2 bag play` |
| --- | --- | --- |
| 实现方式 | 自定义 C++ Reader | ROS 2 命令行工具 |
| 当前功能 | 读取消息并打印日志 | 按时间顺序重新发布消息 |
| 是否驱动订阅者 | 否 | 是 |
| 是否保留原始播放节奏 | 当前实现不保留 | 默认按照录制时间播放 |
| 学习重点 | `rosbag2_cpp::Reader` API | Bag 的标准回放操作 |

## 常见问题

### 找不到功能包或可执行程序

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
```

如果刚修改源码，应重新构建后再刷新环境。

### 提示 Bag 路径已存在

`Writer::open("my_bag_cpp")` 需要创建或打开对应存储目录。重复录制前，应处理当前工作目录中的旧 Bag，避免与同名目录冲突。

### `bag_player` 找不到 Bag

源码使用相对路径 `my_bag_cpp`。请在包含该目录的位置运行读取节点，或者检查录制和读取命令是否在不同目录执行。

### 录制节点没有写入消息

依次确认：

```bash
ros2 topic list
ros2 topic type /turtle1/cmd_vel
ros2 topic echo /turtle1/cmd_vel
```

只有键盘控制节点实际发布速度指令时，录制回调才会执行。

### 读取完成后程序没有自动退出

当前 `bag_player` 在构造函数中读取全部消息，随后进入 `rclcpp::spin()`。消息读取完毕后不会再打印内容，但进程仍然运行，按 `Ctrl+C` 即可退出。

### Conda 环境导致构建失败

如果构建日志显示 CMake 调用了 Conda 中的 Python，并提示缺少 `catkin_pkg`，先退出 Conda 环境：

```bash
conda deactivate
```

然后重新加载 ROS 2 环境并构建。

## 学习要点

- Rosbag2 的录制、存储、查看和回放流程。
- `rosbag2_cpp::Writer` 与 `rosbag2_cpp::Reader` 的基本使用。
- 使用 `std::unique_ptr` 独占管理 Reader 和 Writer。
- 订阅 `rclcpp::SerializedMessage` 并直接写入 Bag。
- 话题名称、消息类型与记录时间戳在写入过程中的作用。
- 使用 `has_next()` 遍历 Bag，并将记录反序列化为指定消息类型。
- 相对路径与当前工作目录对 Bag 存储位置的影响。
- 自定义读取程序与标准 `ros2 bag play` 回放工具的差异。
