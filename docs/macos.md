# macOS Installation

You will need the following:

* An Apple Silicon or Intel mac
* macOS 12.3 Monterey or later
* Python 3.9+ (The app was developed and tested on Python 3.9 but should work on newer versions too.)

There is some limited information regarding running on Apple Silicon in this blog post, but it doesn't go into a lot of detail: https://write.farook.org/adventures-in-imagineering-mining-the-apple-silicon/ Please read it if you are stuck and see if any of the issues listed there are relevant to your particular case.

There are some pre-requisites that must be in place before you can install the SD GUI code and run it.

## Pre-requisites

You might not need all of the following pre-requisites, but it might be helpful to have them in place before you try to install the app. But if you are familiar with the command-line and know what you are doing, feel free to pick and choose as necessary 🙂

Also do note that you might have these already installed. If so, then you don't have to do anything. The following instructions in this section are for people who have pristine systems which do not have the pre-requisites installed.

### Homebrew

[Homebrew](https://brew.sh/) is known as the missing package manager for macOS. It simply allows you to install software on a mac easily via the command line. You can install it via the following command issued from the terminal:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

You will need Homebre in order to install git and git-lfs, which you'll need further on to install both the GUI app and the Stable Diffusion models.

### miniconda

[Miniconda](https://docs.conda.io/en/latest/miniconda.html) is an installer/package manager for Python. It allows you to have multiple environments for different Python apps/tasks and to be able to mix and match different Python versions as required.

To install Miniconda, you need the wget command, which you can install using Homebrew (which you should have installed above) by runing the following command in terminal:

```bash
brew install wget
```

Next, you download the Miniconda installer using wget via the terminal:

```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh -O miniconda.sh
```

**Note:** The above command is for Apple Silicon (arm64). If you want to install Miniconda on an Intel mac, then use the following command:

```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh
```

Finally, you install Miniconda by running the following two commands from the terminal:

```bash
chmod +x miniconda.sh
./miniconda.sh
```

Once the above process completes, you will need to quit your terminal session and restart the terminal before the conda command is available to you. So don't forget to exit the terminal and to restart it again before continuing on.

After you restar the terminal, you can verify if conda is properly install by running the following command in the terminal:

```bash
conda
```

If you get a "command not found" error, then you do not have conda installed properly. But if you get output from conda (generally the conda help), then you are all set to move on to the next step 🙂

**Note:** If the above process fails or you run into issues, please go to the Miniconda site and follow their detailed installation doc here:

https://docs.conda.io/projects/conda/en/latest/user-guide/install/macos.html

While you don't strictly need Miniconda to install the SD GUI app, having it installed will make your life easier and prevent you messing up your existing Python install and packages, or running into various version conflicts with any of your existing installs.

### Git (and git-lfs)

[Git](https://git-scm.com/) is a version control system. Basically, it's what coders use to manage the different versions of their source code. So why do you need it? Because GitHub uses Git and so you'll need to use Git in order to download the code for the SD GUI repo (short for repository) and and to get the SD model data, which is in a different repo.

Git-lfs adds large file support so that you can download large files in an optimized fashion from a Git repo. Since the SD model is stored using git-lfs, you will need git-lfs to corectly download the data from the SD repo.

You can install Git by using Homebrew (via the terminal) as follows:

```bash
brew install git git-lfs
```

That's it! You should now be set for installing and running the code from this repo 🙂

## Installation

There are two different ways you can install. Well, to be accurate, there are many different ways you can install but there are two detailed in this document 😛

### Install script

There's an installer bash script which will prompt you at the relevant points and do the whole install automatically for you. If you are not familiar with the command-line or conda, this might be the best option for you.

**Caveat:** If you are not familiar with miniconda and/or the terminal, this might be too much trouble at this point since I've discovered a bunch of issues with the script after other people tested it. Sorry 😞 So try the manual install or if you wait a few days, I'll try to get the installer issues fixed and a new one out that will work much better.

Do note though that the installer is not well tested and has very little error handling. If it works, fine. If not, you would still need to figure out why the installer failed or try the manual installation steps in the next section.

To run the automated installer, you'd need to download the code from this repo first. So open the terminal, navigate to the folder where you want to place the code from this repo and run the following command:

```bash
git clone https://github.com/FahimF/sd-gui.git
```



Next, while still at the terminal, run the following commands to change over to the source code folder and run the installer:

```bash
cd sd-gui
./install.sh
```

That's about it! If it works, then you are all set.

### Manual Install

You have to open terminal and run the following commands for each step of the installation process to get everything set up. It's more work but you have more control over what is installed and what is not or how you do certain things.

**Note:** Make sure you are in the folder location where you want to have this repo before you start running the following commands.

```bash
# Create and activate new conda environment named ml
conda config --append channels conda-forge
conda create -n ml python=3.9.13
conda activate ml

# Install the needed Python packages
conda install pyqt
conda install pytorch -c pytorch-nightly
conda install -c conda-forge transformers diffusers ftfy flask scipy
pip install opencv-python scikit-image darkdetect

# Clone this repo and create output folder
git clone https://github.com/FahimF/sd-gui.git
cd sd-gui
mkdir output

# Clone the Hugging Face model repo - you will need the Hugging Face user and password for this step
git lfs install
git clone https://huggingface.co/CompVis/stable-diffusion-v1-4
```

If all of the above worked correctly and there were no issues, then you should be set 🙂

# macOS Screenshots

Here are some screenshots of the GUI that you'll be able to see after all of that effort 🙂

|            ![01-main](../screens/mac-01-main.jpg)            |
| :----------------------------------------------------------: |
|              The main tab for generating images              |
|          ![02-editor](../screens/mac-02-editor.jpg)          |
|   The editor tab for in/outpainting or doing basic editing   |
|         ![03-prompts](../screens/mac-03-prompts.jpg)         |
|      The prompts tab for editing prompts and modifiers       |
|         ![04-gallery](../screens/mac-04-gallery.jpg)         |
| The gallery tab for viewing all output images and their prompts |
