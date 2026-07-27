/**
 * 需求：读取 bag 文件中的数据
 * 步骤：
 *      1、包含头文件
 *      2、初始化 ROS2 客户端
 *      3、自定义节点类
 *          3-1、创建读取对象指针
 *          3-2、打开 bag 文件
 *          3-3、读取数据 之后关闭文件
 *      4、调用 spin 函数 并传入节点对象指针
 *      5、释放资源
 */

#include "geometry_msgs/msg/twist.hpp"
#include "rclcpp/rclcpp.hpp"
#include "rosbag2_cpp/reader.hpp"

using geometry_msgs::msg::Twist;

class BagPlayer : public rclcpp::Node {
public:
    BagPlayer() : Node("bag_player_cpp") {
        RCLCPP_INFO(this->get_logger(), "数据回放方创建成功!");
        reader_ = std::make_unique<rosbag2_cpp::Reader>();
        reader_->open("my_bag_cpp");
        while (reader_->has_next()) {
            auto msg = reader_->read_next<Twist>();
            RCLCPP_INFO(
                this->get_logger(), "线速度: %.2f, 角速度: %.2f",
                msg.linear.x, msg.angular.z
            );
        }
    }

private:
    std::unique_ptr<rosbag2_cpp::Reader> reader_;
};

int main(int argc, char **argv) {
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<BagPlayer>());
    rclcpp::shutdown();

    return 0;
}