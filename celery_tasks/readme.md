# 安装
pip install celery, eventlet

# 启动
celery -A celery_tasks.tasks worker -l info -P eventlet
