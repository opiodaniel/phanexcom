from django.http import HttpResponse, JsonResponse
from django.shortcuts import render


contributors_list = [
        {
            'name': 'Opio Daniel',
            'amount': '10,000',
            'time': '2025-07-05',
            'color': 'rank-gold',
        },
        {
            'name': 'Aryono innocent',
            'amount': '10,000',
            'time': '2025-07-07',
            'color': 'rank-silver',
        },
        {
            'name': 'Ekwang Oscar',
            'amount': '10,000',
            'time': '2025-08-05',
            'color': 'rank-bronze',
        },
        {
            'name': 'Ogwal Walter',
            'amount': '10,000',
            'time': '2025-08-09',
            'color': 'rank-gold',
        },
        {
            'name': 'Aryono Jimmy',
            'amount': '10,000',
            'time': '2025-09-05',
            'color': 'rank-silver',
        },
]

month = {
          '01': 'January',
          '02': 'February',
          '03': 'March',
          '04': 'April',
          '05': 'May',
          '06': 'June',
          '07': 'July',
          '08': 'August',
          '09': 'September',
          '10': 'October',
          '11': 'November',
          '12': 'December' }

def get_month(month_num):
    month_ = ''
    for m in month:
        if m == month_num:
            month_ = month[m]
    return month_


def home(request):
    return render(request, 'index.html')

def sort_by_month(request):
    if request.method == 'POST':
        month_num = request.POST.get('selected_date')
        c_list = []
        for contributor in contributors_list:
            print(contributor['time'].split('-')[1])
            if month_num == contributor['time'].split('-')[1]:
                c_list.append({"name":contributor['name'], 'amount':contributor['amount'], 'time':contributor['time'], 'color':contributor['color']})
            elif month_num == 'all':
                c_list.append({"name":contributor['name'], 'amount':contributor['amount'], 'time':contributor['time'], 'color':contributor['color']})

    return JsonResponse({"contributors": c_list})

def record_amount(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        amount = request.POST.get('amount')
        date = request.POST.get('date')
    return JsonResponse({"name": name, "amount": amount, "date": date})
