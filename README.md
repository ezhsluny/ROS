# Task 3

## ex01/
- [full_name_pkg/](https://github.com/ezhsluny/ROS/tree/task3/ex01/full_name_pkg) - шаблон из предыдущего модуля
- [service_full_name/](https://github.com/ezhsluny/ROS/tree/task3/ex01/service_full_name) - основная реализация (сервис и клиент)

### Файловая структура
```
├── full_name_pkg
│   ├── CMakeLists.txt
│   ├── include
│   │   └── full_name_pkg
│   ├── LICENSE
│   ├── msg
│   │   └── FullNameMessage.msg
│   ├── package.xml
│   ├── src
│   └── srv
│       └── FullNameSumService.srv
├── service_full_name
│   ├── LICENSE
│   ├── package.xml
│   ├── resource
│   │   └── service_full_name
│   ├── service_full_name
│   │   ├── client_node.py
│   │   ├── __init__.py
│   │   └── service_node.py
│   ├── setup.cfg
│   ├── setup.py
│   └── test
│       ├── test_copyright.py
│       ├── test_flake8.py
│       └── test_pep257.py
```

1. Сборка пакета
```bash
cd ~/ros2_ws
colcon build --packages-select service_full_name
```

2. Запуск сервиса
```bash
ros2 run service_full_name service_name
```

3. Запуск клиента (в другом терминале)
```bash
ros2 run service_full_name client_name Иванов Иван Иванович
```

4. Пример вывода (для сервиса):
```bash
[INFO] [service_name]: Service SummFullName is ready and waiting for requests...
[INFO] [service_name]: Received request:
  Last name: Иванов
  Name: Иван
  First name: Иванович
Generated full name: "Иванов Иван Иванович"
```
