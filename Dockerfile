FROM jupyter/scipy-notebook

USER root

RUN wget -O /usr/local/share/fonts/SourceHanSans-Normal.ttc https://raw.githubusercontent.com/adobe-fonts/source-han-sans/release/OTC/SourceHanSans-Normal.ttc

RUN pip install grpcio grpcio-tools plotly ipywidgets
