from django.urls import path
from .views import StatsView, ReportCardView, DashboardStatsView

urlpatterns = [
    path('dashboard/', StatsView.as_view(), name='dashboard-stats'),
    path('report-card/', ReportCardView.as_view(), name='report-card'),
    path('dashboard-stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
]
