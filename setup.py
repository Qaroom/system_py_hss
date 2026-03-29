from setuptools import find_packages, setup
from glob import glob

package_name = 'system_py_hss'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ros2',
    maintainer_email='ros2@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            "systemkeyboarcontrol=system_py_hss.system_keyboard_control:main",
            "trajctorypublisher=system_py_hss.trajctorypublisher:main",
            "image_prossising_node=system_py_hss.image_prossising_node:main",
            "move_system_to_target=system_py_hss.move_system_to_target:main",
            "dual_pid_controller=system_py_hss.dual_pid_controller:main"
        ],
    },
)