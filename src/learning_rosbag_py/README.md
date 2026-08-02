# ROS 2 Rosbag2 Python 学习示例

## 功能包说明

`learning_rosbag_py` 用于学习如何在 ROS 2 Python 节点中调用 `rosbag2_py` API，实现话题数据的录制与读取。

本功能包以 `turtlesim` 的速度指令为示例：

- `bag_recoder` 订阅 `/turtle1/cmd_vel`，序列化 `geometry_msgs/msg/Twist` 消息并写入 Bag。
- `bag_player` 读取 Bag 中保存的记录，并输出话题名称、时间戳和序列化数据。

> 源码和控制台脚本使用名称 `recoder`，运行时应保持该拼写。英文中更常见的拼写是 `recorder`，但本文档不修改现有工程命名。

## 环境要求

| 项目 | 要求 |
| --- | --- |
| 操作系统 | Ubuntu 22.04 |
| ROS 2 | Humble Hawksbill |
| 构建类型 | `ament_python` |
| Python 构建工具 | `setuptools` |
| Rosbag2 API | `rosbag2_py` |
| 消息接口 | `geometry_msgs/msg/Twist` |
| 示例程序 | `turtlesim`、`turtle_teleop_key` |

如果缺少 `turtlesim`，可以安装：

```bash
sudo apt install ros-humble-turtlesim
```

## 目录结构

```text
learning_rosbag_py/
├── learning_rosbag_py/
│   ├── __init__.py
│   ├── bag_player.py
│   └── bag_recoder.py
├── resource/
│   └── learning_rosbag_py
├── test/
│   ├── test_copyright.py
│   ├── test_flake8.py
│   └── test_pep257.py
├── package.xml
├── setup.cfg
├── setup.py
└── README.md
```

## 节点说明

| 控制台脚本 | 节点名称 | 作用 |
| --- | --- | --- |
| `bag_recoder` | `simple_bag_recorder_py` | 订阅速度话题，序列化消息并写入 Bag |
| `bag_player` | `simple_bag_player_py` | 顺序读取 Bag，并输出每条记录的原始内容 |

`setup.py` 通过 `console_scripts` 将两个 `main()` 函数注册为可由 `ros2 run` 启动的程序：

```python
'bag_recoder = learning_rosbag_py.bag_recoder:main'
'bag_player = learning_rosbag_py.bag_player:main'
```

## 数据流向

录制阶段的数据流向如下：

```text
turtle_teleop_key
        │
        │ /turtle1/cmd_vel
        │ geometry_msgs/msg/Twist
        ▼
   bag_recoder
        │ serialize_message()
        ▼
    my_bag_py/
```

读取阶段的数据流向如下：

```text
my_bag_py/
        │
        ▼
    bag_player
        │ read_next()
        ▼
话题名称、时间戳和序列化字节日志
```

`bag_player` 当前只读取并打印记录，不会将数据重新发布到 `/turtle1/cmd_vel`，因此它与 `ros2 bag play` 的行为不同。

## 核心实现

### 1. 创建 SequentialWriter

录制节点创建顺序写入器：

```python
self.writer = rosbag2_py.SequentialWriter()
```

`SequentialWriter` 按照消息到达顺序将数据写入 Rosbag2 存储文件。

### 2. 配置存储与转换

写入器通过两个配置对象打开 Bag：

```python
storage_options = rosbag2_py._storage.StorageOptions(
    uri='my_bag_py',
    storage_id='sqlite3'
)
converter_options = rosbag2_py._storage.ConverterOptions('', '')
self.writer.open(storage_options, converter_options)
```

各参数含义如下：

| 参数 | 作用 |
| --- | --- |
| `uri` | Bag 的存储目录 |
| `storage_id` | 存储后端，当前使用 SQLite3 |
| `ConverterOptions('', '')` | 不进行额外的输入、输出序列化格式转换 |

`my_bag_py` 是相对路径，因此 Bag 会创建在执行 `ros2 run` 命令时所在的目录中。

### 3. 注册话题元数据

写入消息前，需要先告诉 Writer 将要记录的话题信息：

```python
topic_info = rosbag2_py._storage.TopicMetadata(
    name='/turtle1/cmd_vel',
    type='geometry_msgs/msg/Twist',
    serialization_format='cdr'
)
self.writer.create_topic(topic_info)
```

元数据包含：

1. 话题名称 `/turtle1/cmd_vel`。
2. 完整消息类型 `geometry_msgs/msg/Twist`。
3. ROS 2 默认使用的 CDR 序列化格式。

话题元数据必须与实际写入的消息一致，否则读取或反序列化时可能失败。

### 4. 序列化并写入消息

订阅回调收到的是普通 `Twist` 消息对象。写入 Bag 前，通过 `serialize_message()` 将其转换为字节数据：

```python
self.writer.write(
    '/turtle1/cmd_vel',
    serialize_message(msg),
    self.get_clock().now().nanoseconds
)
```

三个参数分别表示：

1. 消息所属的话题名称。
2. 序列化后的消息数据。
3. 以纳秒表示的记录时间戳。

### 5. 创建 SequentialReader

读取节点使用同样的存储配置打开 Bag：

```python
self.reader = rosbag2_py.SequentialReader()
self.reader.open(storage_options, converter_options)
```

`SequentialReader` 会按照 Bag 中的记录顺序读取消息。

### 6. 读取消息三元组

读取节点先通过 `has_next()` 判断是否还有记录，再调用：

```python
msg = self.reader.read_next()
```

当前 ROS 2 Humble 环境中，返回值可按以下结构理解：

```text
msg[0]  话题名称
msg[1]  序列化消息数据
msg[2]  记录时间戳
```

当前代码直接打印 `msg[1]`，因此日志中的 `value` 是二进制字节表示，不是已经还原字段的 `Twist` 对象。

Bag 中的全部消息读取完毕后，不会继续产生新日志。由于节点随后进入 `rclpy.spin()`，需要按 `Ctrl+C` 结束进程。

## 构建

在工作空间根目录执行：

```bash
source /opt/ros/humble/setup.bash
colcon build --packages-select learning_rosbag_py
source install/setup.bash
```

修改 Python 源码或 `setup.py` 后，应重新构建并刷新工作空间环境。

## 完整运行流程

建议所有命令都在工作空间根目录执行，以便录制节点和读取节点使用同一个 `my_bag_py` 路径。

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
ros2 run learning_rosbag_py bag_recoder
```

移动小乌龟一段时间后，在录制终端按 `Ctrl+C`。当前目录下应生成：

```text
my_bag_py/
├── metadata.yaml
└── *.db3
```

再次录制前，应先确认当前目录不存在同名的 `my_bag_py`，或者为旧数据更换名称、移动位置。

### 4. 查看 Bag 信息

```bash
ros2 bag info my_bag_py
```

正常情况下可以看到存储格式、持续时间、消息数量以及以下话题信息：

```text
Topic: /turtle1/cmd_vel
Type: geometry_msgs/msg/Twist
```

### 5. 使用自定义节点读取

```bash
source install/setup.bash
ros2 run learning_rosbag_py bag_player
```

预期日志结构类似：

```text
[INFO] [...] [rclpy]: topic = /turtle1/cmd_vel, time = ..., value=b'...'
```

日志中的时间戳和字节内容由实际录制的数据决定。

### 6. 使用 ROS 2 CLI 回放

如需按照 Bag 中的时间顺序重新发布话题，可以使用：

```bash
ros2 bag play my_bag_py
```

运行 `turtlesim_node` 后执行该命令，小乌龟会接收重新发布的速度指令。自定义 `bag_player` 只打印内容，而该命令会真正发布录制的话题消息。

## 运行检查

检查录制节点是否订阅了目标话题：

```bash
ros2 node info /simple_bag_recorder_py
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
ros2 bag info my_bag_py
```

## `bag_player` 与 `ros2 bag play` 的区别

| 对比项 | `bag_player` | `ros2 bag play` |
| --- | --- | --- |
| 实现方式 | 自定义 Python Reader | ROS 2 命令行工具 |
| 当前功能 | 读取记录并打印原始数据 | 按时间顺序重新发布消息 |
| 是否反序列化为 `Twist` | 否 | 内部处理后发布 |
| 是否驱动订阅者 | 否 | 是 |
| 是否保留原始播放节奏 | 当前实现不保留 | 默认按照录制时间播放 |
| 学习重点 | `rosbag2_py.SequentialReader` API | Bag 的标准回放操作 |

## 与 C++ 示例的主要区别

| 对比项 | Python 示例 | C++ 示例 |
| --- | --- | --- |
| 写入 API | `rosbag2_py.SequentialWriter` | `rosbag2_cpp::Writer` |
| 读取 API | `rosbag2_py.SequentialReader` | `rosbag2_cpp::Reader` |
| 写入前处理 | 显式调用 `serialize_message()` | 订阅序列化消息并直接写入 |
| 当前读取结果 | 打印原始序列化字节 | 反序列化为 `Twist` 后打印字段 |
| Bag 目录 | `my_bag_py` | `my_bag_cpp` |

## 常见问题

### 找不到功能包或可执行程序

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
```

如果刚修改源码或 `setup.py`，应重新构建后再刷新环境。

### 提示 Bag 路径已存在

Writer 需要在 `my_bag_py` 中创建存储文件。重复录制前，应处理当前工作目录中的旧 Bag，避免与同名目录冲突。

### `bag_player` 找不到 Bag

源码使用相对路径 `my_bag_py`。请在包含该目录的位置运行读取节点，或者检查录制和读取命令是否在不同目录执行。

### 录制节点没有写入消息

依次确认：

```bash
ros2 topic list
ros2 topic type /turtle1/cmd_vel
ros2 topic echo /turtle1/cmd_vel
```

只有键盘控制节点实际发布速度指令时，订阅回调才会执行并写入数据。

### 日志中的 `value` 无法直接阅读

这是当前实现的正常现象。`read_next()` 返回的是序列化消息数据，代码没有调用 `deserialize_message()` 将其还原为 `Twist` 对象。

### 读取完成后程序没有自动退出

当前 `bag_player` 先同步读取全部消息，随后进入 `rclpy.spin()`。消息读取完毕后不会再打印内容，但进程仍然运行，按 `Ctrl+C` 即可退出。

### Conda 环境导致构建失败

如果 ROS 2 命令使用了 Conda 的 Python 并出现依赖冲突，先退出 Conda 环境：

```bash
conda deactivate
```

然后重新加载 ROS 2 环境并构建。

## 学习要点

- Rosbag2 的录制、存储、查看和回放流程。
- `rosbag2_py.SequentialWriter` 与 `SequentialReader` 的基本使用。
- `StorageOptions`、`ConverterOptions` 和 `TopicMetadata` 的职责。
- 使用 `serialize_message()` 将 ROS 2 消息转换为可写入的字节数据。
- CDR 序列化格式以及话题元数据的重要性。
- 使用 `has_next()` 和 `read_next()` 顺序遍历 Bag。
- 理解读取结果中的话题名称、序列化数据和时间戳。
- `setup.py` 中 `console_scripts` 与 `ros2 run` 的对应关系。
- 相对路径与当前工作目录对 Bag 存储位置的影响。
- 自定义读取程序与标准 `ros2 bag play` 回放工具的差异。
