import os
REDIS_URL = os.environ.get("REDIS_URL")
ROUNDTRIP_CHANNEL = 'workers-responded'
WORKER_TOPIC = ['worker-input', 'worker-input-1']
HENDRIX_CHANNEL = 'hendrix'
NYMS_KEY = 'nyms'
