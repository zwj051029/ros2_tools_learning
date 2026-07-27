"""  
  需求：录制 turtle_teleop_key 节点发布的速度指令。
  步骤：
    1.导包；
    2.初始化 ROS 客户端；
    3.定义节点类；
      3-1.创建写出对象；
      3-2.设置写出的目标文件、话题等参数；
      3-3.写出消息。
    4.调用 spin 函数，并传入对象；
    5.释放资源。

"""
# 1.导包；
import rclpy
from rclpy.node import Node
from rclpy.serialization import serialize_message
from geometry_msgs.msg import Twist
import rosbag2_py
# 3.定义节点类；
class SimpleBagRecorder(Node):
    def __init__(self):
        super().__init__('simple_bag_recorder_py')
        # 3-1.创建写出对象；
        self.writer = rosbag2_py.SequentialWriter()
        # 3-2.设置写出的目标文件、话题等参数；
        storage_options = rosbag2_py._storage.StorageOptions(
            uri='my_bag_py',
            storage_id='sqlite3')
        converter_options = rosbag2_py._storage.ConverterOptions('', '')
        self.writer.open(storage_options, converter_options)

        topic_info = rosbag2_py._storage.TopicMetadata(
            name='/turtle1/cmd_vel',
            type='geometry_msgs/msg/Twist',
            serialization_format='cdr')
        self.writer.create_topic(topic_info)

        self.subscription = self.create_subscription(
            Twist,
            '/turtle1/cmd_vel',
            self.topic_callback,
            10)
        self.subscription

    def topic_callback(self, msg):
        # 3-3.写出消息。
        self.writer.write(
            '/turtle1/cmd_vel',
            serialize_message(msg),
            self.get_clock().now().nanoseconds)


def main(args=None):
    # 2.初始化 ROS 客户端；
    rclpy.init(args=args)
    # 4.调用 spin 函数，并传入对象；
    sbr = SimpleBagRecorder()
    rclpy.spin(sbr)
    # 5.释放资源。
    rclpy.shutdown()


if __name__ == '__main__':
    main()