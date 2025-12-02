# Task 5

В ex05 реализовано уникальное движение робота: робот проезжает по прямой, вращается на месте на небольшой угол ("танцует"), поворачивается на 90 градусов и проезжает по прямой задом. В итоге получается 4-конечная звезда (немного съезжающая)

## Структура пакетов в ex05
```bash
gazebo_robot/
├── config/
│   ├── control.yaml
│   └── robot_bridge.yaml              # мост gazebo-rviz
├── gazebo_robot/
├── launch/
│   ├── circle_movement.launch.py      # launch файл для движения робота по кругу
│   ├── diff_drive.launch.py           # launch файл для движения робота (управление с клавиатуры)
│   └── fancy_square.launch.py         # launch файл для уникального движения робота
├── package.xml
├── resource/
├── robot.gazebo.xacro                 # xacro файл с плагинами gazebo
├── robot.urdf.xacro                   # xacro файл с описанием робота
├── rviz/
│   └── config.rviz                    # конфигурация отображения робота в rviz
├── setup.cfg
├── setup.py
├── test/
└── worlds/
    └── empty.world                    # файл мира для gazebo
```

```bash
gazebo_robot_circle/
├── gazebo_robot_circle/
│   ├── circle_movement.py             # движение по кругу
│   ├── __init__.py
│   └── line_dance.py                  # уникальное движение
├── package.xml
├── resource/
├── setup.cfg
├── setup.py
└── test/
```
