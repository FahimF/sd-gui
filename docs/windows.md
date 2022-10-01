# Windows Installation

There are some pre-requisites that must be in place before you can install the SD GUI code and run it.

## Pre-requisites

You might not need all of the following pre-requisites, but it might be helpful to have them in place before you try to install the app. But if you are familiar with the command-line and know what you are doing, feel free to pick and choose as necessary 🙂

Also do note that you might have these already installed. If so, then you don't have to do anything. The following instructions in this section are for people who have pristine systems which do not have the pre-requisites installed.

### CUDA Toolkit

If you have an NVIDIA graphics card, you will need the CUDA Toolkit installed in order to use your GPU in your Python code. If you don't have the CUDA Toolkit installed, go here and follow the instructiont to install the CUDA Toolkit:

https://developer.nvidia.com/cuda-downloads

### miniconda

[Miniconda](https://docs.conda.io/en/latest/miniconda.html) is an installer/package manager for Python. It allows you to have multiple environments for different Python apps/tasks and to be able to mix and match different Python versions as required.

You can download the Miniconda installer for your OS platform from this page:

https://docs.conda.io/en/latest/miniconda.html

Note that there are a lot of options (and different OS versions) on that page. So make sure to go through the full list and pick the right version of the installer 🙂

While you don't strictly need Miniconda to install the SD GUI app, having it installed will make your life easier and prevent you messing up your existing Python install and packages, or running into various version conflicts with any of your existing installs.

### Git (and git-lfs)

[Git](https://git-scm.com/) is a version control system. Basically, it's what coders use to manage the different versions of their source code. So why do you need it? Because GitHub uses Git and so you'll need to use Git in order to download the code for the SD GUI repo (short for repository) and and to get the SD model data, which is in a different repo.

Git-lfs adds large file support so that you can download large files in an optimized fashion from a Git repo. Since the SD model is stored using git-lfs, you will need git-lfs to corectly download the data from the SD repo.

You can download the installer for Git from here:

https://git-scm.com/download/win

That's it! You should now be set for installing and running the code from this repo 🙂

## Installation

If you are familiar with Python, minconda, and the terminal and have git and git-lfs installed, you should be able to get going by using the following commands (or variants thereof) from a command prompt. 

**Note:** Make sure to be in the folder where you want the code to be placed before you run the following commands.

```bash
# Create and activate new conda environment named ml
conda config --append channels conda-forge
conda create -n ml python=3.9.13
conda activate ml

# Install the needed Python packages
conda install pyqt
conda install torch -c pytorch-nightly
conda install -c conda-forge transformers diffusers ftfy flask scipy
pip install opencv-python

# Clone this repo and create output folder
git clone https://github.com/FahimF/sd-gui.git
cd sd-gui
mkdir output

# Clone the Hugging Face model repo - you will need the Hugging Face user and password for this step
git lfs install
git clone https://huggingface.co/CompVis/stable-diffusion-v1-4
```
