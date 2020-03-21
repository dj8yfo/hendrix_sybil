import os
if os.environ.get("IS_TEST") is None:
    REDIS_HOST = 'redis'
else:
    REDIS_HOST = 'localhost'
REDIS_PORT = 6379
ROUNDTRIP_CHANNEL = 'workers-responded'
WORKER_TOPIC = ['worker-input', 'worker-input-1', 'worker-input-2', 'worker-input-3']
HENDRIX_CHANNEL = 'hendrix'
NYMS_KEY = 'nyms'
