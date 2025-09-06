from django.urls import path
from .views import StatsView, ReportCardView

urlpatterns = [
    path('dashboard/', StatsView.as_view(), name='dashboard-stats'),
    path('report-card/', ReportCardView.as_view(), name='report-card'),
]
