import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2


class ImageSubscriber(Node):
    def __init__(self):
        super().__init__('image_subscriber')
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10)
        self.bridge = CvBridge()

    def image_callback(self, msg):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')


            cv2.waitKey(1)

        except Exception as e:
            self.get_logger().error(f"Error converting image: {e}")


def main(args=None):
    rclpy.init(args=args)
    node = ImageSubscriber()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()


# #!/usr/bin/env python3
# import rclpy
# from rclpy.node import Node
# from sensor_msgs.msg import JointState
# from std_msgs.msg import Float64MultiArray
# import sys, termios, tty, select
# # import keyboard

# def get_key(timeout=0.1):
#     """Terminalden tek tuş oku (non-blocking)."""
#     fd = sys.stdin.fileno()
#     old_settings = termios.tcgetattr(fd)
#     try:
#         tty.setraw(fd)
#         rlist, _, _ = select.select([sys.stdin], [], [], timeout)
#         if rlist:
#             return sys.stdin.read(1)
#         else:
#             return None
#     finally:
#         termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


# class IndependentVelocityController(Node):
#     def __init__(self):
#         super().__init__('independent_velocity_controller')

#         # Publisher (hız komutları)
#         self.pub = self.create_publisher(
#             Float64MultiArray,
#             '/forward_velocity_controller/commands',
#             10
#         )

#         # Subscriber (joint states)
#         self.create_subscription(JointState, '/joint_states', self.joint_callback, 10)

#         # Parametreler
#         self.joint_names = ["base_support_joint", "support_right_mil_joint"]
#         self.current_positions = [0.0, 0.0]
#         self.target_positions = [-1.0, 0.2]

#         # Kontrol ayarları
#         self.speed = 0.5
#         self.tolerance = 0.1

#         self.get_logger().info("IndependentVelocityController çalışıyor. Terminalden hedef gir!")

#     def joint_callback(self, msg: JointState):
#         try:
#             self.current_positions = [msg.position[msg.name.index(n)] for n in self.joint_names]
#         except ValueError:
#             return

#         if self.target_positions is None:
#             return

#         velocities = []

#         # Her eklemi ayrı ayrı kontrol et
#         for t, c in zip(self.target_positions, self.current_positions):
#             error = t - c
#             self.get_logger().warn(f"error value : {error}")
#             if abs(error) <= self.tolerance:
#                 # Hedefteyse → hız = 0
#                 velocities.append(0.0)
#             else:
#                 # Hedefe git → uygun yönde sabit hız
#                 direction = 1.0 if error > 0 else -1.0
#                 velocities.append(direction * self.speed)

#         # Hız komutunu yayınla
#         msg_out = Float64MultiArray()
#         msg_out.data = velocities
#         self.pub.publish(msg_out)

#         # Log
#         self.get_logger().info(f"Current: {self.current_positions}, Target: {self.target_positions}, Vel: {velocities}")

#         # Eğer tüm eklemler hedefteyse → hedefi sıfırla
#         # if all(abs(t - c) <= self.tolerance for t, c in zip(self.target_positions, self.current_positions)):
#         #     self.get_logger().info("🎯 Tüm eklemler hedefe ulaştı, duruldu.")
#         #     self.target_positions = None

#     def set_target(self, target):
#         if len(target) != len(self.joint_names):
#             self.get_logger().error("⚠️ Hedef uzunluğu eklem sayısıyla uyuşmuyor!")
#             return
#         self.target_positions = target
#         self.get_logger().info(f"Yeni hedef: {target}")


# def main(args=None):
#     rclpy.init(args=args)
#     node = IndependentVelocityController()
#     rclpy.spin(node)
#     node.destroy_node()
#     rclpy.shutdown()



# if __name__ == "__main__":
#     main()





# #!/usr/bin/env python3
# import rclpy
# from rclpy.node import Node
# from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
# from sensor_msgs.msg import JointState

# class TrajectoryPublisher(Node):
#     def __init__(self):
#         super().__init__('trajectory_publisher_with_velocity')

#         # Publisher
#         self.publisher_ = self.create_publisher(
#             JointTrajectory,
#             '/joint_trajectory_controller/joint_trajectory',
#             10
#         )

#         # Subscriber (joint_states)
#         self.create_subscription(
#             JointState,
#             '/joint_states',
#             self.joint_state_callback,
#             10
#         )

#         # Son bilinen pozisyon
#         self.current_positions = []
#         self.joint_names = ["base_support_joint", "support_right_mil_joint"]

#         self.get_logger().info("TrajectoryPublisher hazır. Terminalden hedef poz gir!")

#     def joint_state_callback(self, msg: JointState):
#         # Gelen joint state, bizim eklem isimleriyle eşleşiyorsa kaydet
#         if all(name in msg.name for name in self.joint_names):
#             self.current_positions = [msg.position[msg.name.index(name)] for name in self.joint_names]

#     def send_trajectory(self, target_positions, duration=2.0, start_velocity=0.5):
#         if not self.current_positions:
#             self.get_logger().warn("Henüz current_positions alınmadı!")
#             return

#         traj = JointTrajectory()
#         traj.joint_names = self.joint_names

#         # 1️⃣ Başlangıç noktası: hedef pozisyon + başlangıç hızı
#         start_point = JointTrajectoryPoint()
#         start_point.positions = target_positions
#         start_point.velocities = [start_velocity]*len(target_positions)
#         start_point.time_from_start.sec = int(duration)
#         start_point.time_from_start.nanosec = int((duration - int(duration)) * 1e9)

#         # 2️⃣ Bitiş noktası: aynı pozisyon + hız 0
#         stop_point = JointTrajectoryPoint()
#         stop_point.positions = target_positions
#         stop_point.velocities = [0.0]*len(target_positions)
#         stop_point.time_from_start.sec = int(duration + 1)  # 1 saniye sonra dur
#         stop_point.time_from_start.nanosec = 0

#         traj.points.append(start_point)
#         traj.points.append(stop_point)

#         self.publisher_.publish(traj)
#         self.get_logger().info(f"Trajectory gönderildi: {target_positions}, başlangıç hızı={start_velocity}, hedefte durdu")

# def main(args=None):
#     rclpy.init(args=args)
#     node = TrajectoryPublisher()

#     try:
#         while rclpy.ok():
#             rclpy.spin_once(node, timeout_sec=0.1)

#             # Kullanıcıdan hedef pozisyon al
#             cmd = input("Hedef pozisyonları boşlukla gir (ör: 1.57 -0.5), çıkış için q: ")
#             if cmd.lower() == "q":
#                 break

#             try:
#                 target = [float(x) for x in cmd.strip().split()]
#                 if len(target) != len(node.joint_names):
#                     print(f"⚠️ {len(node.joint_names)} eklem için {len(target)} değer girmen gerek!")
#                     continue

#                 node.send_trajectory(target, duration=2.0, start_velocity=0.5)

#             except ValueError:
#                 print("Geçersiz giriş, tekrar dene.")

#     except KeyboardInterrupt:
#         pass
#     finally:
#         node.destroy_node()
#         rclpy.shutdown()

# if __name__ == '__main__':
#     main()





# import rclpy
# from rclpy.node import Node
# from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

# class TrajectoryPublisher(Node):
#     def __init__(self):
#         super().__init__('trajectory_publisher')

#         # Publisher -> joint trajectory controller'ın topic'i
#         self.publisher_ = self.create_publisher(
#             JointTrajectory,
#             '/joint_trajectory_controller/joint_trajectory',
#             10
#         )

#         timer_period = 2  # 2 saniyede bir yayınla
#         self.timer = self.create_timer(timer_period, self.timer_callback)

#     def timer_callback(self):
#         traj = JointTrajectory()
#         traj.joint_names = ["base_support_joint","support_right_mil_joint"]

#         point = JointTrajectoryPoint()
#         point.positions = [3.10, -1.0]   # hedef pozisyonlar
#         # point.velocities = [1.8, 1.8]   # opsiyonel hız
#         point.time_from_start.sec = 2                     # 2 saniyede ulaş

#         traj.points.append(point)

#         # publish et
#         self.publisher_.publish(traj)
#         self.get_logger().info("Trajectory gönderildi!")

# def main(args=None):
#     rclpy.init(args=args)
#     node = TrajectoryPublisher()
#     rclpy.spin(node)
#     node.destroy_node()
#     rclpy.shutdown()

# if __name__ == '__main__':
#     main()
