# iMarker Detector Standalone (with GUI)

![Demo](docs/demo.png "Demo")

This repository contains the GUI-enabled standalone version of **iMarker detector**. It functions as a wrapper for iMarker [detector sensors](https://github.com/snt-arg/csr_sensors) and [algorithms](https://github.com/snt-arg/csr_detector).

## 🛠️ Getting Started

### I. Cloning the Repository

When cloning the repository include `--recurse-submodules` after `git clone` to also include the submodules. You can use the command below:

```
git clone --recurse-submodules git@github.com:snt-arg/csr_detector_standalone.git
```

You can also get the latest changes of each submodule individually using the command `git pull --recurse-submodules`.

💡 **[note]** In case you do not have SSH access, you can just download the code of [this library](https://github.com/snt-arg/csr_detector_standalone), and clone the [detector sensors](https://github.com/snt-arg/csr_sensors) inside `src/csr_sensors`, and [detector algorithms repo](https://github.com/snt-arg/csr_detector) inside `src/csr_detector` paths.

### II. Installation

After cloning the repository, you need to install the required dependencies. The Python version used while developing the framework is `3.10.4`. It is highly recommended to create a Python virtual environment using `python -m venv .venv`, activate it using `source .venv/bin/activate`, and then install the required dependencies in the `requirements.txt` using the below command:

```
pip install -r requirements.txt
```

You can also install the cloned submodules and define dependencies and other distribution-related configurations using the provided `setup.py` file in the root directory of each file. Hence, follow the below steps:

- Go to `src/csr_sensors` and run `pip install -e .`,
- Go to `src/csr_detector` and run `pip install -e .`,
- Go to the **root directory** and run `pip install -e .` to install the package and its dependencies.

## 🚀 Running the Code

### I. Set Configurations

The first step is to modify the configuration file. For a complete list of configurations you can take a look at [config.yaml](/config/config.yaml) or read the detailed descriptions [here](/config/README.md).

### II. Run the Desired Mode

The current version of the framework you can run various modes, including offline images (`"offimg"`), offline videos (`"offvid"`), double-vision USB cameras (`"usb"`), double-vision iDS cameras (`"ids"`), or single-vision RealSense camera (`"rs"`). You can set it in the configuration file.

For single vision sensors (`"rs"`, `"offimg"`, or `"offvid"`) the parameter `temporalSubtraction` can be set to run in **sequential subtraction** or **masking** modes.

Then, go to the root of the project and run `[~/.venv/bin/python] main.py`. The code automatically picks the proper runner for it.

💡 **[note]** You can also set the mode value using the arguments, as shown below:

```python
# Activate the .venv
source .venv/bin/activate

# Option 1: Normal running
[~/.venv/bin/python] main.py

# Option 2: Changing the mode using argument and then run
# [hint] Pick from ["offimg", "offvid", "usb", "ids", "rs"]
[~/.venv/bin/python] main.py --mode rs
```
