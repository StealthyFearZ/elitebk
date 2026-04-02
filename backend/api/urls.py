from django.urls import path, include
from .views import ChatAnswerView

urlpatterns = [
    path('ask/', ChatAnswerView.as_view(), name='api.ask')
]
