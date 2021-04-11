docker stop jupyternotebook
docker rm jupyternotebook
docker run -d \
    -e CHOWN_HOME=yes -e CHOWN_HOME_OPTS='-R' \
    -v $PWD/home:/home/jovyan \
    --name jupyternotebook \
    -p 8888:8888 \
    jupyternotebook