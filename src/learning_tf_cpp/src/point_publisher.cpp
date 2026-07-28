#include "rclcpp/rclcpp.hpp"
#include "geometry_msgs/msg/point_stamped.hpp"

using geometry_msgs::msg::PointStamped;
using namespace std::chrono_literals;

class PointPublisher : public rclcpp::Node {
public:
    PointPublisher() : Node("point_publisher_cpp"), x_(0.0) {
        RCLCPP_INFO(this->get_logger(), "坐标点发布方创建成功!");
        publisher_ = this->create_publisher<PointStamped>("point", 10);
        timer_ = this->create_wall_timer(0.1s, std::bind(&PointPublisher::timer_callback, this));
    }

private:
    void timer_callback() {
        auto msg = PointStamped();
        msg.header.stamp = this->now();
        msg.header.frame_id = "laser";
        msg.point.x = x_;
        msg.point.y = 0.0;
        msg.point.z = -0.5;
        x_ += 0.05;

        publisher_->publish(msg);
    }

    rclcpp::Publisher<PointStamped>::SharedPtr publisher_;
    rclcpp::TimerBase::SharedPtr timer_;
    double x_;
};

int main(int argc, char **argv) {
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<PointPublisher>());
    rclcpp::shutdown();

    return 0;
}