#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/point_cloud2.hpp>
#include <pcl_conversions/pcl_conversions.h>
#include <pcl/point_cloud.h>
#include <pcl/point_types.h>
#include <pcl/filters/voxel_grid.h>
#include <pcl/filters/passthrough.h>

class PCLFilterNode : public rclcpp::Node
{
public:
  PCLFilterNode() : Node("pcl_filter_node")
  {
    // Declare parameters with defaults
    this->declare_parameter("voxel_leaf_size", 0.01);
    this->declare_parameter("pass_z_min", 0.1);
    this->declare_parameter("pass_z_max", 1.5);
    this->declare_parameter("pass_x_min", -0.5);
    this->declare_parameter("pass_x_max", 0.5);
    this->declare_parameter("pass_y_min", -0.5);
    this->declare_parameter("pass_y_max", 0.5);
    this->declare_parameter("input_topic", std::string("/camera/depth_image/points"));
    this->declare_parameter("output_topic", std::string("/filtered_points"));

    std::string input_topic  = this->get_parameter("input_topic").as_string();
    std::string output_topic = this->get_parameter("output_topic").as_string();

    sub_ = this->create_subscription<sensor_msgs::msg::PointCloud2>(
      input_topic, 10,
      std::bind(&PCLFilterNode::cloud_callback, this, std::placeholders::_1));

    pub_ = this->create_publisher<sensor_msgs::msg::PointCloud2>(output_topic, 10);

    RCLCPP_INFO(this->get_logger(), "PCL Filter Node started");
    RCLCPP_INFO(this->get_logger(), "Subscribing to: %s", input_topic.c_str());
    RCLCPP_INFO(this->get_logger(), "Publishing to:  %s", output_topic.c_str());
  }

private:
  void cloud_callback(const sensor_msgs::msg::PointCloud2::SharedPtr msg)
  {
    // Read current parameters (allows runtime tuning)
    float voxel_leaf = this->get_parameter("voxel_leaf_size").as_double();
    float z_min = this->get_parameter("pass_z_min").as_double();
    float z_max = this->get_parameter("pass_z_max").as_double();
    float x_min = this->get_parameter("pass_x_min").as_double();
    float x_max = this->get_parameter("pass_x_max").as_double();
    float y_min = this->get_parameter("pass_y_min").as_double();
    float y_max = this->get_parameter("pass_y_max").as_double();

    // --- Step 1: Convert ROS message → PCL cloud ---
    pcl::PointCloud<pcl::PointXYZ>::Ptr cloud(new pcl::PointCloud<pcl::PointXYZ>);
    pcl::fromROSMsg(*msg, *cloud);

    if (cloud->empty()) {
      RCLCPP_WARN(this->get_logger(), "Received empty cloud, skipping");
      return;
    }

    // --- Step 2: Voxel Grid (downsample) ---
    pcl::PointCloud<pcl::PointXYZ>::Ptr cloud_voxeled(new pcl::PointCloud<pcl::PointXYZ>);
    pcl::VoxelGrid<pcl::PointXYZ> vg;
    vg.setInputCloud(cloud);
    vg.setLeafSize(voxel_leaf, voxel_leaf, voxel_leaf);
    vg.filter(*cloud_voxeled);

    // --- Step 3: PassThrough on Z (depth — keep what's in front of camera) ---
    pcl::PointCloud<pcl::PointXYZ>::Ptr cloud_z(new pcl::PointCloud<pcl::PointXYZ>);
    pcl::PassThrough<pcl::PointXYZ> pass_z;
    pass_z.setInputCloud(cloud_voxeled);
    pass_z.setFilterFieldName("z");
    pass_z.setFilterLimits(z_min, z_max);
    pass_z.filter(*cloud_z);

    // --- Step 4: PassThrough on X (left/right crop) ---
    pcl::PointCloud<pcl::PointXYZ>::Ptr cloud_x(new pcl::PointCloud<pcl::PointXYZ>);
    pcl::PassThrough<pcl::PointXYZ> pass_x;
    pass_x.setInputCloud(cloud_z);
    pass_x.setFilterFieldName("x");
    pass_x.setFilterLimits(x_min, x_max);
    pass_x.filter(*cloud_x);

    // --- Step 5: PassThrough on Y (up/down crop) ---
    pcl::PointCloud<pcl::PointXYZ>::Ptr cloud_filtered(new pcl::PointCloud<pcl::PointXYZ>);
    pcl::PassThrough<pcl::PointXYZ> pass_y;
    pass_y.setInputCloud(cloud_x);
    pass_y.setFilterFieldName("y");
    pass_y.setFilterLimits(y_min, y_max);
    pass_y.filter(*cloud_filtered);

    // --- Step 6: Convert PCL cloud → ROS message and publish ---
    sensor_msgs::msg::PointCloud2 output_msg;
    pcl::toROSMsg(*cloud_filtered, output_msg);
    output_msg.header = msg->header; // preserve original frame_id and timestamp

    pub_->publish(output_msg);

    RCLCPP_DEBUG(this->get_logger(),
      "Filtered: %zu → %zu points",
      cloud->size(), cloud_filtered->size());
  }

  rclcpp::Subscription<sensor_msgs::msg::PointCloud2>::SharedPtr sub_;
  rclcpp::Publisher<sensor_msgs::msg::PointCloud2>::SharedPtr pub_;
};

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<PCLFilterNode>());
  rclcpp::shutdown();
  return 0;
}