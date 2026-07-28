import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PointStamped

class PointPublisher(Node):
    def __init__(self):
        super().__init__("point_publisher_py")
        self.get_logger().info("坐标点发布方创建成功!(Python)")
        self.x_ = 0.0
        self.publisher_ = self.create_publisher(PointStamped, "point", 10)
        self.timer_ = self.create_timer(1.0, self.timer_callback)

    def timer_callback(self):
        msg = PointStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "laser"
        msg.point.x = self.x_
        msg.point.y = 0.0
        msg.point.z = 0.3
        self.x_ += 0.05
        self.publisher_.publish(msg)

def main():
    rclpy.init()
    node = PointPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == "__main__":
    main()