FROM fedora:40

WORKDIR /platform-a

RUN dnf -y install texstudio texlive texlive-fontawesome texlive-scheme-full google-noto-sans-cjk-fonts

RUN dnf -y install python3-pip
RUN pip3 install qrcode
RUN pip3 install bs4
RUN pip3 install requests

COPY make-sticker.py /platform-a
COPY NotoSansCJK-Regular.ttc /platform-a

CMD ["python3", "make-sticker.py"]
