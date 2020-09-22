# MexPub Demo
# Demo Web Application Metadata extraction from German scientific papers

# Please follow the steps for Docker container creation.

1. Install Docker in local machine (Preferably with default Linux container.)

2. Copy the final model file (model_final.pth) inside the /app/models/final folder.

3. In the folder path of the Dockerfile, run docker build to create the docker image of the project with a desired image name. Find below an example to create a docker image of our application with the image name as 'my-mexpub-app' (all in small letters). The dot at the end of the command represents that the Dockerfile can be found in the current directory.

docker build -t my-mexpub-app .

4. Run the newly creted (latest) image as a container with a suitable name. The below example uses container name as 'mexPubContainer' and used the latest application image. Also the Docker cotainer 5000 port is mapped to local machines 5000 port. Which means all the traffics coming to the local networks 5000 port will be redirected to container's 5000 port.

docker run -it -p 5000:5000 --name mexPubContainer my-mexpub-app:latest


5. Hit http://localhost:5000 in the browser to access the appliction. 
