# 基础镜像，使用官方的 Python 3.8 镜像
FROM python:3.8-slim-buster

# 设置工作目录
WORKDIR /app

# 复制项目的 `requirements.txt` 文件到工作目录
COPY requirements.txt /app/

# 安装依赖项
RUN pip install --no-cache-dir -r requirements.txt

# 复制当前目录下的所有文件到工作目录
COPY . /app/

# 复制 .env 文件到工作目录
COPY .env /app/.env

# 暴露应用运行的端口（默认 8000）
EXPOSE 8000

# 设置环境变量
ENV PYTHONUNBUFFERED=1

# 运行数据库迁移和收集静态文件的命令
RUN python manage.py collectstatic --noinput
RUN python manage.py migrate

# 启动命令，使用 Gunicorn 作为应用服务器
CMD ["gunicorn", "gamescoretracker.wsgi:application", "--bind", "0.0.0.0:8000", "--timeout", "120", "--log-level", "debug"]

