#include "rclcpp/rclcpp.hpp"
#include "tf2_ros/buffer.hpp"
#include "tf2_ros/transform_listener.hpp"
#include "tf2_ros/create_timer_ros.hpp"
#include "message_filters/subscriber.hpp"
#include "geometry_msgs/msg/point_stamped.hpp"
#include "tf2_ros/message_filter.hpp"
#include "tf2_geometry_msgs/tf2_geometry_msgs.hpp"

using namespace std::chrono_literals;
using geometry_msgs::msg::PointStamped;

class PointTransformer : public rclcpp::Node {
public:
    PointTransformer() : Node("point_transformer_cpp") {
        RCLCPP_INFO(this->get_logger(), "坐标点变换方创建成功!");
        buffer_ = std::make_shared<tf2_ros::Buffer>(this->get_clock());
        /*
            CreateTimerROS(
                rclcpp::node_interfaces::NodeBaseInterface::SharedPtr node_base, rclcpp::node_interfaces::NodeTimersInterface::SharedPtr node_timers,
                rclcpp::CallbackGroup::SharedPtr callback_group = nullptr
            )
        */
        timer_ = std::make_shared<tf2_ros::CreateTimerROS>(
            this->get_node_base_interface(),
            this->get_node_timers_interface()
        );
        /*
            void setCreateTimerInterface(
                tf2_ros::CreateTimerInterface::SharedPtr create_timer_interface
            )
        */
        buffer_->setCreateTimerInterface(timer_);
        listener_ = std::make_shared<tf2_ros::TransformListener>(*buffer_, this);
        subscriber_.subscribe(this, "point");
        /*
            MessageFilter<F, TimeRepT, TimeT>(
                F &f,
                tf2_ros::Buffer &buffer,
                const std::string &target_frame,
                uint32_t queue_size,
                const rclcpp::node_interfaces::NodeLoggingInterface::SharedPtr &node_logging,
                const rclcpp::node_interfaces::NodeClockInterface::SharedPtr &node_clock, std::chrono::duration<TimeRepT, TimeT> buffer_timeout
            )
        */
        filter_ = std::make_shared<tf2_ros::MessageFilter<PointStamped>>(
            subscriber_, *buffer_, "base_link", 10,
            this->get_node_logging_interface(),
            this->get_node_clock_interface(), 1s
        );
        filter_->registerCallback(&PointTransformer::transform_callback, this);
    }

private:
    void transform_callback(const PointStamped::SharedPtr msg) {
        auto out_point = PointStamped();
        try {
            out_point = buffer_->transform(*msg, "base_link");
            RCLCPP_INFO(
                this->get_logger(), "转换结果为: frame_id: %s, [%.2f, %.2f, %.2f]",
                out_point.header.frame_id.c_str(),
                out_point.point.x,
                out_point.point.y,
                out_point.point.z
            );
        } catch(const tf2::TransformException& e) {
            RCLCPP_WARN(this->get_logger(), "转换异常: %s", e.what());
        }
    }

    std::shared_ptr<tf2_ros::Buffer> buffer_;
    std::shared_ptr<tf2_ros::TransformListener> listener_;
    std::shared_ptr<tf2_ros::CreateTimerROS> timer_;
    message_filters::Subscriber<PointStamped> subscriber_;
    std::shared_ptr<tf2_ros::MessageFilter<PointStamped>> filter_;
};

int main(int argc, char **argv) {
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<PointTransformer>());
    rclcpp::shutdown();

    return 0;
}