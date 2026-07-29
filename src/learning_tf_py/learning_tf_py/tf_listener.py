import rclpy
from rclpy.node import Node
from rclpy.time import Time
from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener
from geometry_msgs.msg import TransformStamped

class TfListener(Node):
    def __init__(self):
        super().__init__("tf_listener_py")
        self.get_logger().info("坐标系监听方创建成功!(Python)")
        self.buffer_ = Buffer()
        self.listener_ = TransformListener(self.buffer_, self)
        self.timer_ = self.create_timer(1.0, self.timer_callback)

    def timer_callback(self):
        if self.buffer_.can_transform("camera", "laser", Time()):
            transform: TransformStamped = self.buffer_.lookup_transform("camera", "laser", Time())
            self.get_logger().info("---------转换成功----------")
            self.get_logger().info(
                f"target_frame: {transform.header.frame_id} "
                f"source_frame: {transform.child_frame_id} "
                f"[x: {transform.transform.translation.x}"
                f" y: {transform.transform.translation.y}"
                f" z: {transform.transform.translation.z}]"
            )
        else:
            self.get_logger().warn("转换异常!")

def main():
    rclpy.init()
    listener = TfListener()
    try:
        rclpy.spin(listener)
    except KeyboardInterrupt:
        pass
    finally:
        listener.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == "__main__":
    main()