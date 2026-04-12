from django.urls import path
from . import views
from .views import ChatAnswerView, LoginView, UploadContextView

urlpatterns = [
    path('ask/', ChatAnswerView.as_view(), name='api.ask'),
    path('update-dataset/', views.update_dataset_view, name='update_dataset'),
    path('login/', LoginView.as_view(), name='api.login'), # Used for deciding dev user vs enduser
    path('upload-context/', UploadContextView.as_view(), name='api.upload_context'), # Used for uplod dataset
]
