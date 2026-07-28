from setuptools import find_packages, setup

package_name = 'learning_tf_py'

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
            'static_tf_broadcaster = learning_tf_py.static_tf_broadcaster:main',
            'dynamic_tf_broadcaster = learning_tf_py.dynamic_tf_broadcaster:main',
            'point_publisher = learning_tf_py.point_publisher:main',
        ],
    },
)
