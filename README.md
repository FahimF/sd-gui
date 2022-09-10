# Stable Diffusion for Apple Silicon

This repo is my work on getting Stable Diffusion working on Apple Silicon macs by keeping things as simple as possible. The requirements are kept as simple as possible and probably the most complicated thing is the GUI which allows you to set up all your image generation parameters on a GUI whether you are on a Mac, Linux, or Windows.

**Note:** All development has been done on an Apple Silicon Mac and this has been optimized for Apple Silicon. I don't know if it will work on an Intel Mac or not and no testing has been done on any other platform but it should (theoretically) work on other platforms too.

![gui](assets/gui.jpg)

## Installation

You will need the following:

* An Apple Silicon mac (has not been tested on anything else)
* macOS 12.3 Monterey or later
* Python

Before you start your installation, you might also want to sign up at [Hugging Face](https://huggingface.co/) since you'll need a Hugging Face user account in order to download the Stable Diffusion models.

To get set up, you'll need to run the following commands in terminal one at a time. Do note that some of these commands would require you to make decisions and respond to prompts. If you are not comforable with that, this process might not be for you 🙂

There is some limited information which might help you in this blog post, but that too doesn't go into a lot of detail: https://write.farook.org/adventures-in-imagineering-mining-the-apple-silicon/

**Note:** Make sure you are in the folder location where you want to have this repo before you start running the following commands.

```bash
# install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install miniconda to manage your Python environments
/bin/bash -c "$(curl -fsSL https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh)"

# Create and activate new conda environment named ml
conda create -n ml python=3.8
conda activate ml

# Install the needed Python packages
conda install pytorch torchvision torchaudio -c pytorch-nightly
conda install transformers
conda install -c conda-forge diffusers
conda install fastcore
conda install ftfy

# Install git and git-lfs via Homebrew
brew install git git-lfs

# Clone this repo
git clone https://github.com:FahimF/sd-gui.git
cd sd-gui

# Clone the Hugging Face model repo - you will need the Hugging Face user and password for this step
git clone https://huggingface.co/CompVis/stable-diffusion-v1-4
```

If all of the above worked correctly and there were no issues, then you should be set 🙂

If you are still at the terminal, simply type the following to launch the UI:

```
python gui.py
```

If you closed the terminal or want to use the UI at some other point, you'd have to navigate back to where you have this repo (`sd-gui`) before you run the above command.