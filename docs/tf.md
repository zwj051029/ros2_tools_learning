# ROS 2 TF2 坐标变换知识点总结

## 1. 为什么需要 TF2

机器人系统中会同时存在许多坐标系，例如：

```text
map                 地图坐标系
odom                里程计坐标系
base_footprint      机器人在地面的投影坐标系
base_link           机器人底盘坐标系
camera_link         相机安装坐标系
camera_optical_frame 相机光学坐标系
laser               激光雷达坐标系
imu_link            IMU 坐标系
```

同一个物体在不同坐标系中的坐标不同。例如，激光雷达测得障碍点 `(1.0, 0.0, 0.0)`，只表示这个点位于雷达前方 1 米，并不能直接说明它在底盘或地图中的位置。

TF2 负责维护各坐标系之间随时间变化的关系，并提供统一的坐标转换能力。

它解决的核心问题是：

```text
某个时刻，坐标系 A 与坐标系 B 是什么关系？
如何把 B 中表达的数据转换成 A 中的表达？
```

TF2 常用于：

- 将传感器数据转换到机器人底盘坐标系。
- 将机器人局部观测转换到地图坐标系。
- 发布机器人各部件之间的安装关系。
- 表示机器人、机械臂关节和移动目标的实时姿态。
- 为 RViz、导航、定位和感知算法提供统一坐标基础。

## 2. TF2 与普通话题通信的区别

TF2 底层同样使用 ROS 2 话题传递数据，但它不是普通的“收到一条消息就处理一条消息”模式。

| 对比项 | 普通话题 | TF2 |
| --- | --- | --- |
| 主要内容 | 业务消息 | 坐标系之间的变换 |
| 数据组织 | 按话题独立传输 | 按坐标树和时间缓存 |
| 查询方式 | 订阅回调 | 根据目标、源和时间查询 |
| 多段关系 | 业务代码自行处理 | TF2 自动组合坐标链 |
| 历史数据 | 由节点自行保存 | Buffer 保存一定时间窗口 |

TF2 适合表达“坐标系关系”，不适合代替普通传感器话题。大量点云、图像或检测目标仍应通过对应消息发布，只在消息的 `header.frame_id` 中说明它属于哪个坐标系。

## 3. 坐标系树

TF2 将坐标系组织为一棵树：

```text
map
└── odom
    └── base_footprint
        └── base_link
            ├── laser
            ├── camera_link
            │   └── camera_optical_frame
            └── imu_link
```

树结构具有以下约束：

- 一个坐标系可以有多个子坐标系。
- 每个非根坐标系只能有一个直接父坐标系。
- 整棵树不能形成环。
- 两个坐标系必须位于同一棵树中才能互相转换。
- 同一个 `child_frame_id` 不应由多个来源发布不同的父子关系。

TF2 可以自动组合多段变换。例如已知：

```text
map -> odom
odom -> base_link
base_link -> laser
```

就可以查询：

```text
laser -> map
map -> laser
odom -> laser
```

## 4. 父坐标系与子坐标系

`geometry_msgs/msg/TransformStamped` 是 TF2 最常用的变换消息。

```text
header.frame_id  父坐标系
child_frame_id   子坐标系
transform        子坐标系相对于父坐标系的位姿
```

示例：

```cpp
transform.header.frame_id = "base_link";
transform.child_frame_id = "laser";
transform.transform.translation.x = 0.4;
transform.transform.translation.y = 0.0;
transform.transform.translation.z = 0.2;
```

表示：

```text
laser 是 base_link 的子坐标系
laser 原点在 base_link 中的位置为 (0.4, 0.0, 0.2)
```

可以把它理解为“子坐标系在父坐标系中的安装位姿”。

## 5. 变换方向

TF2 最容易出错的地方是方向。

### 广播时的问题

```text
子坐标系相对于父坐标系在哪里？
```

### 转换数据时的问题

```text
数据当前属于哪个源坐标系？
希望转换到哪个目标坐标系？
```

查询 API 的常见顺序：

```text
lookupTransform(target_frame, source_frame, time)
lookup_transform(target_frame, source_frame, time)
```

它获得的是：

```text
把 source_frame 中的数据转换到 target_frame 所需的变换
```

例如：

```cpp
buffer.lookupTransform("base_link", "laser", tf2::TimePointZero);
```

含义是查询如何把 `laser` 中的数据转换到 `base_link`。

### `tf2_echo` 的参数

Humble 中命令格式为：

```bash
ros2 run tf2_ros tf2_echo <source_frame> <target_frame>
```

常用示例：

```bash
ros2 run tf2_ros tf2_echo base_link laser
```

Humble 的帮助信息将两个位置参数称为 `source_frame` 和 `target_frame`。需要特别注意：该命令的输出可用于把第二个参数坐标系中的数据转换到第一个参数坐标系。上面的命令因此显示 `laser` 相对于 `base_link` 的位姿。

### 快速判断方法

看到：

```text
base_link -> laser
```

应先读成：

```text
laser 的父坐标系是 base_link
laser 的安装位姿在 base_link 中表达
```

不要只依赖箭头直觉，应回到 `header.frame_id` 和 `child_frame_id` 判断。

## 6. 坐标变换数学基础

刚体变换由两部分组成：

```text
平移 t
旋转 R
```

把坐标系 B 中的点转换到坐标系 A：

```text
p_A = R_A_B * p_B + t_A_B
```

其中：

- `p_B`：点在 B 中的坐标。
- `R_A_B`：B 相对于 A 的旋转。
- `t_A_B`：B 原点在 A 中的位置。
- `p_A`：点转换到 A 后的坐标。

反向变换：

```text
p_B = R_A_B^T * (p_A - t_A_B)
```

多段变换组合：

```text
T_A_C = T_A_B * T_B_C
```

TF2 会负责求逆和链式组合，业务代码通常不需要手工计算矩阵。

## 7. ROS 坐标约定

机器人常用的机体坐标约定为右手坐标系：

```text
X 轴向前
Y 轴向左
Z 轴向上
```

角度正方向遵循右手定则。

常见单位：

```text
距离：米
角度：弧度
时间：秒或纳秒
```

相机光学坐标系通常采用：

```text
X 轴向右
Y 轴向下
Z 轴向前
```

因此相机驱动常同时提供 `camera_link` 和 `camera_optical_frame`，二者之间通过固定 TF 连接。

## 8. 平移与旋转字段

`TransformStamped` 中的核心字段：

```text
transform.translation.x
transform.translation.y
transform.translation.z

transform.rotation.x
transform.rotation.y
transform.rotation.z
transform.rotation.w
```

旋转使用四元数，而不是直接使用 Roll、Pitch、Yaw。

四元数优点：

- 避免欧拉角万向节锁问题。
- 适合连续旋转插值。
- 组合计算稳定。

有效旋转四元数应保持归一化：

```text
x^2 + y^2 + z^2 + w^2 = 1
```

## 9. RPY 与四元数转换

RPY 含义：

```text
Roll   绕 X 轴旋转
Pitch  绕 Y 轴旋转
Yaw    绕 Z 轴旋转
```

输入单位是弧度。

### C++

```cpp
#include "tf2/LinearMath/Quaternion.h"

tf2::Quaternion quaternion;
quaternion.setRPY(roll, pitch, yaw);

transform.transform.rotation.x = quaternion.x();
transform.transform.rotation.y = quaternion.y();
transform.transform.rotation.z = quaternion.z();
transform.transform.rotation.w = quaternion.w();
```

### Python

```python
import tf_transformations

quaternion = tf_transformations.quaternion_from_euler(
    roll,
    pitch,
    yaw
)

transform.transform.rotation.x = quaternion[0]
transform.transform.rotation.y = quaternion[1]
transform.transform.rotation.z = quaternion[2]
transform.transform.rotation.w = quaternion[3]
```

常见换算：

```text
90 度  = 1.5708 弧度
180 度 = 3.1416 弧度
```

## 10. 静态 TF

静态 TF 用于描述运行期间不会改变的安装关系，例如：

- 底盘到激光雷达。
- 底盘到相机。
- 相机安装坐标系到光学坐标系。
- 底盘到 IMU。
- URDF 中的固定关节。

静态变换发布到：

```text
/tf_static
```

它使用适合静态数据的 QoS，使后启动的监听器也能获得已有变换。

## 11. 使用命令发布静态 TF

Humble 推荐使用具名参数：

```bash
ros2 run tf2_ros static_transform_publisher \
  --x 0.4 \
  --y 0.0 \
  --z 0.2 \
  --roll 0.0 \
  --pitch 0.0 \
  --yaw 0.0 \
  --frame-id base_link \
  --child-frame-id laser
```

如果不提供平移和旋转，默认发布单位变换。

也可以直接使用四元数：

```bash
ros2 run tf2_ros static_transform_publisher \
  --x 0.4 --y 0.0 --z 0.2 \
  --qx 0.0 --qy 0.0 --qz 0.0 --qw 1.0 \
  --frame-id base_link \
  --child-frame-id laser
```

欧拉角和四元数应选择一种方式提供，不要混合出含义不清的旋转配置。

## 12. C++ 静态广播

```cpp
#include "geometry_msgs/msg/transform_stamped.hpp"
#include "tf2_ros/static_transform_broadcaster.h"

class StaticBroadcaster : public rclcpp::Node {
public:
    StaticBroadcaster() : Node("static_broadcaster") {
        broadcaster_ =
            std::make_shared<tf2_ros::StaticTransformBroadcaster>(this);

        geometry_msgs::msg::TransformStamped transform;
        transform.header.stamp = now();
        transform.header.frame_id = "base_link";
        transform.child_frame_id = "laser";
        transform.transform.translation.x = 0.4;
        transform.transform.translation.y = 0.0;
        transform.transform.translation.z = 0.2;
        transform.transform.rotation.w = 1.0;

        broadcaster_->sendTransform(transform);
    }

private:
    std::shared_ptr<tf2_ros::StaticTransformBroadcaster> broadcaster_;
};
```

即使只发送一次，节点通常仍保持运行，便于管理其生命周期和观察日志。

## 13. Python 静态广播

```python
from geometry_msgs.msg import TransformStamped
from tf2_ros.static_transform_broadcaster import StaticTransformBroadcaster

self.broadcaster = StaticTransformBroadcaster(self)

transform = TransformStamped()
transform.header.stamp = self.get_clock().now().to_msg()
transform.header.frame_id = 'base_link'
transform.child_frame_id = 'laser'
transform.transform.translation.x = 0.4
transform.transform.translation.y = 0.0
transform.transform.translation.z = 0.2
transform.transform.rotation.w = 1.0

self.broadcaster.sendTransform(transform)
```

## 14. 动态 TF

动态 TF 用于描述随时间变化的关系，例如：

- `odom -> base_link`。
- 地图定位输出的 `map -> odom`。
- 移动目标的位置。
- 机械臂活动关节。
- 小乌龟在 `world` 中的位置。

动态变换发布到：

```text
/tf
```

动态广播需要持续更新，且每条变换都应带有正确时间戳。

## 15. C++ 动态广播

```cpp
#include "tf2_ros/transform_broadcaster.hpp"

broadcaster_ =
    std::make_shared<tf2_ros::TransformBroadcaster>(this);

geometry_msgs::msg::TransformStamped transform;
transform.header.stamp = now();
transform.header.frame_id = "world";
transform.child_frame_id = "robot";
transform.transform.translation.x = x;
transform.transform.translation.y = y;
transform.transform.translation.z = 0.0;
transform.transform.rotation = quaternion_msg;

broadcaster_->sendTransform(transform);
```

动态广播通常在以下位置触发：

- 位姿订阅回调。
- 里程计更新回调。
- 固定频率定时器。
- 控制循环或状态估计循环。

## 16. Python 动态广播

```python
from tf2_ros import TransformBroadcaster

self.broadcaster = TransformBroadcaster(self)

transform = TransformStamped()
transform.header.stamp = self.get_clock().now().to_msg()
transform.header.frame_id = 'world'
transform.child_frame_id = 'robot'
# 设置平移和旋转
self.broadcaster.sendTransform(transform)
```

不要在高频循环中无意义地重复发布完全不变的安装关系，这类关系应使用静态 TF。

## 17. 时间戳的重要性

TF2 维护的是：

```text
坐标关系 + 时间
```

动态系统中，机器人在不同时间的位置不同。因此查询时不仅要说明目标和源坐标系，还要说明希望使用哪个时刻的变换。

消息中常见：

```text
header.stamp
header.frame_id
```

- `frame_id` 表明数据属于哪个坐标系。
- `stamp` 表明数据对应哪个时刻。

处理传感器消息时，通常应使用消息自己的时间戳查询 TF，而不是无条件使用“当前时间”。否则高速运动或存在通信延迟时会引入空间误差。

## 18. 最新变换与指定时刻变换

### C++ 查询最新变换

```cpp
buffer_->lookupTransform(
    "base_link",
    "laser",
    tf2::TimePointZero
);
```

`tf2::TimePointZero` 表示查询最新可用变换。

### Python 查询最新变换

```python
from rclpy.time import Time

transform = buffer.lookup_transform(
    'base_link',
    'laser',
    Time()
)
```

空的 `Time()` 表示零时间，也就是最新可用变换。

### 指定消息时间查询

概念上应使用：

```text
target_frame
source_frame
message.header.stamp
```

如果对应时刻超出 Buffer 保存范围，会出现外推异常。

## 19. Buffer 与 TransformListener

监听端通常需要两个对象：

```text
Buffer             存储并查询坐标变换
TransformListener  订阅 TF 话题并填充 Buffer
```

### C++

```cpp
buffer_ = std::make_unique<tf2_ros::Buffer>(get_clock());
listener_ = std::make_shared<tf2_ros::TransformListener>(
    *buffer_,
    this
);
```

### Python

```python
from tf2_ros import Buffer, TransformListener

self.buffer = Buffer()
self.listener = TransformListener(self.buffer, self)
```

Listener 必须保持存活。如果只创建临时局部对象并立即销毁，Buffer 将无法持续接收 TF。

## 20. 查询变换

### C++

```cpp
try {
    auto transform = buffer_->lookupTransform(
        "camera",
        "laser",
        tf2::TimePointZero
    );
} catch (const tf2::TransformException &error) {
    RCLCPP_WARN(get_logger(), "%s", error.what());
}
```

工程中通常捕获基类 `tf2::TransformException`，以覆盖查找、连接和外推等变换异常。

### Python

```python
from rclpy.time import Time

if self.buffer.can_transform('camera', 'laser', Time()):
    transform = self.buffer.lookup_transform(
        'camera',
        'laser',
        Time()
    )
```

也可以使用异常处理。`can_transform()` 适合先判断变换是否可用，但系统状态可能在判断后发生变化，关键代码仍应正确处理查询失败。

## 21. 常见 TF 异常

### LookupException

目标或源坐标系尚未出现在 Buffer 中，常见原因：

- 广播节点未启动。
- frame ID 拼写错误。
- Listener 刚启动，还没收到 TF。

### ConnectivityException

两个坐标系都存在，但不在同一棵连通的 TF 树中。

例如：

```text
tree 1: map -> base_link
tree 2: camera -> laser
```

### ExtrapolationException

请求的时间早于或晚于 Buffer 可提供的时间范围。

常见原因：

- 使用当前时间查询，但最新 TF 还没到达。
- 传感器消息时间和 TF 时间源不一致。
- 系统时间与仿真时间混用。
- 查询很久以前的历史数据。

### InvalidArgumentException

参数或 frame ID 不合法，例如空坐标系名称。

## 22. 等待变换

TF 数据通过通信异步到达。Listener 创建后立即查询，第一次查询失败是正常现象。

可采用：

- 周期定时器重复查询。
- `canTransform()` 或 `can_transform()`。
- 带超时时间的查询。
- `tf2_ros::MessageFilter`。

不要用无限循环持续查询而不让执行器处理回调，否则 Listener 可能永远没有机会接收 TF。

## 23. 带坐标系的数据

TF2 通常处理带 `Header` 的消息，例如：

- `geometry_msgs/msg/PointStamped`
- `geometry_msgs/msg/PoseStamped`
- `geometry_msgs/msg/Vector3Stamped`
- `geometry_msgs/msg/TransformStamped`
- `sensor_msgs/msg/PointCloud2`

以 `PointStamped` 为例：

```cpp
geometry_msgs::msg::PointStamped point;
point.header.stamp = now();
point.header.frame_id = "laser";
point.point.x = 1.0;
point.point.y = 0.0;
point.point.z = 0.0;
```

如果缺少正确的 `frame_id` 和时间戳，TF2 无法判断该点应该使用哪条坐标关系。

## 24. C++ 转换几何数据

引入类型支持：

```cpp
#include "tf2_geometry_msgs/tf2_geometry_msgs.hpp"
```

执行转换：

```cpp
geometry_msgs::msg::PointStamped output;

try {
    output = buffer_->transform(input, "base_link");
} catch (const tf2::TransformException &error) {
    RCLCPP_WARN(get_logger(), "%s", error.what());
}
```

`input.header.frame_id` 是源坐标系，`base_link` 是目标坐标系。

## 25. Python 转换几何数据

Python 中使用相同概念：

```python
import tf2_geometry_msgs

try:
    output = self.buffer.transform(
        input_point,
        'base_link'
    )
except Exception as error:
    self.get_logger().warn(str(error))
```

`tf2_geometry_msgs` 的导入会注册相关几何消息类型的转换支持。实际工程中应捕获 TF2 对应异常，并根据数据重要性决定丢弃、等待或重试。

## 26. MessageFilter

普通订阅回调可能先收到传感器消息，但对应时间的 TF 还没到达。如果立即转换，就会失败。

`tf2_ros::MessageFilter` 用于协调：

```text
消息已到达
        +
对应时间的目标坐标变换已可用
        ↓
才调用业务回调
```

典型结构：

```text
message_filters::Subscriber
            │
            ▼
tf2_ros::MessageFilter
            │ 等待 TF
            ▼
业务变换回调
```

它适合相机、激光雷达、点云等带时间戳的高频数据。

需要合理设置：

- 目标坐标系。
- 消息队列长度。
- 等待超时。
- Buffer 时间窗口。

队列过小可能丢弃等待中的消息；队列过大则增加内存和处理延迟。

## 27. 静态点变换示例

已知：

```text
base_link -> laser
translation = (0.4, 0.0, 0.2)
rotation    = identity
```

`laser` 中的点：

```text
(0.0, 0.0, -0.5)
```

因为没有旋转，所以只需加上平移：

```text
x = 0.0 + 0.4 = 0.4
y = 0.0 + 0.0 = 0.0
z = -0.5 + 0.2 = -0.3
```

转换到 `base_link` 后：

```text
(0.4, 0.0, -0.3)
```

如果存在旋转，必须先旋转点再加平移，不能只对三个坐标分量做简单加减。

## 28. `map`、`odom` 与 `base_link`

移动机器人常见坐标链：

```text
map -> odom -> base_link
```

### `map`

- 全局参考坐标系。
- 适合表达机器人在地图中的位置。
- 定位修正可能让 `map -> odom` 出现跳变。

### `odom`

- 局部连续坐标系。
- 通常由轮式里程计、视觉里程计或融合系统维护。
- 短期连续，但长期可能漂移。

### `base_link`

- 固定在机器人本体上的坐标系。
- 机器人运动时，它相对于 `odom` 和 `map` 发生变化。

职责通常为：

```text
定位系统发布 map -> odom
里程计系统发布 odom -> base_link
机器人描述发布 base_link -> sensors
```

不同系统不应重复发布同一段 TF，否则会产生冲突。

## 29. `base_footprint` 与 `base_link`

```text
base_footprint
└── base_link
```

常见理解：

- `base_footprint`：机器人在地面平面上的投影。
- `base_link`：机器人实体底盘参考坐标系，可能离地面有高度。

平面导航常以 `base_footprint` 或 `base_link` 作为机器人参考，具体选择应与整套导航和机器人描述配置一致。

## 30. URDF 与 TF2

URDF 定义机器人 Link 和 Joint 关系，`robot_state_publisher` 根据这些关系发布 TF。

```text
URDF robot_description
        +
/joint_states
        ↓
robot_state_publisher
        ↓
/tf 和 /tf_static
```

- 固定关节通常发布到 `/tf_static`。
- 可运动关节根据 `/joint_states` 计算并发布动态 TF。

因此：

```text
URDF 描述机器人结构
Joint State 描述关节当前状态
TF2 提供当前坐标关系
```

不要同时手工广播和 `robot_state_publisher` 发布完全相同的父子 TF。

## 31. 仿真时间与 TF2

仿真或 Bag 回放时，节点可能使用：

```text
use_sim_time = true
```

此时节点时钟来自 `/clock`。

如果广播方使用仿真时间，监听方使用系统时间，可能出现大量外推错误。参与同一套 TF 查询的节点应使用一致的时间来源。

Bag 回放常见配置：

```bash
ros2 bag play robot_bag --clock
```

并让需要跟随回放时间的节点启用 `use_sim_time`。

## 32. 常用调试工具

### 查看单段或组合变换

```bash
ros2 run tf2_ros tf2_echo base_link laser
```

可选参数：

```text
-r <rate>       输出频率
-t <time>       查询固定时间
-p <precision>  输出小数精度
```

### 查看 TF 话题

```bash
ros2 topic echo /tf
ros2 topic echo /tf_static
```

`/tf` 通常频率较高、内容较多，直接查看适合确认是否有人发布，不适合长期阅读复杂系统全部数据。

### 生成坐标树

```bash
ros2 run tf2_tools view_frames
```

它可以生成当前 TF 树报告，用于检查：

- 根坐标系。
- 父子关系。
- 是否存在断开的子树。
- 广播频率和时间信息。

### RViz2

在 RViz2 中添加 `TF` 显示项，可以直观看到坐标轴、名称和树结构。

显示传感器消息时，RViz 的 Fixed Frame 必须能够连接到消息的 `frame_id`。

### 查看节点发布关系

```bash
ros2 node info /node_name
```

可用于确认节点是否发布 `/tf` 或 `/tf_static`。

## 33. 坐标系命名规范

推荐：

- 使用小写蛇形命名，例如 `base_link`、`camera_link`。
- 名称表达物理含义，不使用 `frame1`、`test2` 等模糊名称。
- 不在 frame ID 前添加 `/`。
- 传感器 Link 与光学坐标系使用明确后缀。
- 多机器人系统通过前缀或命名空间避免冲突。
- 同一项目统一采用一套命名规则。

常见名称：

```text
map
odom
base_footprint
base_link
laser_link
camera_link
camera_color_optical_frame
imu_link
tool0
```

Frame ID 是字符串，但不能“随便写”。广播方和消息发布方必须使用同一套有物理意义且连通的坐标定义。

## 34. 广播频率建议

动态 TF 频率应根据运动速度和下游算法需求决定。

频率过低：

- 运动显示不平滑。
- 高频传感器消息可能找不到对应时间变换。
- 坐标转换误差增大。

频率过高：

- 增加网络和 CPU 负载。
- 重复发布没有实际价值的数据。

原则：

```text
静态关系只使用静态广播
动态关系按实际状态更新频率发布
时间戳必须真实且单调合理
```

## 35. 常见问题

### `frame does not exist`

检查：

1. 广播节点是否运行。
2. frame ID 是否拼写一致。
3. Listener 是否刚启动还未收到数据。
4. 是否加载了正确工作空间。
5. `/tf` 或 `/tf_static` 是否有消息。

### 两棵 TF 树无法连接

使用 `view_frames` 检查断点，找到缺少的父子关系。

不要用一条没有物理依据的 TF 只为了让树“看起来连上”。应确认哪个节点负责发布真实关系。

### Extrapolation into the future

请求时间晚于最新 TF。常见解决方向：

- 检查广播频率。
- 检查消息与 TF 的时间来源。
- 使用正确的消息时间戳。
- 允许执行器先接收最新 TF。
- 必要时使用等待机制或 MessageFilter。

### Extrapolation into the past

请求时间早于 Buffer 中最早数据。可能是消息延迟过大、Buffer 时间窗口不足，或播放数据的时间系统配置错误。

### 点变换结果符号相反

检查：

- 父子坐标系是否写反。
- `lookupTransform()` 的目标和源顺序。
- 传感器安装平移方向。
- 旋转四元数是否正确。
- 是否错误地对变换取了两次逆。

### 静态 TF 发布了但监听不到

检查：

- 是否使用 `/tf_static` 对应的静态广播器。
- frame ID 是否为空或冲突。
- ROS Domain ID 和中间件环境是否一致。
- Listener 是否订阅了正确 ROS 2 图。

### RViz 显示 `No transform`

检查：

```text
RViz Fixed Frame
消息 header.frame_id
TF 树是否连通
消息时间戳
TF 是否覆盖对应时刻
```

### 同一坐标系跳来跳去

通常意味着多个节点正在发布同一个 `child_frame_id`，但父坐标系或数值不同。

通过以下命令检查发布节点：

```bash
ros2 topic info /tf --verbose
ros2 topic info /tf_static --verbose
```

### MessageFilter 没有触发回调

检查：

- 输入消息是否到达。
- `header.frame_id` 是否正确。
- 目标坐标系是否存在。
- 对应消息时间的 TF 是否可用。
- 队列是否过小。
- 等待超时是否过短。

## 36. 工程设计建议

### 明确每段 TF 的唯一负责人

维护一张表：

| 父坐标系 | 子坐标系 | 类型 | 发布者 |
| --- | --- | --- | --- |
| `map` | `odom` | 动态 | 定位节点 |
| `odom` | `base_link` | 动态 | 里程计或状态估计节点 |
| `base_link` | `laser` | 静态 | URDF 或静态广播节点 |

### 传感器消息使用采样时间

不要在处理回调中随意把消息时间戳改成当前时间来绕过 TF 错误。这样可能让转换成功，但空间结果对应了错误时刻。

### 优先使用 URDF 管理机器人本体结构

机器人固定部件较多时，使用 URDF/Xacro 和 `robot_state_publisher` 比编写许多独立静态广播节点更容易维护。

### 对异步数据使用 MessageFilter

高频传感器数据不应靠不断 `try/catch` 和立即丢弃来处理时序问题。MessageFilter 能更明确地等待所需 TF。

### 记录 TF 数据

使用 Rosbag2 记录传感器数据时，通常同时记录：

```text
/tf
/tf_static
```

否则离线回放时可能无法完成坐标转换。

## 37. 学习仓库中的对应示例

### C++ 功能包

`learning_tf_cpp` 包含：

| 节点 | 作用 |
| --- | --- |
| `static_tf_broadcaster` | 根据参数发布静态 TF |
| `dynamic_tf_broadcaster` | 根据小乌龟位姿发布 `world -> turtle1` |
| `tf_listener` | 查询 `laser` 到 `camera` 的变换 |
| `point_publisher` | 发布 `laser` 中的 `PointStamped` |
| `point_transformer` | 使用 MessageFilter 变换到 `base_link` |

### Python 功能包

`learning_tf_py` 包含：

| 节点 | 作用 |
| --- | --- |
| `static_tf_broadcaster` | Python 静态广播 |
| `dynamic_tf_broadcaster` | Python 动态广播 |
| `tf_listener` | 使用 `can_transform()` 后查询变换 |
| `point_publisher` | 发布 `laser` 中的 `PointStamped` |

Python 发布的点可以由 C++ `point_transformer` 订阅并转换，体现 ROS 2 消息接口与编程语言解耦。

## 38. 完整练习命令

### 静态 TF 与点变换

终端 1：

```bash
source install/setup.bash
ros2 run learning_tf_cpp static_tf_broadcaster \
  0.4 0 0.2 0 0 0 base_link laser
```

终端 2：

```bash
source install/setup.bash
ros2 run learning_tf_cpp point_publisher
```

终端 3：

```bash
source install/setup.bash
ros2 run learning_tf_cpp point_transformer
```

预期首个输出：

```text
frame_id: base_link, [0.40, 0.00, -0.30]
```

### 动态 TF

终端 1：

```bash
ros2 run turtlesim turtlesim_node
```

终端 2：

```bash
ros2 run turtlesim turtle_teleop_key
```

终端 3：

```bash
source install/setup.bash
ros2 run learning_tf_cpp dynamic_tf_broadcaster
```

终端 4：

```bash
ros2 run tf2_ros tf2_echo world turtle1
```

移动小乌龟时，变换数据应持续变化。

## 39. 复习速查表

### 必须记住的消息字段

```text
header.stamp       变换对应时间
header.frame_id    父坐标系
child_frame_id     子坐标系
translation       子坐标系在父坐标系中的平移
rotation          子坐标系在父坐标系中的旋转四元数
```

### 必须记住的 API

```text
StaticTransformBroadcaster  发布静态 TF
TransformBroadcaster        发布动态 TF
Buffer                      缓存并查询 TF
TransformListener           接收 TF 并填充 Buffer
lookupTransform             查询坐标关系
transform                   转换几何数据
MessageFilter               等待消息对应时间的 TF
```

### 必须分清

```text
广播：子坐标系相对于父坐标系的位姿
查询：把源坐标系中的数据转换到目标坐标系

/tf         动态变换
/tf_static  静态变换

frame_id        数据属于哪个坐标系
stamp           数据属于哪个时刻
```

### 常用命令

```bash
# 发布静态 TF
ros2 run tf2_ros static_transform_publisher \
  --x 0.4 --y 0 --z 0.2 \
  --roll 0 --pitch 0 --yaw 0 \
  --frame-id base_link \
  --child-frame-id laser

# 查看变换
ros2 run tf2_ros tf2_echo base_link laser

# 生成 TF 树
ros2 run tf2_tools view_frames

# 查看 TF 话题
ros2 topic echo /tf
ros2 topic echo /tf_static
```

### 标准排查顺序

```text
1. 检查广播节点是否运行
2. 检查 /tf 和 /tf_static 是否有数据
3. 核对 frame ID 拼写和父子关系
4. 使用 tf2_echo 查询目标关系
5. 使用 view_frames 检查树是否连通
6. 核对消息 header.frame_id 和 header.stamp
7. 核对系统时间、仿真时间和 Buffer 时间范围
8. 检查是否有多个节点重复发布同一子坐标系
```

### 一句话总结

```text
TF2 维护“坐标系之间随时间变化的关系”，让带有 frame_id 和时间戳的数据能够被正确转换到目标坐标系。
```
