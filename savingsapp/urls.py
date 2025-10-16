from django.urls import path

from savingsapp import views

urlpatterns = [
    # 1. Dashboard / Home View (Always the main landing page)
    # Displays current month's contributions and total balance.
    path('', views.dashboard, name='dashboard'),

    # 2. Data Preparation View (The CRITICAL Upload Step)
    # Users upload the latest Excel backup file here to re-populate the temporary DB.
    path('prepare-db/', views.upload_and_prepare_db, name='prepare_db'),

    # 3. Record New Contribution View (Submission and Forced Download)
    # Handles form submission, saves the new record, and immediately triggers the full export.
    path('record-new/', views.record_new_contribution, name='record_new_contribution'),

    # 4. Optional: Manual Full Export (Good for admin to download anytime from dashboard)
    # This view queries ALL data in the temporary DB and sends the Excel file.
    path('export-all/', views.export_all_data, name='export_all_data'),
]

