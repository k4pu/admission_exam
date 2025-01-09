bind = "0.0.0.0:8000"
workers = 12 # gnprocの結果12だったので12*2+1=25
threads = 2
timeout = 120
loglevel = "debug" # 本番環境ではinfoにする
# accesslog = "/var/log/gunicorn/access.log"
# errorlog = "/var/log/gunicorn/error.log"
preload_app = True # アプリケーションをworkerにpreload
