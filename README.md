# system_py_hss

`system_hss` robotu için Python tabanlı ROS 2 kontrol ve algoritma paketi.  
Klavyeden teleoperasyon, yörünge yayını, görüntü işleme, hedefe hareket ve PID kontrol node'larını içerir.

> Bu paket, [`system_hss`](https://github.com/Qaroom/system_hss) (URDF + Gazebo + `ros2_control` simülasyon paketi) ile birlikte kullanılmak üzere tasarlanmıştır.

## Node'lar

| Komut | Açıklama |
|---|---|
| `systemkeyboarcontrol` | Klavyeden teleoperasyon ile robotun manuel kontrolü |
| `trajctorypublisher` | Eklem yörüngelerini (`JointTrajectory`) yayımlar |
| `image_prossising_node` | Kamera görüntülerini işleyen görüntü işleme node'u |
| `move_system_to_target` | Robotu belirli bir hedef noktaya götüren node |
| `dual_pid_controller` | İki ayrı eksen için PID denetleyici |

## Yapı

```
system_py_hss/
├── launch/            # ROS 2 launch dosyaları
├── resource/          # ament_python kaynak işaretçisi
├── system_py_hss/     # Python kaynak kodu (node'lar)
├── test/              # Lint ve birim testleri
├── package.xml
├── setup.cfg
└── setup.py
```

## Kurulum

Paketi bir ROS 2 workspace'ine klonlayıp derleyin:

```bash
cd ~/ros2_ws/src
git clone https://github.com/Qaroom/system_py_hss.git
cd ~/ros2_ws
colcon build --packages-select system_py_hss
source install/setup.bash
```

## Kullanım

Tek tek node'ları çalıştırmak için:

```bash
ros2 run system_py_hss systemkeyboarcontrol
ros2 run system_py_hss trajctorypublisher
ros2 run system_py_hss image_prossising_node
ros2 run system_py_hss move_system_to_target
ros2 run system_py_hss dual_pid_controller
```

Veya `launch/` klasöründeki bir launch dosyası ile birden fazla node'u birlikte başlatabilirsiniz:

```bash
ros2 launch system_py_hss <launch_file>.launch.py
```

Tam bir senaryo için önce `system_hss` paketiyle simülasyonu, sonra bu paketten ilgili kontrol/algoritma node'larını çalıştırın.

## Lisans

[MIT Lisansı](LICENSE)  
Copyright (c) 2026 Akram Al Qasemi
