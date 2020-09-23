# Metadata extraction from German scientific papers 

This repository contains  a method of extraction metadata from  German scientific papers (PDF) using  [Detectron2](https://github.com/facebookresearch/detectron2) implementation and synthetic data of German publications. 
In this project we used an implementation of detectron2 that was trained with 200K images from PublayNet dataset ([model](https://github.com/hpanwar08/detectron2))and we re-finetuned it with 30k of our synthetic data.
Our model extracts nine metadata classes:Title, Author, Journal, Abstract, Affiliation, Email, Address, DOI, Date.
## Data

 ## Installation
 #### Using google Colaboratory:
 This [colab] (https://colab.research.google.com/drive/16jcaJoc6bCFAQ96jDe2HwtXj7BMD_-m5)notebook has all the steps and instructions to install Detectron2
 #### Using docker:
 This [dockerfile ](https://github.com/facebookresearch/detectron2/blob/master/docker/Dockerfile) also installs detectron2 with a few simple commands.
 #### Locally
 ##### Requirements:
 - Linux or macOS
 - Python ≥ 3.6
 - PyTorch ≥ 1.3
 - [torchvision](https://github.com/pytorch/vision/) that matches the PyTorch installation.
     You can install them together at [pytorch.org](https://pytorch.org) to make sure of this.
 - OpenCV, needed by demo and visualization
 - pycocotools: `pip install cython; pip install 'git+https://github.com/cocodataset/cocoapi.git#subdirectory=PythonAPI'`
 - GCC ≥ 4.9
 ##### Build and Install Detectron2

 After having the above dependencies, run:
 ```
 git clone https://github.com/facebookresearch/detectron2.git
 cd detectron2
 pip install -e .

 # or if you are on macOS
 # MACOSX_DEPLOYMENT_TARGET=10.9 CC=clang CXX=clang++ pip install -e .

 # or, as an alternative to `pip install`, use
 # python setup.py build develop
 ```
 Note: you often need to rebuild detectron2 after reinstalling PyTorch.
 ## Docker deployment
 #### For docker deployment for testing our model please follow the steps:

 1. Install Docker in local machine (Preferably with default Linux container.)

 2. Copy the final model file (model_final.pth) inside the /app/models/final folder.

 3. In the folder path of the Dockerfile, run docker build to create the docker image of the project with a desired image name. Find below an example to create a docker image of our application with the image name as 'my-mexpub-app' (all in small letters). The dot at the end of the command represents that the Dockerfile can be found in the current directory.

 docker build -t my-mexpub-app .

 4. Run the newly created (latest) image as a container with a suitable name. The below example uses container name as 'mexPubContainer' and used the latest application image. Also the Docker cotainer 5000 port is mapped to local machines 5000 port. Which means all the traffics coming to the local networks 5000 port will be redirected to container's 5000 port.

 docker run -it -p 5000:5000 --name mexPubContainer my-mexpub-app:latest
 
 Note: It takes time to return the predictions
 | <img src="assets/images/1.JPG" width=400> | <img src="assets/images/2.JPG" width=400> |
 |---------------------------------------------------------------------------|---------------------------------------------------------------------------|


 5. Hit http://localhost:5000 in the browser to access the appliction. 

## Sample outputs of PubMEX
| <img src="images/21375_1036.jpeg" width=400> | <img src="images/20011_1311.jpeg" width=400> |
|---------------------------------------------------------------------------|---------------------------------------------------------------------------|
| <img src="images/11703_510.jpeg" width=400> | <img src="images/11916_950.jpeg" width=400> |
| <img src="images/12455_890.jpeg" width=400> | <img src="/images/12715_540.jpeg" width=400> |

## License
[MIT](https://choosealicense.com/licenses/mit/)

