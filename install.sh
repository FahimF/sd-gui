#!/bin/bash
read  -n 1 -p "Create conda environment (y/n)?" input
if [[ $input = n ]] ; then
	printf "\nBypassing environment creation ...\n"
else
	conda create -n ml python=3.9.13	
fi
read  -n 1 -p "Activate new conda environment (y/n)?" input
if [[ $input = n ]] ; then
	printf "\nBypassing environment activation ...\n"
else
	# conda activate mlnew
	source "/Users/$USER/miniforge3/bin/activate" ml
fi
read  -n 1 -p "Continue (y/n)?" input
if [[ $input = n ]] ; then
	printf "\nQuitting ...\n"
	exit
fi
conda install pytorch -c pytorch-nightly -y
conda install pyqt -y
conda install -c conda-forge transformers diffusers ftfy flask scipy -y
pip install opencv-python
read  -n 1 -p "Revert PyTorch to good nightly (y/n)?" input
if [[ $input = n ]] ; then
	printf "\nQuitting ...\n"
	exit
fi
pip install --pre -r requirements.txt -f https://download.pytorch.org/whl/nightly/torch_nightly.html
read  -n 1 -p "Download the Stable Diffusion model (y/n)?" input
if [[ $input = n ]] ; then
	printf "\nQuitting ...\n"
	exit
fi
git lfs install
git clone https://huggingface.co/CompVis/stable-diffusion-v1-4