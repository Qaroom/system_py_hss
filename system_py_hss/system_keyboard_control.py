#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray
import math
import sys, termios, tty, select
from controller_manager_msgs.srv import SwitchController

def get_key(timeout=0.1):
    """Terminalden tek tuş oku (non-blocking)."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        rlist, _, _ = select.select([sys.stdin], [], [], timeout)
        if rlist:
            return sys.stdin.read(1)
        else:
            return None
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


class SystemKeyboardControl(Node):
    def __init__(self):
        super().__init__("system_keyboard_control")

        # Limitler
        self.Y_MIN, self.Y_MAX = -1.2, 0.53
        self.X_MIN, self.X_MAX = -math.pi, math.pi

        # Başlangıç değerleri
        self.step = 0.02
        self.direction_x = 0.0
        self.direction_y = 0.0
        self.velocity_x=1.0
        self.velocity_y=1.0

        # Publisher
        self.keyboardpublis = self.create_publisher(
            Float64MultiArray,
            '/forward_position_controller/commands',
            10
        )

        # self.keyboardpublisvelocity = self.create_publisher(
        #     Float64MultiArray,
        #     '/forward_velocity_controller/commands',
        #     10
        # )
        # self.cli = self.create_client(
        #     SwitchController,
        #     '/controller_manager/switch_controllers'
        # )
        # while not self.cli.wait_for_service(timeout_sec=1.0):
        #     self.get_logger().warn('switch_controllers service not available, waiting...')

        # Timer
        self.create_timer(0.1, self.callbacksystemaxisescontroller)

        self.get_logger().info("system_keyboard_control node has been started, congratulations")
        self.get_logger().info("Control with: I(up), K(down), J(left), L(right), Q(quit)")

        # self.switch_to_position()
        # self.get_logger().warn("Only position control!!! |for velociy controller press v")



    def switch_to_velocity(self):
        req = SwitchController.Request()
        req.activate_controllers = ['forward_velocity_controller']
        req.deactivate_controllers = ['forward_position_controller']
        req.strictness = req.STRICT
        # self.cli.call_async(req)

    def switch_to_position(self):
        req = SwitchController.Request()
        req.activate_controllers = ['forward_position_controller']
        req.deactivate_controllers = ['forward_velocity_controller']
        req.strictness = req.STRICT
        # self.cli.call_async(req)



    def callbacksystemaxisescontroller(self):
        key = get_key()

        if key == "i":     # Y eksenini yukarı
            self.direction_y += self.step
            if self.direction_y > self.Y_MAX:
                self.direction_y = self.Y_MAX

        elif key == "k":   # Y eksenini aşağı
            self.direction_y -= self.step
            if self.direction_y < self.Y_MIN:
                self.direction_y = self.Y_MIN

        elif key == "j":   # X sola
            self.direction_x += self.step
            if self.direction_x > self.X_MAX:
                self.direction_x = self.X_MAX

        elif key == "l":   # X sağa
            self.direction_x -= self.step
            if self.direction_x < self.X_MIN:
                self.direction_x = self.X_MIN
                
        elif key == "u":   # X sola
            self.velocity_x += 1
            if self.velocity_x > 5:
                self.velocity_x = 5
        
        elif key == "d":   # X sağa
            self.velocity_y -= 1
            if self.velocity_y < -5:
                self.velocity_y = -5

        elif key == "v":   # X sağa
            self.switch_to_velocity()
            self.get_logger().warn("Only velocity control!!!")

        elif key == "s":   # X sağa
            self.switch_to_position()
            self.get_logger().warn("Only position control!!!")

        elif key == "q":   # Çıkış
            self.get_logger().info("Exit key pressed. Shutting down...")
            rclpy.shutdown()
            return

        # Yayınla
        msg = Float64MultiArray()
        msg.data = [self.direction_x, self.direction_y]
        self.keyboardpublis.publish(msg)

        # msgvelocity = Float64MultiArray()
        # msgvelocity.data = [self.velocity_x, self.velocity_y]
        # self.keyboardpublisvelocity.publish(msgvelocity)



       # self.get_logger().info(f"Published X={self.direction_x:.2f}, Y={self.direction_y:.2f}")


def main(args=None):
    rclpy.init(args=args)
    node = SystemKeyboardControl()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
