from django.urls import path
from .views import UserActivityListView,UserActionView,DashboardView

urlpatterns = [
    #path('user-activity/', UserActivityView.as_view(), name='user_activity'),
    path('user-activity/list/', UserActivityListView.as_view(), name='user_activity_list'),
    path('user-action/', UserActionView.as_view(), name='user_action'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),

]
