docker stop jupyternotebook
docker rm jupyternotebook
docker run -d \
    -v $PWD/home:/home/jovyan \
    --name jupyternotebook \
    -p 8888:8888 \
    jupyter/scipy-notebook