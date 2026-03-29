
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray,Float64MultiArray,Int8


class MoveSystemTOTarget(Node):
    def __init__(self):
        super().__init__("move_system_to_target")
        self.system_velocity_publisher=self.create_publisher(Float64MultiArray,"/forward_velocity_controller/commands",10)
        self.system_errors=self.create_publisher(Float64MultiArray,"system_errors",10)
        self.targets_positions=self.create_subscription(Float32MultiArray,"/camera/targets",self.movecallback,10)
        self.targets_no=self.create_subscription(Int8,"target_no",self.movecallbacktargetno,10)
        self.get_logger().info("Move system to target node has been started")

        self.fixed_target_positions=[]

        self.cx=640/2
        self.cy=480/2
        self.velocity_x=0
        self.velocity_y=0
        self.velocity_value=0.2
        self.targets_number=0

    
    def movecallbacktargetno(self,targets_msg):
        self.targets_number=targets_msg.data


    def movecallback(self, out_msg):
        targets_positions = out_msg.data
        
        self.fixed_target_positions = []

        for i in range(0, len(targets_positions), 2):
            self.fixed_target_positions.append([targets_positions[i], targets_positions[i+1]])

        if not self.fixed_target_positions:
            return 
        
        error_x = self.fixed_target_positions[self.targets_number][0] - self.cx
        error_y = self.fixed_target_positions[self.targets_number][1] - self.cy

        dead_zone = 5

        error_msg=Float64MultiArray()
        error_msg.data=[error_x,error_y]
        self.system_errors.publish(error_msg)



        # if abs(error_x) <= dead_zone:
        #     self.velocity_x = 0
        # elif error_x > dead_zone:
        #     self.velocity_x = -1
        # else: 
        #     self.velocity_x = 1

        # if abs(error_y) <= dead_zone:
        #     self.velocity_y = 0
        # elif error_y > dead_zone:
        #     self.velocity_y = 1
        # else:  
        #     self.velocity_y = -1

        
        # velocity_msg=Float64MultiArray()
        # velocity_msg.data=[self.velocity_x*self.velocity_value,self.velocity_y*self.velocity_value]
        # self.system_velocity_publisher.publish(velocity_msg)



def main():
    rclpy.init()
    node = MoveSystemTOTarget()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()



        






    



