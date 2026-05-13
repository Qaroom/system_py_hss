#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Float32MultiArray, Int8
import cv2, base64, numpy as np
from cv_bridge import CvBridge
from sensor_msgs.msg import Image
import math



# from custom_msgs.msg import OperationActivate
# import your_processing_functions 

# from your_processing_functions import (
#     Hedef_tespit_etmm,
#     maskeleme_ve_ayirma,
#     maskeleme_ve_ayirma_manuel,
#     Dusman_tespit_etmm,
#     Dost_tespit_etmm,
#     build_mask
# )

def hedefler_yeniden_siralama( hedeflerin_konumlari):
        center_x, center_y = 640 / 2, 480 / 2
        return sorted(hedeflerin_konumlari, key=lambda p: math.hypot(p[0] - center_x, p[1] - center_y))
def draw_target(frame,
                circle_radius=30,
                line_length=20,
                line_thickness=2,
                color_main=(102, 255, 102),   # Sarı (BGR)
                color_center=(0, 200, 200)  # Ortadaki sembol için (açık turuncu/altın)
                ):
    """
    Görüntünün ortasına profesyonel nişan sembolü çizer.
    """
    h, w = frame.shape[:2]
    cx, cy = w // 2, h // 2

    # --- Dış daire ---
    # cv2.circle(frame, (cx, cy), circle_radius, color_main, line_thickness, lineType=cv2.LINE_AA)

    # --- Dört ana çizgi (daireyi kesen) ---
    # üst
    cv2.line(frame, (cx, cy - circle_radius),
             (cx, cy - circle_radius - line_length),
             color_main, line_thickness, lineType=cv2.LINE_AA)
    # alt
    cv2.line(frame, (cx, cy + circle_radius),
             (cx, cy + circle_radius + line_length),
             color_main, line_thickness, lineType=cv2.LINE_AA)
    # sol
    cv2.line(frame, (cx - circle_radius, cy),
             (cx - circle_radius - line_length, cy),
             color_main, line_thickness, lineType=cv2.LINE_AA)
    # sağ
    cv2.line(frame, (cx + circle_radius, cy),
             (cx + circle_radius + line_length, cy),
             color_main, line_thickness, lineType=cv2.LINE_AA)

    # --- Ortadaki küçük kare ---
    square_size = 12
    top_left = (cx - square_size // 2, cy - square_size // 2)
    bottom_right = (cx + square_size // 2, cy + square_size // 2)
    cv2.rectangle(frame, top_left, bottom_right, color_center, -1, lineType=cv2.LINE_AA)

    # --- Ortadaki dört kısa çizgi (karenin etrafında) ---
    inner_len = 8
    inner_gap = square_size // 2 + 4
    t = max(2, line_thickness // 2)

    # üst
    cv2.line(frame, (cx, cy - inner_gap - inner_len),
             (cx, cy - inner_gap),
             color_center, t, lineType=cv2.LINE_AA)
    # alt
    cv2.line(frame, (cx, cy + inner_gap),
             (cx, cy + inner_gap + inner_len),
             color_center, t, lineType=cv2.LINE_AA)
    # sol
    cv2.line(frame, (cx - inner_gap - inner_len, cy),
             (cx - inner_gap, cy),
             color_center, t, lineType=cv2.LINE_AA)
    # sağ
    cv2.line(frame, (cx + inner_gap, cy),
             (cx + inner_gap + inner_len, cy),
             color_center, t, lineType=cv2.LINE_AA)

    return frame

def Hedef_tespit_etmm(BirlesikMaske, img, algilama_hassasiyeti):
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (1,1))
    closed = cv2.dilate(BirlesikMaske, kernel, iterations=1)
    # İlk olarak orijinal maskeden uygun konturları bul
    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # Dolgu maskesi oluştur
    mask_filled = np.zeros_like(BirlesikMaske, dtype=np.uint8)
    for cnt in contours:
        hull = cv2.convexHull(cnt)
        cv2.drawContours(mask_filled, [hull], -1, 255, thickness=cv2.FILLED)
    # Doldurulmuş maskede yeniden kontur bul
    filled_contours, _ = cv2.findContours(mask_filled, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    merkezler = []
    for cnt in filled_contours:
        if cv2.contourArea(cnt) < algilama_hassasiyeti:
            continue
        # print(cv2.contourArea(cnt))
        per = cv2.arcLength(cnt, True)
        circ = (4 * np.pi * cv2.contourArea(cnt)) / (per**2 + 1e-5)
        if circ > 0.84:
            M = cv2.moments(cnt)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
            else:
                x, y, w, h = cv2.boundingRect(cnt)
                cx, cy = x + w//2, y + h//2
            # Görüntü üzerine çizim
            merkezler.append([cx, cy])
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 240), 2)
            cv2.putText(img, "Hedef", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,255), 2)
    return {"merkezler": merkezler}     #{"hedef maske": mask_filled,    "merkezler": merkezler}

def build_mask(hsv, lower, upper):
    mask   = cv2.inRange(hsv, lower, upper)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
    mask   = cv2.morphologyEx(mask, cv2.MORPH_OPEN,  kernel)
    mask   = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    return mask

def maskeleme_ve_ayirma_manuel(frameHSV):
    hsv = frameHSV
    # Kırmızı alt/üst sınırlar
    lower_red1 = np.array([0, 120, 70])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 120, 70])
    upper_red2 = np.array([180, 255, 255])
    # Mavi alt/üst sınırlar
    lower_blue = np.array([100, 100,  100])
    upper_blue = np.array([140, 255, 255])

    # Maskeleri oluştur ve temizle
    m1 = build_mask(hsv, lower_red1, upper_red1)
    m2 = build_mask(hsv, lower_red2, upper_red2)
    mask_kirmizi = cv2.bitwise_or(m1, m2)
    mask_mavi    = build_mask(hsv, lower_blue, upper_blue)

    birlesik_maske=cv2.bitwise_or(mask_kirmizi,mask_mavi)

    return birlesik_maske

def maskeleme_ve_ayirma(frameHSV, dusman_rengi):
    hsv = frameHSV
    # Kırmızı alt/üst sınırlar
    lower_red1 = np.array([0, 120, 70])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 120, 70])
    upper_red2 = np.array([180, 255, 255])
    # Mavi alt/üst sınırlar
    lower_blue = np.array([100, 100,  100])
    upper_blue = np.array([140, 255, 255])

    # Maskeleri oluştur ve temizle
    m1 = build_mask(hsv, lower_red1, upper_red1)
    m2 = build_mask(hsv, lower_red2, upper_red2)
    mask_kirmizi = cv2.bitwise_or(m1, m2)
    mask_mavi    = build_mask(hsv, lower_blue, upper_blue)

    if dusman_rengi.strip().lower() == "kirmizi":
        return {"Dusman": mask_kirmizi, "Dost": mask_mavi}
    else:
        return {"Dusman": mask_mavi,    "Dost": mask_kirmizi}  

def Dusman_tespit_etmm(Dusman_maske, img, algilama_hassasiyeti):
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (1,1))
    closed = cv2.dilate(Dusman_maske, kernel, iterations=1)
    # İlk olarak orijinal maskeden uygun konturları bul
    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # Dolgu maskesi oluştur
    mask_filled = np.zeros_like(Dusman_maske, dtype=np.uint8)
    for cnt in contours:
        hull = cv2.convexHull(cnt)
        cv2.drawContours(mask_filled, [hull], -1, 255, thickness=cv2.FILLED)
    # Doldurulmuş maskede yeniden kontur bul
    filled_contours, _ = cv2.findContours(mask_filled, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    merkezler = []
    for cnt in filled_contours:
        if cv2.contourArea(cnt) < algilama_hassasiyeti:
            continue
        # print(cv2.contourArea(cnt))
        per = cv2.arcLength(cnt, True)
        circ = (4 * np.pi * cv2.contourArea(cnt)) / (per**2 + 1e-5)
        if circ > 0.84:
            M = cv2.moments(cnt)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
            else:
                x, y, w, h = cv2.boundingRect(cnt)
                cx, cy = x + w//2, y + h//2
            # Görüntü üzerine çizim
            merkezler.append([cx, cy])
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 240), 2)
            cv2.putText(img, "Dusman", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,255), 2)
    return {"merkezler": merkezler} #{"dusman maske": mask_filled,   "merkezler": merkezler}

def Dost_tespit_etmm(Dost_maske, img, algilama_hassasiyeti, label="Dost"):
    # İlk olarak orijinal maskeden uygun konturları bul
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (1,1))
    closed = cv2.dilate(Dost_maske, kernel, iterations=1)
    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # Dolgu maskesi oluştur
    mask_filled = np.zeros_like(Dost_maske, dtype=np.uint8)
    for cnt in contours:
        hull = cv2.convexHull(cnt)
        cv2.drawContours(mask_filled, [hull], -1, 255, thickness=cv2.FILLED)
    # Doldurulmuş maskede yeniden kontur bul
    filled_contours, _ = cv2.findContours(mask_filled, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in filled_contours:
        if cv2.contourArea(cnt) < algilama_hassasiyeti:
            continue
        per = cv2.arcLength(cnt, True)
        circ = (4 * np.pi * cv2.contourArea(cnt)) / (per**2 + 1e-5)
        if circ > 0.84:
            M = cv2.moments(cnt)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
            else:
                x, y, w, h = cv2.boundingRect(cnt)
                cx, cy = x + w//2, y + h//2
            # Görüntü üzerine çizim
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 240), 2)
            cv2.putText(img, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,255), 2)
    # return mask_filled


class ImageProcessingNode(Node):
    def __init__(self):
        super().__init__('image_processing_node')

        # Subscriptions
        self.create_subscription(Image, '/camera0/image_raw', self.image_callback, 10)
        # self.create_subscription(OperationActivate, '/operation/activate', self.operation_callback, 10)
        # self.create_subscription(Int32, '/processing/sensitivity', self.sensitivity_callback, 10)

        self.get_logger().info('✅ Image Processing Node initialized.')

        # Publishers
        self.publisher_centers = self.create_publisher(Float32MultiArray, '/camera/targets', 10)
        self.targets_no_publisher=self.create_publisher(Int8,"target_no",10)
        # self.publisher_image = self.create_publisher(String, '/image_processed_base64', 10)

        # Dynamic Parameters
        self.latest_rengi = "kirmizi"
        self.latest_durum = "Tam Otomatik"

        # Frame placeholders
        self.frameHSV = None
        self.algilama_hassasiyeti=300
        self.targets_no=0

        # self.algilama_hassasiyeti = 200

        self.bridge = CvBridge()

    # def operation_callback(self, msg):
    #     try:
    #         mode = msg.operation_mode.strip()
    #         detection_mode = msg.detection_mode.strip()
    #         target = msg.target.strip()
    #         color = msg.color.strip()
    #         friend_color = msg.friend_color.strip()
    #         enemy_color = msg.enemy_color.strip()

    #         if not mode:
    #             mode = "Tam Otomatik"
    #         if not color:
    #             color = "kirmizi"

    #         self.latest_durum = mode
    #         self.latest_rengi = enemy_color
            
    #         self.get_logger().info(f'✅ Operation Updated → Mode: {self.latest_durum}, Color: {self.latest_rengi}, friend_color: {friend_color}, enemy_color: {enemy_color}, detection_mode: {detection_mode}')
    #     except Exception as e:
    #         self.get_logger().error(f"❌ Invalid operation/create message: {e}")


    # def sensitivity_callback(self, msg):
    #     self.algilama_hassasiyeti = msg.data
    #     self.get_logger().info(f'📶 Sensitivity updated: {self.algilama_hassasiyeti}')

    def image_callback(self, msg):
        # decoded_data = base64.b64decode(msg.data)
        # nparr = np.frombuffer(decoded_data, np.uint8)
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        if frame is None or frame.size == 0:
            self.get_logger().error('❌ Invalid frame from Base64, skipping.')
            return
        def preprocess(frame):
            blur = cv2.GaussianBlur(frame, (7,7), 0)
            hsv  = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
            h, s, v = cv2.split(hsv)
            clahe   = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            v_eq    = clahe.apply(v)
            return cv2.merge((h, s, v_eq))

        self.frameHSV = preprocess(frame)

        result_centers = []

        # Processing Logic
        if self.latest_durum == "Tam Otomatik":
            # self.get_logger().info(f'Tam Otomatik girdi ')
            masks = maskeleme_ve_ayirma(self.frameHSV, self.latest_rengi)
            Dost_maske = masks["Dost"]
            Dusman_maske = masks["Dusman"]
            Dost_tespit_etmm(Dost_maske, frame, self.algilama_hassasiyeti)
            result = Dusman_tespit_etmm(Dusman_maske, frame, self.algilama_hassasiyeti)
            result_centers = result.get("merkezler", [])


        elif self.latest_durum == "Manuel":
            self.get_logger().info(f'Manuel girdi')
            if self.latest_rengi == "hepsi":
                HedefMaskesi = maskeleme_ve_ayirma_manuel(self.frameHSV)
                Hedef_tespit_etmm(HedefMaskesi, frame, self.algilama_hassasiyeti)
            elif self.latest_rengi == "mavi":
                masks = maskeleme_ve_ayirma(self.frameHSV, "mavi")
                HedefMaskesi = masks["Dusman"]
                Dost_tespit_etmm(HedefMaskesi, frame, self.algilama_hassasiyeti, "Hedef")
            elif self.latest_rengi == "kirmizi":
                masks = maskeleme_ve_ayirma(self.frameHSV, "kirmizi")
                HedefMaskesi = masks["Dusman"]
                Dost_tespit_etmm(HedefMaskesi, frame, self.algilama_hassasiyeti, "Hedef")

        elif self.latest_durum == "Yari Otomatik":
            self.get_logger().info(f'Yari Otomatik girdi')
            mask = maskeleme_ve_ayirma_manuel(self.frameHSV)
            result = Hedef_tespit_etmm(mask, frame, self.algilama_hassasiyeti)
            result_centers = result.get("merkezler", [])

        # Publish Detected Centers (Float32MultiArray)
        # self.get_logger().info(f'✅ Operation gondermek uzere (Float32MultiArray)')
        result_centers=hedefler_yeniden_siralama(result_centers)
        out_msg = Float32MultiArray()
        # # Flatten list of tuples [(x1,y1), (x2,y2)] → [x1, y1, x2, y2]
        out_msg.data = [float(x) for center in result_centers for x in center]
        
        # print(result_centers)
        self.publisher_centers.publish(out_msg)

        # self.get_logger().info(f'✅ Gonderildi: {out_msg.data}')

        # if result_centers:
        #     self.get_logger().info(f'✅ Merkezler gonderildi: {out_msg.data}')
        # else:
        #     self.get_logger().info('⚠️ No targets detected — sent empty center list.')

        
        cv2.imshow("processed image", draw_target(frame))

        key = cv2.waitKey(1) & 0xFF  # en son 8 bitini al
        cv2.waitKey(1)
        if key == ord('n'): 
            self.targets_no=+1

            if self.targets_no == len(result_centers):
                self.targets_no=0
        if key == ord('z'): 
            self.targets_no=0
        if key == ord('s'): 
            self.targets_no=len(result_centers)-1
            

         

        targets_msg=Int8()
        targets_msg.data=self.targets_no
        self.targets_no_publisher.publish(targets_msg)

        

        

           
        
        


        # Publish Processed Image Back to WPF
        # _, buffer = cv2.imencode('.jpg', frame)
        # base64_str = base64.b64encode(buffer).decode('utf-8')
        # image_msg = String()
        # image_msg.data = base64_str
        # self.publisher_image.publish(image_msg)


def main():
    rclpy.init()
    node = ImageProcessingNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
