from setuptools import find_packages, setup
from glob import glob

package_name = 'learning_launch_py'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch/py',
            glob('launch/py/*_launch.py')),
        ('share/' + package_name + '/launch/xml',
            glob('launch/xml/*_launch.xml')),
        ('share/' + package_name + '/launch/yaml',
            glob('launch/yaml/*_launch.yaml')),
        ('share/' + package_name + '/config', glob('config/*.yaml')),
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
        ],
    },
)
