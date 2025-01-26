bind = "0.0.0.0:8000"
workers = 12 # gnprocの結果12だったので12*2+1=25
threads = 2
timeout = 120
loglevel = "debug" # 本番環境ではinfoにする
accesslog = "/app/log/gunicorn/access.log"
errorlog = "/app/log/gunicorn/error.log"
preload_app = True # アプリケーションをworkerにpreload
