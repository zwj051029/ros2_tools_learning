import sys
import rclpy
import tf_transformations
from rclpy.node import Node
from rclpy.logging import get_logger
from tf2_ros.static_transform_broadcaster import StaticTransformBroadcaster
from geometry_msgs.msg import TransformStamped

class StaticTfBroadcaster(Node):
    def __init__(self, argv):
        super().__init__("static_tf_broadcaster_py")
        self.get_logger().info("静态广播方创建成功!(Python)")
        self.broadcaster_ = StaticTransformBroadcaster(self)
        self.publish_transform(argv)

    def publish_transform(self, argv):
        qtn = tf_transformations.quaternion_from_euler(
            float(argv[4]),
            float(argv[5]),
            float(argv[6])
        )

        transform = TransformStamped()
        transform.header.stamp = self.get_clock().now().to_msg()
        transform.header.frame_id = argv[7]
        transform.child_frame_id = argv[8]
        transform.transform.translation.x = float(argv[1])
        transform.transform.translation.y = float(argv[2])
        transform.transform.translation.z = float(argv[3])
        transform.transform.rotation.x = qtn[0]
        transform.transform.rotation.y = qtn[1]
        transform.transform.rotation.z = qtn[2]
        transform.transform.rotation.w = qtn[3]

        self.broadcaster_.sendTransform(transform)
        self.get_logger().info("静态坐标发布成功!")

def main():
    if len(sys.argv) != 9:
        get_logger("rclpy").error("输入参数数目不合法!")
        if rclpy.ok():
            rclpy.shutdown()
        return

    rclpy.init()
    node = StaticTfBroadcaster(sys.argv)
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