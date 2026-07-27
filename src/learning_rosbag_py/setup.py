from setuptools import find_packages, setup

package_name = 'learning_rosbag_py'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='zhangwenjing',
    maintainer_email='924110800235@njust.edu.cn',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'bag_recoder = learning_rosbag_py.bag_recoder:main',
            'bag_player = learning_rosbag_py.bag_player:main'
        ],
    },
)
