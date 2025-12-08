from pathlib import Path
from setuptools import setup, find_packages

HERE = Path(__file__).parent

# Long description from README if available
long_description = ""
readme_path = HERE / "README.md"
if readme_path.exists():
	long_description = readme_path.read_text(encoding="utf-8")

# Read install requirements from requirements.txt if present
requirements = []
req_path = HERE / "requirements.txt"
if req_path.exists():
	requirements = [r.strip() for r in req_path.read_text(encoding="utf-8").splitlines() if r.strip() and not r.strip().startswith("#")]

setup(
	name="taxmate",
	version="0.0.0",
	description="Taxmate — Indian tax assistant",
	long_description=long_description,
	long_description_content_type="text/markdown",
	author="taxmate",
	packages=find_packages(where="src"),
	package_dir={"": "src"},
	include_package_data=True,
	install_requires=requirements,
	python_requires=">=3.9",
	zip_safe=False,
)

