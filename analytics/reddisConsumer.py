import redis
import json

def process_message(message):
    data = json.loads(message[b'data'].decode('utf-8'))
    print(f"Received message: {data}")

r = redis.Redis(host='localhost', port=6379, db=0)
last_id = '0-0'  # Start from the beginning

while True:
    messages = r.xread({'user_activity_stream': last_id}, block=0, count=10)
    if messages:
        for stream, message in messages:
            last_id, message_data = message[0]
            process_message(message_data)
            last_id = last_id.decode('utf-8')
