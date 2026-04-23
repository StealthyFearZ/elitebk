from django.urls import path
from . import views
from .views import (
    ChatAnswerView,
    GenerateReportView,
    LoginView,
    PredictLineupView,
    RegisterView,
    UploadContextView,
)


urlpatterns = [
    path('ask/', ChatAnswerView.as_view(), name='api.ask'),
    path('generate-report/', GenerateReportView.as_view(), name='api.generate_report'), # Generates the pdf report
    path('predict-lineup/', PredictLineupView.as_view(), name='api.predict_lineup'), # Generates predicted stat line excel
    path('update-dataset/', views.update_dataset_view, name='update_dataset'),
    path('login/', LoginView.as_view(), name='api.login'), # Used for deciding dev user vs enduser
    path('upload-context/', UploadContextView.as_view(), name='api.upload_context'), # Used for uplod dataset
    path('register/', RegisterView.as_view(), name='api.register'), # used for signup / registere
]
