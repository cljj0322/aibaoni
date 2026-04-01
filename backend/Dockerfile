FROM python:3.12-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# 复制应用代码
COPY . .

# 创建必要的目录
RUN mkdir -p instance /var/log/aibaoni

EXPOSE 5001

# 使用 gunicorn 启动，覆盖 bind 地址为 0.0.0.0 以便容器内通信
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "-c", "gunicorn.conf.py", "run:app"]
