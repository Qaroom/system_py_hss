import cv2
import numpy as np




def Hedef_tespit_etmm(BirlesikMaske, img, algilama_hassasiyeti):
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (1,1))
    closed = cv2.dilate(BirlesikMaske, kernel, iterations=1)
    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    mask_filled = np.zeros_like(BirlesikMaske, dtype=np.uint8)
    for cnt in contours:
        hull = cv2.convexHull(cnt)
        cv2.drawContours(mask_filled, [hull], -1, 255, thickness=cv2.FILLED)
    filled_contours, _ = cv2.findContours(mask_filled, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    merkezler = []
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
    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    mask_filled = np.zeros_like(Dusman_maske, dtype=np.uint8)
    for cnt in contours:
        hull = cv2.convexHull(cnt)
        cv2.drawContours(mask_filled, [hull], -1, 255, thickness=cv2.FILLED)
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
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (1,1))
    closed = cv2.dilate(Dost_maske, kernel, iterations=1)
    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    mask_filled = np.zeros_like(Dost_maske, dtype=np.uint8)
    for cnt in contours:
        hull = cv2.convexHull(cnt)
        cv2.drawContours(mask_filled, [hull], -1, 255, thickness=cv2.FILLED)
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
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 240), 2)
            cv2.putText(img, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,255), 2)
