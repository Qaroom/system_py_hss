#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray
import matplotlib.pyplot as plt
import numpy as np
import threading
import time

TIME_STEP = 0.0167
MAX_OUTPUT = 7.0
MIN_OUTPUT = -7.0
DEADZONE=0.0
# PID parameters
# KP_X, KI_X, KD_X = 0.080000, 79.168728, 0.053354
# KP_Y, KI_Y, KD_Y = 0.080000, 79.168728, 0.000057

KP_X, KI_X, KD_X = 0.011, 0.002, 0.0002
KP_Y, KI_Y, KD_Y = 0.011, 0.0008, 0.0002



class PID:
    def __init__(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.error = 0.0
        self.error_last = 0.0
        self.integral = 0.0
        self.output = 0.0

    def update(self, error, dt):
    # Deadzone uygulaması
        if abs(error) < DEADZONE:
            error = 0.0

        self.error = error
        derivative = (error - self.error_last) / dt
        self.integral += error * dt
        self.integral = np.clip(self.integral, -5, 5)  # anti-windup
        output = self.kp * error + self.ki * self.integral + self.kd * derivative
        self.error_last = error
        return np.clip(output, MIN_OUTPUT, MAX_OUTPUT)


class DualPIDNode(Node):
    def __init__(self):
        super().__init__('dual_pid_controller')

        self.pid_x = PID(KP_X, KI_X, KD_X)
        self.pid_y = PID(KP_Y, KI_Y, KD_Y)
        self.error_x = 0.0
        self.error_y = 0.0

        self.create_subscription(Float64MultiArray, 'system_errors', self.error_callback, 10)
        self.pub_velocity = self.create_publisher(Float64MultiArray, 'forward_velocity_controller/commands', 10)

        self.time_data, self.out_x_data, self.out_y_data = [], [], []
        self.start_time = time.time()

        self.create_timer(TIME_STEP, self.update)
        threading.Thread(target=self.plot_live, daemon=True).start()
        self.get_logger().info("Dual-axis PID controller started.")

    def error_callback(self, msg):
        if len(msg.data) >= 2:
            self.error_x, self.error_y = msg.data[0], msg.data[1]
        else:
            self.get_logger().warn(f"Invalid error array: {msg.data}")

    def update(self):
        self.out_x = self.pid_x.update(self.error_x, TIME_STEP)
        self.out_y = self.pid_y.update(self.error_y, TIME_STEP)

        vel_msg = Float64MultiArray()
        vel_msg.data = [self.out_x * -1, self.out_y]
        self.pub_velocity.publish(vel_msg)

        t = time.time() - self.start_time
        self.time_data.append(t)
        self.out_x_data.append(self.out_x)
        self.out_y_data.append(self.out_y)

    def plot_live(self):
        plt.ion()
        fig, ax = plt.subplots()
        
        # Hata ve output çizgileri
        line_ex, = ax.plot([], [], label='Error X', color='orange')
        line_ey, = ax.plot([], [], label='Error Y', color='green')
        line_outx, = ax.plot([], [], label='Output X', color='blue')
        line_outy, = ax.plot([], [], label='Output Y', color='red')
        
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Value')
        ax.set_title('Real-Time Error and PID Output (X and Y)')
        ax.legend()
        ax.grid(True)

        # Verileri saklamak için listeler
        error_x_data = []
        error_y_data = []
        out_x_data = []
        out_y_data = []
        time_data = []

        start_time = time.time()

        # --- Tıklama olayını yakalayan fonksiyon ---
        def onclick(event):
            if event.inaxes == ax:
                x_val = event.xdata
                y_val = event.ydata
                print(f"\n🟩 Selected Point → Time: {x_val:.3f} s | Value: {y_val:.3f}\n")

        fig.canvas.mpl_connect('button_press_event', onclick)

        # --- Tu tahmini fonksiyonu ---
        def estimate_Tu(time_data, error_data):
            if len(error_data) < 2:
                return None
            zero_crossings = np.where(np.diff(np.sign(error_data)))[0]
            if len(zero_crossings) < 2:
                return None
            periods = np.diff([time_data[i] for i in zero_crossings])
            Tu_est = np.mean(periods) * 2  # tam periyot
            return Tu_est

        # --- Canlı çizim döngüsü ---
        while rclpy.ok():
            t = time.time() - start_time
            time_data.append(t)
            error_x_data.append(self.error_x)
            error_y_data.append(self.error_y)
            out_x_data.append(self.out_x)
            out_y_data.append(self.out_y)

            # Çizgileri güncelle
            line_ex.set_xdata(time_data)
            line_ey.set_xdata(time_data)
            line_outx.set_xdata(time_data)
            line_outy.set_xdata(time_data)

            line_ex.set_ydata(error_x_data)
            line_ey.set_ydata(error_y_data)
            line_outx.set_ydata(out_x_data)
            line_outy.set_ydata(out_y_data)

            ax.relim()
            ax.autoscale_view()
            plt.pause(0.05)

            # Tu tahmini (opsiyonel, ekrana yazdır)
            Tu_x = estimate_Tu(time_data, error_x_data)
            Tu_y = estimate_Tu(time_data, error_y_data)
            if Tu_x:
                print(f"Estimated Tu X: {Tu_x:.3f} s", end='\r')
            if Tu_y:
                print(f"Estimated Tu Y: {Tu_y:.3f} s", end='\r')

        plt.ioff()
        plt.show()



def main(args=None):
    rclpy.init(args=args)
    node = DualPIDNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()



