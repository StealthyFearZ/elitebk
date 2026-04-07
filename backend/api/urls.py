from django.urls import path, include
from . import views
from .views import ChatAnswerView

urlpatterns = [
    path('ask/', ChatAnswerView.as_view(), name='api.ask'),
    path('update-dataset/', views.update_dataset_view, name='update_dataset'),
]
