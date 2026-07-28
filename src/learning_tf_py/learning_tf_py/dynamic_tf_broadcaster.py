import rclpy
from rclpy.node import Node
from tf2_ros import TransformBroadcaster
from turtlesim.msg import Pose
from geometry_msgs.msg import TransformStamped
import tf_transformations

class DynamicTfBroadcaster(Node):
    def __init__(self):
        super().__init__("dynamic_tf_broadcaster_py")
        self.get_logger().info("动态坐标广播方创建成功!")
        self.broadcaster_ = TransformBroadcaster(self)
        self.subscriber_ = self.create_subscription(
            Pose, "/turtle1/pose", self.turtle_pose_callback, 10
        )

    def turtle_pose_callback(self, pose: Pose):
        qtn = tf_transformations.quaternion_from_euler(
            0.0, 0.0, pose.theta
        )

        transform = TransformStamped()
        transform.header.stamp = self.get_clock().now().to_msg()
        transform.header.frame_id = "world"
        transform.child_frame_id = "turtle1"
        transform.transform.translation.x = pose.x
        transform.transform.translation.y = pose.y
        transform.transform.translation.z = 0.0
        transform.transform.rotation.x = qtn[0]
        transform.transform.rotation.y = qtn[1]
        transform.transform.rotation.z = qtn[2]
        transform.transform.rotation.w = qtn[3]
        
        self.broadcaster_.sendTransform(transform)

def main():
    rclpy.init()
    node = DynamicTfBroadcaster()
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