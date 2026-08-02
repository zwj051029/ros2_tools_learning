# ROS 2 Rosbag2 知识点总结

## 1. Rosbag2 是什么

Rosbag2 是 ROS 2 中用于录制、保存、查看和回放消息数据的工具。

机器人运行时，传感器、定位、控制、TF 等数据通常通过话题持续传输。Rosbag2 可以像“数据录像机”一样把这些消息按时间保存下来，之后在没有真实机器人或传感器的情况下重新查看和发布。

典型用途：

- 记录机器人现场运行数据。
- 复现偶发故障和异常场景。
- 离线调试感知、定位和规划算法。
- 保存传感器数据用于算法验证。
- 比较修改前后的算法输出。
- 为演示、测试和回归测试提供固定输入。
- 在团队之间传递可复现的数据样本。

一句话理解：

```text
Rosbag2 记录的是 ROS 2 消息及其时间信息，而不是整个正在运行的机器人程序。
```

## 2. Rosbag2 不会自动保存什么

Rosbag2 主要记录话题消息。仅仅保存 Bag，通常不能完整恢复当时的系统状态。

它不会自动保存：

- 节点源代码和可执行程序版本。
- Launch 文件和启动参数。
- 未通过已录制话题传输的内部变量。
- 操作系统、驱动和依赖环境。
- 所有节点参数的完整快照。
- 环境变量和工作空间覆盖关系。
- 机器人硬件本身的状态。

为了让数据真正可复现，工程中通常还需要同步保存：

```text
代码提交版本 + 配置文件 + Launch 命令 + 参数 + Bag 数据 + 环境说明
```

## 3. Rosbag2 基本架构

Rosbag2 可以理解为以下几层：

```text
ROS 2 话题
    │
    ▼
Recorder / Writer
    │ 序列化消息、话题元数据、时间戳
    ▼
Storage Plugin
    │
    ▼
Bag 目录
    │
    ▼
Reader / Player
    │
    ▼
读取数据或重新发布话题
```

核心组件：

| 组件 | 作用 |
| --- | --- |
| Recorder | 发现并订阅目标话题，将消息交给存储层 |
| Writer | 在代码中主动创建和写入 Bag |
| Storage Plugin | 决定消息在磁盘中的存储格式 |
| Reader | 按顺序读取 Bag 中的记录 |
| Player | 根据时间戳重新发布记录的消息 |
| Converter | 在需要时转换序列化格式 |

ROS 2 Humble 默认常用的存储插件是 SQLite3，对应数据文件通常以 `.db3` 结尾。

## 4. Bag 目录结构

执行：

```bash
ros2 bag record -o robot_run /topic_name
```

通常会生成：

```text
robot_run/
├── metadata.yaml
└── robot_run_0.db3
```

### `metadata.yaml`

元数据文件通常包含：

- 存储插件名称。
- Bag 持续时间。
- 起始时间。
- 消息总数。
- 话题名称和消息类型。
- 各话题消息数量。
- 序列化格式。
- QoS 相关信息。
- 分包文件列表。

### `.db3` 文件

SQLite3 存储文件保存序列化消息、时间戳、话题索引等实际数据。

不要只复制 `.db3` 而漏掉 `metadata.yaml`。移动数据时应复制整个 Bag 目录。

## 5. 开始前的检查

加载 ROS 2 环境：

```bash
source /opt/ros/humble/setup.bash
```

查看当前话题：

```bash
ros2 topic list
```

确认消息类型：

```bash
ros2 topic type /topic_name
```

确认话题确实有数据：

```bash
ros2 topic echo /topic_name
```

查看发布频率：

```bash
ros2 topic hz /topic_name
```

先确认数据源正常，再开始录制，可以避免得到消息数量为 0 的 Bag。

## 6. CLI 录制基础

### 录制一个话题

```bash
ros2 bag record /turtle1/cmd_vel
```

未指定输出名称时，Rosbag2 会在当前目录创建带时间戳的目录。

### 指定输出目录

```bash
ros2 bag record -o turtle_bag /turtle1/cmd_vel
```

`-o` 是 `--output` 的简写。

### 同时录制多个话题

```bash
ros2 bag record -o turtle_bag \
  /turtle1/cmd_vel \
  /turtle1/pose
```

### 录制全部已发现话题

```bash
ros2 bag record -a -o all_topics_bag
```

`-a` 是 `--all` 的简写。

录制全部话题很方便，但可能产生大量无关数据并快速占满磁盘。实际机器人项目更推荐明确选择需要的话题。

### 结束录制

在录制终端按：

```text
Ctrl+C
```

应尽量让 Recorder 正常退出，以便缓存数据和元数据正确写入磁盘。强制终止进程或突然断电可能留下不完整的 Bag。

## 7. 话题筛选

### 按正则表达式录制

```bash
ros2 bag record -e '^/camera/.*' -o camera_bag
```

`-e` 或 `--regex` 用于选择名称匹配正则表达式的话题。

### 排除话题

```bash
ros2 bag record -a -x '^/debug/.*' -o robot_bag
```

`-x` 或 `--exclude` 可以在全部话题或正则筛选结果中排除不需要的话题。

### 包含隐藏话题

```bash
ros2 bag record -a --include-hidden-topics -o bag_with_hidden_topics
```

隐藏话题通常是 ROS 2 内部机制使用的话题。没有明确需求时，不建议为了“完整”而盲目录制。

## 8. 录制时的话题发现

默认情况下，Recorder 会周期发现新出现的话题。因此录制启动后才创建的发布方，也可能被自动加入录制。

相关选项：

| 选项 | 作用 |
| --- | --- |
| `--no-discovery` | 禁止运行期间继续发现新话题 |
| `--polling-interval` | 设置发现话题的轮询间隔，单位为毫秒 |
| `--include-unpublished-topics` | 包含当前没有发布方的话题 |
| `--ignore-leaf-topics` | 忽略没有发布方的话题 |

使用 `--no-discovery` 时，只会录制启动 Recorder 时已经存在且符合条件的话题。

## 9. 查看 Bag 信息

```bash
ros2 bag info turtle_bag
```

重点关注：

| 字段 | 含义 |
| --- | --- |
| Storage id | 存储插件 |
| Duration | 录制持续时间 |
| Start | 起始时间 |
| Messages | 消息总数 |
| Topic | 话题名称 |
| Type | 消息类型 |
| Count | 对应话题消息数量 |

判断录制是否成功时，不要只看目录是否存在，还要检查：

```text
消息数量是否大于 0
话题名称是否正确
消息类型是否正确
持续时间是否符合预期
```

## 10. CLI 回放基础

### 回放全部记录

```bash
ros2 bag play turtle_bag
```

Player 会根据 Bag 中的时间戳安排消息发布，尽量还原原始消息节奏。

### 只回放指定话题

```bash
ros2 bag play turtle_bag --topics /turtle1/cmd_vel
```

### 调整播放速度

两倍速：

```bash
ros2 bag play turtle_bag --rate 2.0
```

半速：

```bash
ros2 bag play turtle_bag --rate 0.5
```

播放速率必须大于 `0.0`。

### 循环播放

```bash
ros2 bag play turtle_bag --loop
```

到达末尾后会重新从头播放，直到用户结束进程。

### 从指定时间开始

```bash
ros2 bag play turtle_bag --start-offset 5.0
```

表示跳过 Bag 开头 5 秒，从后续位置开始回放。

### 延迟开始播放

```bash
ros2 bag play turtle_bag --delay 2.0
```

Player 启动后等待 2 秒再开始发布，便于订阅方先完成初始化。

### 启动时暂停

```bash
ros2 bag play turtle_bag --start-paused
```

适合先启动所有订阅节点，再手动开始播放。

## 11. 回放时重映射

Bag 中保存的是录制时的话题名称。回放时可以把旧名称映射到新名称：

```bash
ros2 bag play turtle_bag \
  --remap /turtle1/cmd_vel:=/robot/cmd_vel
```

重映射常用于：

- 将历史数据输入新版本节点。
- 给多个测试实例使用不同命名空间。
- 避免与实时话题冲突。
- 将真实机器人数据接入仿真或离线算法。

## 12. 回放与 `/clock`

通过以下命令让 Player 发布 ROS 时间：

```bash
ros2 bag play turtle_bag --clock
```

也可以指定 `/clock` 发布频率：

```bash
ros2 bag play turtle_bag --clock 100
```

需要跟随 Bag 时间的节点应设置：

```text
use_sim_time = true
```

基本关系：

```text
ros2 bag play --clock
        │
        ▼
      /clock
        │
        ▼
use_sim_time=true 的节点
```

如果 Player 不发布 `/clock`，或者节点没有启用 `use_sim_time`，节点仍然使用系统时间。

## 13. 录制仿真时间

Recorder 支持：

```bash
ros2 bag record -a --use-sim-time -o sim_bag
```

启用后，Recorder 订阅 `/clock` 并使用仿真时间作为消息时间基准。在收到第一条 `/clock` 之前，不会写入消息。

仿真系统中应统一规划时间来源，避免一部分节点使用系统时间、另一部分使用仿真时间。

## 14. QoS 与 Rosbag2

ROS 2 通信受 QoS 影响。Recorder 本质上是订阅方，Player 本质上是发布方，因此它们也必须满足 QoS 兼容规则。

常见 QoS 维度：

- Reliability：`reliable` 或 `best_effort`。
- Durability：`volatile` 或 `transient_local`。
- History：保留策略。
- Depth：队列深度。

容易出现的现象：

- 话题存在，但 Bag 中消息数为 0。
- 传感器 `best_effort` 数据没有按预期录制。
- 回放后订阅节点收不到消息。
- `/tf_static` 等 `transient_local` 数据表现异常。

查看话题 QoS：

```bash
ros2 topic info /topic_name --verbose
```

Recorder 和 Player 都支持 QoS 覆盖文件：

```bash
ros2 bag record /topic_name \
  --qos-profile-overrides-path qos_overrides.yaml
```

```bash
ros2 bag play robot_bag \
  --qos-profile-overrides-path qos_overrides.yaml
```

遇到“话题存在但收不到数据”时，应优先检查 QoS，而不是只检查话题名称。

## 15. 分包

长时间录制时，可以按大小或持续时间拆分存储文件。

### 按大小分包

```bash
ros2 bag record -a \
  --max-bag-size 1073741824 \
  -o robot_bag
```

示例限制每个存储文件约为 1 GiB。

### 按时长分包

```bash
ros2 bag record -a \
  --max-bag-duration 300 \
  -o robot_bag
```

示例每 300 秒切换到新的存储文件。

同时设置大小和时长时，先达到的条件会触发分包。

分包仍然属于同一个 Bag 目录，`metadata.yaml` 会记录全部存储文件。

## 16. 压缩

录制时可以启用压缩：

```bash
ros2 bag record -a \
  --compression-mode file \
  --compression-format zstd \
  -o compressed_bag
```

常见压缩模式：

| 模式 | 含义 |
| --- | --- |
| `none` | 不压缩 |
| `file` | 按存储文件压缩 |
| `message` | 按消息压缩 |

压缩可以降低磁盘占用，但会增加 CPU 消耗。高频相机、点云等大数据录制前，应结合磁盘写入速度和 CPU 性能测试。

## 17. 缓存与写入性能

Recorder 可以通过 `--max-cache-size` 控制缓存大小：

```bash
ros2 bag record -a --max-cache-size 104857600 -o robot_bag
```

缓存可以缓冲短时间写盘波动，但会占用内存。Humble 的 Recorder 使用双缓冲，极端情况下内存占用可能达到配置值的约两倍。

如果设置为 `0`，每条消息会直接写入磁盘。

性能规划应考虑：

```text
总消息带宽
磁盘持续写入速度
CPU 序列化和压缩开销
可用内存
允许丢失的数据量
```

## 18. 快照模式

快照模式先把消息保存在缓存中，直到调用服务才写入 Bag：

```bash
ros2 bag record -a --snapshot-mode -o snapshot_bag
```

触发快照：

```bash
ros2 service call \
  /rosbag2_recorder/snapshot \
  rosbag2_interfaces/srv/Snapshot
```

适合记录故障发生前的一段数据，例如机器人碰撞、定位突然发散或控制器异常。缓存大小决定能够保留多长时间的数据。

## 19. 修复元数据

如果录制被异常终止，Bag 数据文件存在但 `metadata.yaml` 缺失或损坏，可以尝试：

```bash
ros2 bag reindex <bag_directory>
```

`reindex` 会根据存储文件重新构建元数据。它不能保证修复所有损坏的数据，因此正常结束录制和做好备份仍然更重要。

## 20. 存储插件

查看当前可用插件：

```bash
ros2 bag list
```

指定存储插件：

```bash
ros2 bag record -s sqlite3 -o robot_bag /topic_name
```

回放和查看时通常会自动从元数据识别存储格式，也可以通过 `-s` 显式指定。

Rosbag2 的存储层是插件化的。不同 ROS 2 发行版或额外安装的插件可能支持不同格式，不应假设所有电脑都有完全相同的插件列表。

## 21. C++ Writer 基础

包含头文件：

```cpp
#include "rosbag2_cpp/writer.hpp"
```

创建并打开 Writer：

```cpp
auto writer = std::make_unique<rosbag2_cpp::Writer>();
writer->open("my_bag_cpp");
```

写入序列化消息：

```cpp
writer->write(
    serialized_message,
    "/turtle1/cmd_vel",
    "geometry_msgs/msg/Twist",
    node->now()
);
```

四项信息必须正确对应：

```text
消息内容
话题名称
消息类型
记录时间戳
```

### 为什么使用 `std::unique_ptr`

Reader 或 Writer 通常只属于当前节点，不需要多个对象共享所有权，因此适合用 `std::unique_ptr`：

- 明确表示独占所有权。
- 节点销毁时自动释放资源。
- 不需要引用计数，语义更直接。

## 22. C++ Reader 基础

包含头文件：

```cpp
#include "rosbag2_cpp/reader.hpp"
```

创建并打开 Reader：

```cpp
auto reader = std::make_unique<rosbag2_cpp::Reader>();
reader->open("my_bag_cpp");
```

顺序读取：

```cpp
while (reader->has_next()) {
    auto msg = reader->read_next<geometry_msgs::msg::Twist>();
    // 使用 msg.linear.x、msg.angular.z 等字段
}
```

自定义 Reader 只是“读取数据”，不会自动按原始时间间隔等待，也不会自动重新发布话题。要实现标准回放行为，还需要自行处理时间调度和 Publisher。

## 23. Python SequentialWriter 基础

创建 Writer：

```python
import rosbag2_py

writer = rosbag2_py.SequentialWriter()
```

配置存储：

```python
storage_options = rosbag2_py._storage.StorageOptions(
    uri='my_bag_py',
    storage_id='sqlite3'
)
converter_options = rosbag2_py._storage.ConverterOptions('', '')
writer.open(storage_options, converter_options)
```

注册话题元数据：

```python
topic_info = rosbag2_py._storage.TopicMetadata(
    name='/turtle1/cmd_vel',
    type='geometry_msgs/msg/Twist',
    serialization_format='cdr'
)
writer.create_topic(topic_info)
```

写入消息：

```python
from rclpy.serialization import serialize_message

writer.write(
    '/turtle1/cmd_vel',
    serialize_message(msg),
    node.get_clock().now().nanoseconds
)
```

Python 接收到的是普通消息对象，写入前需要显式序列化。

## 24. Python SequentialReader 基础

创建并打开 Reader：

```python
reader = rosbag2_py.SequentialReader()
reader.open(storage_options, converter_options)
```

顺序读取：

```python
while reader.has_next():
    topic_name, serialized_data, timestamp = reader.read_next()
```

返回的三项内容：

| 元素 | 含义 |
| --- | --- |
| `topic_name` | 话题名称 |
| `serialized_data` | 序列化后的二进制消息 |
| `timestamp` | 记录时间戳 |

如果需要访问消息字段，应使用正确消息类型反序列化：

```python
from geometry_msgs.msg import Twist
from rclpy.serialization import deserialize_message

msg = deserialize_message(serialized_data, Twist)
```

一个 Bag 可能包含多种消息类型。通用读取工具应先根据话题元数据建立“话题名称到消息类型”的映射，再选择对应类型反序列化。

## 25. 录制时间与消息自身时间戳

需要区分两类时间：

```text
Bag 记录时间
消息 header.stamp
```

- Bag 记录时间由 Recorder 或 Writer 传入，用于排序和回放调度。
- `header.stamp` 是消息内容的一部分，通常表示传感器采样或数据生成时间。

两者可能不完全相同，例如消息经过网络、队列或处理节点后才被 Recorder 收到。

进行传感器同步、TF 查询和延迟分析时，应明确自己使用的是哪一个时间。

## 26. 自定义 Reader 与标准 Player 的区别

| 对比项 | 自定义 Reader | `ros2 bag play` |
| --- | --- | --- |
| 读取消息 | 是 | 是 |
| 自动反序列化 | 由代码决定 | 内部处理 |
| 重新发布话题 | 需要自己实现 | 是 |
| 保留原始时间节奏 | 需要自己实现 | 默认支持 |
| 支持速率、循环、重映射 | 需要自己实现 | 命令行直接支持 |
| 适合用途 | 数据分析和定制处理 | 标准消息回放 |

不要因为自定义程序名为 `bag_player`，就默认它一定具备标准 Player 的全部行为。应以实际源码是否创建 Publisher、是否根据时间戳调度为准。

## 27. 小乌龟完整练习

### 启动数据源

终端 1：

```bash
ros2 run turtlesim turtlesim_node
```

终端 2：

```bash
ros2 run turtlesim turtle_teleop_key
```

### 录制速度与位姿

终端 3：

```bash
ros2 bag record -o turtle_bag \
  /turtle1/cmd_vel \
  /turtle1/pose
```

移动小乌龟一段时间，然后在录制终端按 `Ctrl+C`。

### 检查数据

```bash
ros2 bag info turtle_bag
```

确认两个话题的消息数量都大于 0。

### 回放

重新启动 `turtlesim_node`，然后执行：

```bash
ros2 bag play turtle_bag --topics /turtle1/cmd_vel
```

小乌龟会再次接收录制的速度命令。

`/turtle1/pose` 是小乌龟自身发布的状态话题，通常用于观察或离线分析，不应在同一个运行图中随意与实时状态源重复发布。

## 28. 机器人项目中的录制规划

不要等故障发生后才临时决定录什么。可以提前按层次规划话题。

### 基础状态

```text
/tf
/tf_static
/joint_states
/diagnostics
```

### 传感器

```text
相机图像与 CameraInfo
激光雷达 Scan 或 PointCloud2
IMU
里程计
GNSS
```

### 算法输出

```text
定位位姿
局部与全局地图
规划路径
目标速度
障碍物检测结果
```

### 控制与任务

```text
速度指令
底盘反馈
任务状态
关键诊断信息
```

选择原则：

- 能否用这些数据复现问题？
- 是否包含算法输入与输出？
- 是否记录了所需 TF？
- 是否包含时间同步所需话题？
- 数据量是否超过磁盘和计算能力？
- 是否包含隐私或敏感信息？

## 29. 大数据话题注意事项

相机和点云数据常带来很高的数据率。

录制前应评估：

```text
单条消息大小 x 发布频率 x 话题数量 x 录制时长
```

可采取的措施：

- 只录制需要的话题。
- 降低传感器发布频率或分辨率。
- 使用合适的压缩模式。
- 使用高速 SSD。
- 设置分包大小或时长。
- 监控 CPU、内存和磁盘写入。
- 录制后检查消息数量和时间跨度。

磁盘目录生成并不代表数据没有丢失。高负载场景必须通过统计和实际回放验证。

## 30. 常见问题

### Bag 输出目录已存在

同名输出目录可能导致 Recorder 或 Writer 无法创建 Bag。

解决思路：

- 使用新的 `-o` 名称。
- 将旧 Bag 移动到归档位置。
- 确认旧数据不再需要后再处理。

不要在不确认内容的情况下直接覆盖旧数据。

### Bag 中消息数量为 0

检查：

1. 录制时发布方是否正在运行。
2. 话题名称是否正确。
3. 话题是否真的产生消息。
4. QoS 是否兼容。
5. 是否错误使用了 `--no-discovery`。
6. 使用仿真时间时是否已经收到 `/clock`。

### 回放后订阅方收不到消息

检查：

1. 回放的话题是否被 `--topics` 过滤掉。
2. 是否进行了错误重映射。
3. 发布与订阅 QoS 是否兼容。
4. 订阅节点是否在播放开始前准备完成。
5. 节点是否使用了正确命名空间。

可以使用 `--delay` 或 `--start-paused` 给订阅节点留出初始化时间。

### 回放速度或时间行为异常

检查：

- `--rate` 是否被修改。
- 节点使用系统时间还是 ROS 时间。
- 是否使用 `--clock`。
- 节点的 `use_sim_time` 是否为 `true`。
- 算法使用 Bag 记录时间还是消息 `header.stamp`。

### 自定义 Reader 打印的是字节

`read_next()` 返回序列化数据。需要使用消息类型和 `deserialize_message()` 才能获得普通 Python 消息对象。

### 自定义 Reader 读取完成后仍不退出

如果程序读完 Bag 后又进入 `spin()`，进程会继续等待回调。是否自动退出取决于程序控制流程，与 Reader 是否已经到达末尾是两件事。

### Bag 找不到

自定义代码使用相对路径时，路径相对于启动命令的当前工作目录，而不是相对于源文件或功能包目录。

检查：

```bash
pwd
ls
```

### 元数据缺失

先确认 `.db3` 文件是否存在，再尝试：

```bash
ros2 bag reindex <bag_directory>
```

### Conda 导致构建异常

如果 ROS 2 构建过程错误地使用 Conda Python，并出现 `catkin_pkg` 等依赖缺失，可以先执行：

```bash
conda deactivate
source /opt/ros/humble/setup.bash
```

然后重新构建工作空间。

## 31. 数据管理建议

Bag 文件通常很大，不建议无规划地提交到 Git 仓库。

建议：

- 在 `.gitignore` 中忽略本地 Bag 目录和大型数据库文件。
- 使用日期、机器人、场景和任务命名。
- 为关键数据记录 README 或元数据说明。
- 保存对应代码提交哈希和配置版本。
- 重要数据至少保留一份独立备份。
- 上传或共享前检查隐私和敏感信息。

推荐命名示例：

```text
2026-08-03_robot01_lab_navigation_failure_01/
```

配套说明可以记录：

```text
录制时间
机器人编号
测试场景
启动命令
代码提交
参数配置
已知问题
关键时间点
```

## 32. 学习仓库中的对应示例

本仓库提供两套编程 API 示例：

| 功能包 | 语言 | Bag 目录 | 主要内容 |
| --- | --- | --- | --- |
| `learning_rosbag_cpp` | C++ | `my_bag_cpp` | Writer 录制序列化消息，Reader 还原并打印 `Twist` 字段 |
| `learning_rosbag_py` | Python | `my_bag_py` | SequentialWriter 序列化写入，SequentialReader 打印原始记录 |

两个示例都围绕：

```text
/turtle1/cmd_vel
geometry_msgs/msg/Twist
```

它们用于理解 API，不等同于功能完整的 `ros2 bag record` 和 `ros2 bag play`。

## 33. 复习速查表

### 日常必会命令

```bash
# 录制指定话题
ros2 bag record -o my_bag /topic1 /topic2

# 录制全部话题
ros2 bag record -a -o my_bag

# 查看 Bag 信息
ros2 bag info my_bag

# 回放
ros2 bag play my_bag

# 两倍速回放
ros2 bag play my_bag --rate 2.0

# 循环回放
ros2 bag play my_bag --loop

# 只回放指定话题
ros2 bag play my_bag --topics /topic1

# 回放时重映射
ros2 bag play my_bag --remap /old_topic:=/new_topic

# 修复元数据
ros2 bag reindex my_bag
```

### 必须记住

```text
Recorder / Writer 负责写入
Reader 负责读取
Player 负责按时间重新发布
metadata.yaml 保存 Bag 元数据
SQLite3 数据通常保存在 .db3 文件
消息写入前需要序列化
话题名称、类型、时间戳必须对应
QoS 不兼容会导致录不到或收不到消息
```

### 标准排查顺序

```text
1. ros2 topic list
2. ros2 topic type /topic
3. ros2 topic echo /topic
4. ros2 topic info /topic --verbose
5. 开始录制并正常 Ctrl+C 结束
6. ros2 bag info <bag>
7. 启动订阅方后再回放
8. 检查话题名称、重映射、QoS 和时间设置
```

### 一句话总结

```text
Rosbag2 把 ROS 2 消息连同话题元数据和时间信息保存下来，使机器人运行过程能够被检查、分析和重新发布。
```
