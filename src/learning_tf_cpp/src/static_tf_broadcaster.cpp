#include "geometry_msgs/msg/transform_stamped.hpp"
#include "rclcpp/rclcpp.hpp"
#include "tf2_ros/static_transform_broadcaster.h"
#include "tf2/LinearMath/Quaternion.h"

using geometry_msgs::msg::TransformStamped;

class StaticTfBroadcaster : public rclcpp::Node {
public:
    StaticTfBroadcaster(char **argv) : Node("static_tf_broadcaster_cpp") {
        RCLCPP_INFO(this->get_logger(), "静态广播方创建成功!");
        tf_publisher_ = std::make_shared<tf2_ros::StaticTransformBroadcaster>(this);
        publish_transform(argv);
    }

private:
    void publish_transform(char **argv) {
        auto qtn = tf2::Quaternion();
        qtn.setRPY(
            atof(argv[4]),
            atof(argv[5]),
            atof(argv[6])
        );

        /*
            x y z roll pitch yaw frame_id child_frame_id
        */
        auto transform = TransformStamped();
        transform.header.stamp = this->now();
        transform.header.frame_id = argv[7];
        transform.child_frame_id = argv[8];
        transform.transform.translation.x = atof(argv[1]);
        transform.transform.translation.y = atof(argv[2]);
        transform.transform.translation.z = atof(argv[3]);
        transform.transform.rotation.x = qtn.getX();
        transform.transform.rotation.y = qtn.getY();
        transform.transform.rotation.z = qtn.getZ();
        transform.transform.rotation.w = qtn.getW();

        /*
            void sendTransform(const geometry_msgs::msg::TransformStamped &transform)
        */
        tf_publisher_->sendTransform(transform);
        RCLCPP_INFO(this->get_logger(), "静态坐标发布成功!");
    }

    std::shared_ptr<tf2_ros::StaticTransformBroadcaster> tf_publisher_;
};

int main(int argc, char **argv) {
    if (argc != 9) {
        RCLCPP_ERROR(rclcpp::get_logger("rclcpp"), "输入参数数目不合法!");
        return 1;
    }

    rclcpp::init(argc, argv);
    auto node = std::make_shared<StaticTfBroadcaster>(argv);
    rclcpp::spin(node);
    rclcpp::shutdown();

    return 0;
}