# ベースイメージとして Python を使用
FROM python:3.11-slim

# 作業ディレクトリを設定
WORKDIR /app

# 必要なパッケージをインストール
COPY requirements.txt /app/
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt \
 && apt-get update \
 && apt-get install -y --no-install-recommends \
    nginx \
 && apt-get -y clean \
 && rm -rf /var/lib/apt/lists/*

# プロジェクトのコードをコンテナにコピー
COPY . /app/

# 静的ファイルを収集
RUN python manage.py collectstatic --noinput
