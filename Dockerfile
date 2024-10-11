FROM pytorch/pytorch:2.2.2-cuda12.1-cudnn8-runtime

# 必须指定 pip 版本为 24.0, 解决 https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI/issues/2244
RUN sed -i 's/archive.ubuntu.com/repo.huaweicloud.com/g' /etc/apt/sources.list && \
    apt-get update && \
    pip config set global.index-url https://mirrors.huaweicloud.com/repository/pypi/simple && \
    pip config set global.trusted-host repo.huaweicloud.com && \
    pip config set global.timeout 120 && \
    pip install pip==24.0

# pkg-config/libmysqlclient-dev/build-essential for mysqlclient,
RUN apt-get install -y ffmpeg build-essential pkg-config libmysqlclient-dev

WORKDIR /app/rvc
COPY requirements.txt /app/rvc/requirements.txt
RUN pip install -r requirements.txt
# 使用原始源安装 mcelery, 镜像不够新
RUN pip install -i https://pypi.org/simple mcelery==0.0.3

COPY . /app/rvc/
CMD celery -A rvc_celery worker -l INFO -E -P solo -Q rvc_infer -n rvc_worker