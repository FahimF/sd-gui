#!/bin/bash
read  -n 1 -p "Create conda environment (y/n)?" input
if [[ $input = n ]] ; then
	printf "\nBypassing environment creation ...\n"
else
	conda create -n mlnew python=3.9.13	
fi
read  -n 1 -p "Activate new conda environment (y/n)?" input
if [[ $input = n ]] ; then
	printf "\nBypassing environment activation ...\n"
else
	# conda activate mlnew
	source "/Users/$USER/miniforge3/bin/activate" mlnew
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