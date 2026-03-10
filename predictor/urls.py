from django.urls import path
from predictor.views import upload_report,predict

urlpatterns = [
    path('', predict, name='predict'),            # default page
    path('upload/', upload_report, name='upload_report'),  # OCR + report upload
]
