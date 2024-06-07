from django.views import View
from django.shortcuts import render
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
import json
import boto3
import os
import redis
from datetime import datetime
from collections import Counter


AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_DEFAULT_REGION = os.environ.get('AWS_DEFAULT_REGION')

dynamodb = boto3.resource(
    'dynamodb',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_DEFAULT_REGION
)

# Redis client
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

@method_decorator(ensure_csrf_cookie, name='dispatch')
class UserActionView(View):
    template_name = 'analytics/index.html'
    table_name = 'new-user-activity'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)  # Parse JSON data from request
        user_ip = self.get_client_ip(request)  # Get user IP address
        user_agent = request.META.get('HTTP_USER_AGENT', '')  # Get user agent

        # Store the user action in DynamoDB
        self.store_user_action(user_ip, user_agent, data)

        return JsonResponse({'message': 'JSON data received'}, status=200)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def store_user_action(self, user_ip, user_agent, data):
        table = dynamodb.Table('new-user-activity')
        item = {
            'user_id': user_ip,
            'user_agent': user_agent,
            'action': data.get('action'),
            'timestamp': str(datetime.utcnow()),
        }
        table.put_item(Item=item)

class UserActivityListView(View):
    table_name = 'new-user-activity'

    def get(self, request, *args, **kwargs):
        cache_key = 'new-user-activity'
        cached_data = redis_client.get(cache_key)

        if cached_data:
            items = json.loads(cached_data)
        else:
            table = dynamodb.Table(self.table_name)
            response = table.scan()
            items = response.get('Items', [])

            # Cache the data for 15 minutes
            redis_client.setex(cache_key, 60*15, json.dumps(items))

        return JsonResponse(items, safe=False, status=200)

class DashboardView(View):
    def get(self, request, *args, **kwargs):
        # Check if the data is in Redis cache
        cached_data = redis_client.get('dashboard_data')
        if cached_data:
            # If data is found in cache, use it
            items = json.loads(cached_data)
        else:
            # If not found, fetch from DynamoDB
            table = dynamodb.Table('new-user-activity')
            response = table.scan()
            items = response.get('Items', [])

            # Store the fetched data in Redis cache for 15 minutes (900 seconds)
            redis_client.set('dashboard_data', json.dumps(items), ex=900)

        # Extract data for charts
        timestamps = [item['timestamp'] for item in items]
        activity_types = [item['action'] for item in items]

        # Convert timestamps to hours for traffic analysis
        hours = [datetime.fromisoformat(ts).hour for ts in timestamps]

        # Count occurrences
        hour_counts = dict(Counter(hours))
        activity_counts = dict(Counter(activity_types))

        context = {
            'items': items,
            'hour_counts': hour_counts,
            'activity_counts': activity_counts
        }
        return render(request, 'analytics/dashboard.html', context)