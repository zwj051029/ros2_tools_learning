"""  
    需求：读取 bag 文件数据。
    步骤：
        1.导包；
        2.初始化 ROS 客户端；
        3.定义节点类；
            3-1.创建读取对象；
            3-2.设置读取的目标文件、话题等参数；
            3-3.读消息；
            3-4.关闭文件。
        4.调用 spin 函数，并传入对象；
        5.释放资源。

"""
# 1.导包；
import rclpy
from rclpy.node import Node
import rosbag2_py
from rclpy.logging import get_logger
# 3.定义节点类；
class SimpleBagPlayer(Node):
    def __init__(self):
        super().__init__('simple_bag_player_py')
        # 3-1.创建读取对象；
        self.reader = rosbag2_py.SequentialReader()
        # 3-2.设置读取的目标文件、话题等参数；
        storage_options = rosbag2_py._storage.StorageOptions(
                uri="my_bag_py",
                storage_id='sqlite3')
        converter_options = rosbag2_py._storage.ConverterOptions('', '')
        self.reader.open(storage_options,converter_options)

    def read(self):    
        # 3-3.读消息；
        while self.reader.has_next():
            msg = self.reader.read_next()
            get_logger("rclpy").info("topic = %s, time = %d, value=%s" % (msg[0], msg[2], msg[1]))

def main(args=None):
    # 2.初始化 ROS 客户端；
    rclpy.init(args=args)

    # 4.调用 spin 函数，并传入对象；
    reader = SimpleBagPlayer()
    reader.read()
    rclpy.spin(reader)
    # 5.释放资源。
    rclpy.shutdown()


if __name__ == '__main__':
    main()