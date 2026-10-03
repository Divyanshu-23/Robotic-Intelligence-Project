import os
from enum import Enum

import rclpy
import yaml
from ament_index_python.packages import get_package_share_directory
from action_msgs.msg import GoalStatus
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.node import Node
from std_msgs.msg import String

from warehouse_robot_interfaces.srv import RequestDelivery


class MissionState(Enum):
    IDLE = 'IDLE'
    GO_TO_PACKAGE = 'GO_TO_PACKAGE'
    PACKAGE_REACHED = 'PACKAGE_REACHED'
    PICKUP_SIMULATION = 'PICKUP_SIMULATION'
    GO_TO_DESTINATION = 'GO_TO_DESTINATION'
    DELIVERY = 'DELIVERY'
    RETURN_TO_BASE = 'RETURN_TO_BASE'
    COMPLETED = 'COMPLETED'
    NAVIGATION_FAILED = 'NAVIGATION_FAILED'


class MissionPlanner(Node):
    def __init__(self):
        super().__init__('mission_planner')
        self._callback_group = ReentrantCallbackGroup()
        self.declare_parameter('warehouse_file', '')
        self.declare_parameter('pickup_duration_sec', 2.0)
        self.declare_parameter('delivery_duration_sec', 2.0)
        self.declare_parameter('max_navigation_retries', 1)

        warehouse_file = self.get_parameter('warehouse_file').value
        if not warehouse_file:
            navigation_share = get_package_share_directory(
                'warehouse_robot_navigation'
            )
            warehouse_file = os.path.join(
                navigation_share, 'config', 'warehouse.yaml'
            )
        self._warehouse = self._load_warehouse(warehouse_file)

        self._state = MissionState.IDLE
        self._package_id = None
        self._package = None
        self._destination = None
        self._navigation_goal = None
        self._navigation_wait_timer = None
        self._navigation_retries = 0
        self._timer = None

        self._state_publisher = self.create_publisher(
            String, 'mission_state', 10
        )
        self._package_publisher = self.create_publisher(
            String, 'active_package', 10
        )
        self._delivery_service = self.create_service(
            RequestDelivery,
            'request_delivery',
            self._request_delivery,
            callback_group=self._callback_group,
        )
        self._navigate_client = ActionClient(
            self,
            NavigateToPose,
            'navigate_to_pose',
            callback_group=self._callback_group,
        )
        self._publish_state()
        self.get_logger().info(
            'Mission planner ready. Request a package with '
            '`ros2 service call /request_delivery '
            'warehouse_robot_interfaces/srv/RequestDelivery '
            '"{package_id: A12}"`.'
        )

    @staticmethod
    def _load_warehouse(path):
        try:
            with open(path, encoding='utf-8') as warehouse_file:
                warehouse = yaml.safe_load(warehouse_file)
        except (OSError, yaml.YAMLError) as error:
            raise RuntimeError(
                f'Unable to load warehouse catalog {path}: {error}'
            ) from error
        if not isinstance(warehouse, dict):
            raise RuntimeError('Warehouse catalog must contain a mapping')
        for section in ('base', 'packages', 'stations'):
            if section not in warehouse or not isinstance(
                warehouse[section], dict
            ):
                raise RuntimeError(
                    f'Warehouse catalog is missing mapping: {section}'
                )
        return warehouse

    def _request_delivery(self, request, response):
        package_id = request.package_id.strip()
        if self._state != MissionState.IDLE:
            response.accepted = False
            response.message = (
                f'Mission already active in state {self._state.value}'
            )
            return response

        package = self._warehouse['packages'].get(package_id)
        if package is None:
            response.accepted = False
            response.message = f'Unknown package: {package_id}'
            return response

        destination_id = package.get('destination')
        if destination_id not in self._warehouse['stations']:
            response.accepted = False
            response.message = (
                f'Package {package_id} references unknown station '
                f'{destination_id}'
            )
            return response

        self._package_id = package_id
        self._package = package
        self._destination = self._warehouse['stations'][destination_id]
        self._navigation_retries = 0
        response.accepted = True
        response.message = f'Delivery accepted for package {package_id}'
        self._package_publisher.publish(String(data=package_id))
        self._set_state(MissionState.GO_TO_PACKAGE)
        self._send_navigation_goal(package['location'])
        return response

    def _send_navigation_goal(self, location):
        if not self._navigate_client.wait_for_server(timeout_sec=0.0):
            self.get_logger().warning(
                'Nav2 action server is not available; waiting for it'
            )
            if self._navigation_wait_timer is None:
                self._navigation_wait_timer = self.create_timer(
                    1.0,
                    lambda: self._send_navigation_goal(location),
                    callback_group=self._callback_group,
                )
            return
        if self._navigation_wait_timer is not None:
            self._navigation_wait_timer.cancel()
            self._navigation_wait_timer = None

        if self._navigation_goal is not None:
            self._navigation_goal.cancel_goal_async()
            self._navigation_goal = None

        goal = NavigateToPose.Goal()
        goal.pose = self._pose_from_location(location)
        future = self._navigate_client.send_goal_async(
            goal, feedback_callback=self._navigation_feedback
        )
        future.add_done_callback(self._goal_response)

    def _goal_response(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self._navigation_failed('Nav2 rejected the goal')
            return
        self._navigation_goal = goal_handle
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self._navigation_result)

    def _navigation_result(self, future):
        result = future.result()
        self._navigation_goal = None
        if result.status != GoalStatus.STATUS_SUCCEEDED:
            self._navigation_failed(
                f'Navigation failed with status {result.status}'
            )
            return

        if self._state == MissionState.GO_TO_PACKAGE:
            self._set_state(MissionState.PACKAGE_REACHED)
            self._start_timed_state(
                MissionState.PICKUP_SIMULATION,
                self.get_parameter('pickup_duration_sec').value,
                self._start_destination_navigation,
            )
        elif self._state == MissionState.GO_TO_DESTINATION:
            self._set_state(MissionState.DELIVERY)
            self._start_timed_state(
                MissionState.DELIVERY,
                self.get_parameter('delivery_duration_sec').value,
                self._start_return_navigation,
            )
        elif self._state == MissionState.RETURN_TO_BASE:
            self._set_state(MissionState.COMPLETED)
            self._finish_mission()

    def _start_destination_navigation(self):
        self._set_state(MissionState.GO_TO_DESTINATION)
        self._navigation_retries = 0
        self._send_navigation_goal(self._destination['location'])

    def _start_return_navigation(self):
        self._set_state(MissionState.RETURN_TO_BASE)
        self._navigation_retries = 0
        self._send_navigation_goal(self._warehouse['base']['location'])

    def _navigation_failed(self, reason):
        self.get_logger().error(reason)
        failed_state = self._state
        self._set_state(MissionState.NAVIGATION_FAILED)
        max_retries = self.get_parameter('max_navigation_retries').value
        if self._navigation_retries < max_retries:
            self._navigation_retries += 1
            self.get_logger().warning(
                f'Retrying navigation ({self._navigation_retries}/'
                f'{max_retries})'
            )
            retry_state = failed_state
            self._set_state(retry_state)
            if retry_state == MissionState.GO_TO_PACKAGE:
                location = self._package['location']
            elif retry_state == MissionState.GO_TO_DESTINATION:
                location = self._destination['location']
            else:
                location = self._warehouse['base']['location']
            self._send_navigation_goal(location)
        else:
            self.get_logger().error('Mission aborted after navigation failure')
            self._finish_mission()

    def _start_timed_state(self, state, duration, callback):
        if self._timer is not None:
            self._timer.cancel()
        self._timer = self.create_timer(
            max(0.0, duration), callback, callback_group=self._callback_group
        )

    def _finish_mission(self):
        if self._timer is not None:
            self._timer.cancel()
            self._timer = None
        self._package_id = None
        self._package = None
        self._destination = None
        self._navigation_goal = None
        self._set_state(MissionState.IDLE)
        self._package_publisher.publish(String(data=''))

    def _set_state(self, state):
        self._state = state
        self._publish_state()
        self.get_logger().info(f'Mission state: {state.value}')

    def _publish_state(self):
        self._state_publisher.publish(String(data=self._state.value))

    def _navigation_feedback(self, feedback):
        del feedback

    def _pose_from_location(self, location):
        if not isinstance(location, (list, tuple)) or len(location) != 2:
            raise ValueError('Warehouse locations must be [x, y]')
        pose = PoseStamped()
        pose.header.frame_id = 'map'
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.pose.position.x = float(location[0])
        pose.pose.position.y = float(location[1])
        pose.pose.orientation.w = 1.0
        return pose


def main(args=None):
    rclpy.init(args=args)
    node = MissionPlanner()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
