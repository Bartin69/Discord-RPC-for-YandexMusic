from setuptools import setup, find_packages

setup(
    name="yandexmusicrpc",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "pypresence",
        "yandex-music",
        "psutil",
        "pystray",
        "pillow",
        "winsdk",
    ],
)