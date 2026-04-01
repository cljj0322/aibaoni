import multiprocessing

# 绑定地址
bind = "127.0.0.1:5001"

# Worker 数量（CPU 核数 * 2 + 1）
workers = multiprocessing.cpu_count() * 2 + 1

# Worker 类型
worker_class = "sync"

# 超时时间
timeout = 120

# 日志
accesslog = "/var/log/aibaoni/access.log"
errorlog = "/var/log/aibaoni/error.log"
loglevel = "info"

# 进程名
proc_name = "aibaoni"

# 守护进程（由 systemd 管理时设为 False）
daemon = False
