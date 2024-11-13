# 使用说明

## 环境

pip install -r requirements.txt

## 部署

./run_mock_server.sh
> 如果需要后台部署，修改脚本，切换到nohup即可

## 请求链接

依据run_mock_server.sh中的端口确定，默认为18000
> gunicorn -c gunicorn.py run_mock_server:app -b 0.0.0.0:18000 -t 600000 --timeout 600000 -k gevent  

### 本地地址

<http://127.0.0.1:18000/mock>  

### 远程地址

http://{部署机器ip}:18000/mock  
