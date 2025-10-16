from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db import transaction, models
from .models import Contribution
from io import BytesIO
from datetime import date
import pandas as pd
import calendar # To get month name
from django import forms
from django.db.models import Sum


def dashboard(request):
    today = date.today()

    # 1. Calculate Total Balance (from all records in the temporary DB)
    total_balance_data = Contribution.objects.all().aggregate(
        total=models.Sum('amount')
    )
    total_balance = total_balance_data.get('total') or 0.00

    # 2. Filter data for the Current Month only
    current_month_data = Contribution.objects.filter(
        date__year=today.year,
        date__month=today.month
    ).order_by('-date', 'name')  # Order by most recent first

    # 3. Calculate Current Month Total
    monthly_total_data = current_month_data.aggregate(
        total=models.Sum('amount')
    )
    monthly_total = monthly_total_data.get('total') or 0.00

    context = {
        'total_balance': total_balance,
        'current_month_name': calendar.month_name[today.month],
        'contributions': current_month_data,
        'monthly_total': monthly_total,
        # Check if the DB has any data (it should be empty if not prepared)
        'db_is_prepared': Contribution.objects.exists()
    }

    return render(request, 'dashboard.html', context)

def upload_and_prepare_db(request):
    if request.method == 'POST':
        excel_file = request.FILES.get('excel_file')

        if not excel_file:
            # Simple message handling (you can improve this with Django messages)
            return render(request, 'upload_form.html', {'error': 'No file uploaded.'})

        # Check file type (optional but recommended)
        if not excel_file.name.endswith('.xlsx'):
            return render(request, 'upload_form.html', {'error': 'Invalid file type. Please upload an .xlsx file.'})

        try:
            # Read the Excel file into a Pandas DataFrame
            df = pd.read_excel(excel_file)

            # --- Enforce Data Consistency ---
            # Standardize column names (adjust these to match your Excel backup file)
            df = df.rename(columns={
                'name': 'name',
                'amount': 'amount',
                'date': 'date'
            })

            # Convert date column to datetime objects
            df['date'] = pd.to_datetime(df['date']).dt.date

            # --- Transaction ensures Atomicity (all or nothing) ---
            with transaction.atomic():
                # 1. CLEAR the temporary DB
                Contribution.objects.all().delete()

                # 2. Prepare records for bulk creation
                records_to_create = [
                    Contribution(
                        name=row['name'],
                        amount=row['amount'],
                        date=row['date']
                    ) for index, row in df.iterrows()
                ]

                # 3. BULK INSERT the historical data
                Contribution.objects.bulk_create(records_to_create)

            # Success: Redirect to the recording page
            return redirect('record_new_contribution')

        except Exception as e:
            # Catches errors like file corruption, missing columns, or bad data types
            error_message = f"Error processing file: Ensure columns are 'name', 'amount', 'date'. Details: {e}"
            return render(request, 'upload_form.html', {'error': error_message})

    # GET request: Display the upload form
    return render(request, 'upload_form.html')


def export_all_data(request):
    # Check if any data exists to export
    if not Contribution.objects.exists():
        # Handle case where the DB is empty
        return redirect('prepare_db')

    # 1. Query ALL data, ordered chronologically
    queryset = Contribution.objects.all().order_by('date', 'id')

    # Convert QuerySet to DataFrame
    df = pd.DataFrame(list(queryset.values('name', 'amount', 'date')))

    # 2. Add Running Balance Column (Professional Touch)
    df['Running_Balance'] = df['amount'].cumsum()

    # Rename columns for clarity in the final Excel output
    df = df.rename(columns={
        'name': 'Member Name',
        'amount': 'Contribution (UGX)',
        'date': 'Date of Entry',
        'Running_Balance': 'Total Savings (UGX)',
    })

    # 3. Create the in-memory Excel file
    output = BytesIO()
    # Use 'xlsxwriter' for professional styling
    writer = pd.ExcelWriter(output, engine='xlsxwriter')

    # Write DataFrame to the ExcelWriter
    df.to_excel(writer, index=False, sheet_name='All Contributions')

    # --- AUTO-WIDTH IMPLEMENTATION ---

    # Get the xlsxwriter workbook and worksheet objects
    workbook = writer.book
    # Access the sheet we just created
    worksheet = writer.sheets['All Contributions']

    # Define widths for each column based on content size
    column_widths = [
        # Col 1: Member Name (A:A) - Needs width for 150 unique names
        ('A:A', 30),
        # Col 2: Contribution Amount (B:B) - Sufficient for large UGX numbers
        ('B:B', 22),
        # Col 3: Date of Entry (C:C)
        ('C:C', 18),
        # Col 4: Total Savings Balance (D:D) - Needs widest space for cumulative total
        ('D:D', 25),
    ]

    # Set the column widths
    for col_range, width in column_widths:
        worksheet.set_column(col_range, width)

    # --- AUTO-WIDTH IMPLEMENTATION END ---

    # Finalize the Excel file generation
    writer.close()
    output.seek(0)

    # 4. Prepare and return the HTTP Response
    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    # Set the filename to include the current date for easy tracking
    filename = f"Family_Savings_Backup_{date.today().isoformat()}.xlsx"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    return response


# A simple Form for the contribution (best practice over using request.POST directly)
class ContributionForm(forms.ModelForm):
    class Meta:
        model = Contribution
        # Only expose the fields the user needs to enter
        fields = ['name', 'amount', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }


def record_new_contribution(request):
    # CRITICAL CHECK: Ensure the temporary DB is populated with historical data
    db_is_prepared = Contribution.objects.exists()

    if request.method == 'POST':
        if not db_is_prepared:
            # If they submit without preparation, redirect them back to fix it
            return redirect('prepare_db')

        form = ContributionForm(request.POST)
        if form.is_valid():
            # 1. Save the new record to the temporary SQLite DB
            form.save()

            return redirect('record_new_contribution')


        # If form is invalid, fall through to display form with errors
    else:
        # GET request
        form = ContributionForm(initial={'date': date.today()})

    context = {
        'form': form,
        'today': date.today().isoformat(),
        'db_is_prepared': db_is_prepared,
    }

    return render(request, 'new_contribution_form.html', context)