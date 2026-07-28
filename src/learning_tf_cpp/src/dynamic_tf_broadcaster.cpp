#include "rclcpp/rclcpp.hpp"
#include "tf2_ros/transform_broadcaster.hpp"
#include "turtlesim/msg/pose.hpp"
#include "geometry_msgs/msg/transform_stamped.hpp"
#include "tf2/LinearMath/Quaternion.hpp"

using turtlesim::msg::Pose;
using std::placeholders::_1;

class DynamicTfBroadcaster : public rclcpp::Node {
public:
    DynamicTfBroadcaster() : Node("dynamic_tf_broadcaster_cpp") {
        RCLCPP_INFO(this->get_logger(), "动态坐标广播方创建成功!");
        broadcaster_ = std::make_shared<tf2_ros::TransformBroadcaster>(this);
        subscriber_ = this->create_subscription<Pose>(
            "/turtle1/pose", 10,
            std::bind(&DynamicTfBroadcaster::turtle_pose_callback, this, _1)
        );
    }

private:
    void turtle_pose_callback(const Pose::SharedPtr pose_msg) {
        auto qtn = tf2::Quaternion();
        qtn.setRPY(0.0, 0.0, pose_msg->theta);

        auto transform = geometry_msgs::msg::TransformStamped();
        transform.header.stamp = this->now();
        transform.header.frame_id = "world";
        transform.child_frame_id = "turtle1";
        transform.transform.translation.x = pose_msg->x;
        transform.transform.translation.y = pose_msg->y;
        transform.transform.translation.z = 0.0;
        transform.transform.rotation.x = qtn.getX();
        transform.transform.rotation.y = qtn.getY();
        transform.transform.rotation.z = qtn.getZ();
        transform.transform.rotation.w = qtn.getW();

        /*
            void sendTransform(const geometry_msgs::msg::TransformStamped &transform)
        */
        broadcaster_->sendTransform(transform);
    }

    std::shared_ptr<tf2_ros::TransformBroadcaster> broadcaster_;
    rclcpp::Subscription<Pose>::SharedPtr subscriber_;
};

int main(int argc, char **argv) {
    rclcpp::init(argc, argv);
    auto node = std::make_shared<DynamicTfBroadcaster>();
    rclcpp::spin(node);
    rclcpp::shutdown();

    return 0;
}