#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2
from geometry_msgs.msg import TransformStamped
import sensor_msgs_py.point_cloud2 as pc2
from tf2_ros import TransformBroadcaster
import numpy as np

# The camera frame — confirmed from your topic echo
CAMERA_FRAME = "link_6"
OBJECT_FRAME = "target_object"


class ObjectDetector(Node):

    def __init__(self):
        super().__init__('object_detector')
        self.tf_broadcaster = TransformBroadcaster(self)

        self.sub = self.create_subscription(
            PointCloud2,
            '/filtered_points',
            self.cloud_callback,
            10
        )
        self.get_logger().info('Object Detector started')
        self.get_logger().info(f'Listening on /filtered_points')
        self.get_logger().info(f'Will broadcast: {CAMERA_FRAME} -> {OBJECT_FRAME}')

    def cloud_callback(self, msg):
        # --- Step 1: Read all points from the filtered cloud ---
        points = list(pc2.read_points(msg, field_names=(["x", "y", "z"]), skip_nans=True))

        if len(points) < 10:
            self.get_logger().warn('Too few points to detect object, skipping')
            return

        # --- Step 2: Convert to numpy array ---
        pts = np.array([[p[0], p[1], p[2]] for p in points])

        # --- Step 3: Find centroid of all remaining points ---
        # After filtering, what remains on the table IS the object
        # This is valid as long as your PassThrough crops out the table surface itself
        centroid = pts.mean(axis=0)

        # --- Step 4: Broadcast TF transform ---
        t = TransformStamped()
        t.header.stamp = msg.header.stamp   # use cloud timestamp, not now()
        t.header.frame_id = CAMERA_FRAME
        t.child_frame_id = OBJECT_FRAME

        t.transform.translation.x = float(centroid[0])
        t.transform.translation.y = float(centroid[1])
        t.transform.translation.z = float(centroid[2])

        # No rotation — we're reporting position only
        t.transform.rotation.x = 0.0
        t.transform.rotation.y = 0.0
        t.transform.rotation.z = 0.0
        t.transform.rotation.w = 1.0

        self.tf_broadcaster.sendTransform(t)

        self.get_logger().debug(
            f'Object at ({centroid[0]:.3f}, {centroid[1]:.3f}, {centroid[2]:.3f}) '
            f'in frame [{CAMERA_FRAME}]'
        )


def main(args=None):
    rclpy.init(args=args)
    node = ObjectDetector()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()