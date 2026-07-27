/**
 * 需求：录制 turtle_teleop_key 节点发布的速度指令
 * 步骤：
 *      1、包含头文件
 *      2、初始化 ROS2 客户端
 *      3、自定义节点类
 *          3-1、创建写出对象指针和订阅对象指针
 *          3-2、打开目标文件
 *          3-3、写出订阅到的数据
 *      4、调用 spin 函数 并传入节点对象指针
 *      5、释放资源
 */

#include "geometry_msgs/msg/twist.hpp"
#include "rclcpp/rclcpp.hpp"
#include "rosbag2_cpp/writer.hpp"

using geometry_msgs::msg::Twist;
using std::placeholders::_1;

class BagRecoder : public rclcpp::Node {
public:
    BagRecoder() : Node("bag_recoder_cpp") {
        RCLCPP_INFO(this->get_logger(), "数据录制方创建成功!");
        writer_ = std::make_unique<rosbag2_cpp::Writer>();
        writer_->open("my_bag_cpp");
        subscriber_ = this->create_subscription<Twist>(
            "/turtle1/cmd_vel", 10,
            std::bind(&BagRecoder::write_callback ,this, _1)
        );
    }

private:
    void write_callback(const std::shared_ptr<rclcpp::SerializedMessage> msg) {
        RCLCPP_INFO(this->get_logger(), "数据写入中...");
        /*
            void write(
                std::shared_ptr<rclcpp::SerializedMessage> message,
                const std::string &topic_name,
                const std::string &type_name,
                const rclcpp::Time &time
            )
        */
        writer_->write(msg, "/turtle1/cmd_vel", "geometry_msgs/msg/Twist", this->now());
    }

    std::unique_ptr<rosbag2_cpp::Writer> writer_;
    rclcpp::Subscription<Twist>::SharedPtr subscriber_;
};

int main(int argc, char **argv) {
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<BagRecoder>());
    rclcpp::shutdown();

    return 0;
}