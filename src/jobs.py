# jobs.py
import uuid
from hotqueue import HotQueue
from redis import StrictRedis
import os
import sys

redis_ip = os.environ.get('REDIS_IP')
# if not redis_ip:
#     raise Exception()

rd = StrictRedis(host=redis_ip, port=6379, db=0, decode_responses=True)
jrd = StrictRedis(host=redis_ip, port=6379, db=1, decode_responses=True)
q = HotQueue("queue", host=redis_ip, port=6379, db=2)
image_rd = StrictRedis(host=redis_ip, port=6379, db=3)

# Allows print statements to be viewed in logs:
original_stdout = sys.stdout
sys.stdout = sys.stderr

def _generate_jid():
    return str(uuid.uuid4())

def _generate_job_key(jid):
    return 'job.{}'.format(jid)

def _instantiate_job(jid, status, countries, date_range):
    if type(jid) == str:
        return {'jid': jid,
                'status': status,
                'countries': countries,
                'date_range': date_range
        }
    return {'jid': jid.decode('utf-8'),
            'status': status.decode('utf-8'),
            'countries': countries.decode('utf-8'),
            'date_range': date_range.decode('utf-8')
    }

def _save_job(job_key, job_dict):
    """Save a job object in the Redis jobs database."""
    jrd.hmset(job_key, job_dict)

def _queue_job(jid):
    """Add a job to the redis queue."""
    q.put(jid)

def add_job(countries, date_range, status="submitted"):
    """Add a job to the redis queue."""
    jid = _generate_jid()
    job_dict = _instantiate_job(jid, status, countries, date_range)
    _save_job(_generate_job_key(jid), job_dict)
    _queue_job(jid)
    return job_dict

def update_job_status(jid, new_status):
    """Update the status of job with job id `jid` to status `new_status`."""
    jrd.hset(_generate_job_key(jid), 'status', new_status)

def get_job_data(jid):
    """Returns dictionary containing job data"""
    return jrd.hgetall(_generate_job_key(jid))

def add_image(jid, img):
    jrd.hset(_generate_job_key(jid), 'image_status', 'created')
    image_rd.hset(jid, 'image', img)