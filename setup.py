from setuptools import setup
from pathlib import Path
import shutil
import os

root = Path(__file__).parent

pkg_data = root / "src" / "gui" / "data"
pkg_data.mkdir(parents=True, exist_ok=True)

# project.yaml
yaml_src = root / "project.yaml"
if yaml_src.exists():
    shutil.copy2(yaml_src, pkg_data / "project.yaml")

# все *.rcc
for rcc_file in root.glob("*.rcc"):
    shutil.copy2(rcc_file, pkg_data / rcc_file.name)

setup(
    name="pysca-hmi",
    package_dir={"": "src"},
    packages=["gui"],
    include_package_data=True,
)