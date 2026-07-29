#include "rclcpp/rclcpp.hpp"
#include "tf2_ros/buffer.hpp"
#include "tf2_ros/transform_listener.hpp"

using namespace std::chrono_literals;

class TfListener : public rclcpp::Node {
public:
    TfListener() : Node("tf_listener_cpp") {
        RCLCPP_INFO(this->get_logger(), "坐标系监听方创建成功!");
        buffer_ = std::make_unique<tf2_ros::Buffer>(this->get_clock());
        listener_ = std::make_shared<tf2_ros::TransformListener>(*buffer_, this);
        timer_ = this->create_wall_timer(1s, std::bind(&TfListener::timer_callback, this));
    }

private:
    void timer_callback() {
        try {
            auto transform = buffer_->lookupTransform("camera", "laser", tf2::TimePointZero);
            RCLCPP_INFO(this->get_logger(), "----------转换完成----------");
            RCLCPP_INFO(
                this->get_logger(), "target_frame: %s, source_frame: %s, [%.2f, %.2f, %.2f]",
                transform.header.frame_id.c_str(),
                transform.child_frame_id.c_str(),
                transform.transform.translation.x,
                transform.transform.translation.y,
                transform.transform.translation.z
            );
        } catch (const tf2::LookupException &e) {
            RCLCPP_WARN(this->get_logger(), "转换异常: %s", e.what());
        }
    }

    std::unique_ptr<tf2_ros::Buffer> buffer_;
    std::shared_ptr<tf2_ros::TransformListener> listener_;
    rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char **argv) {
    rclcpp::init(argc, argv);

    auto listener = std::make_shared<TfListener>();
    rclcpp::spin(listener);

    rclcpp::shutdown();

    return 0;
}