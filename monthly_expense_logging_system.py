import os
import sys
import yaml

from datetime import datetime as dt

# curDir=os.path.dirname(sys.argv[0])
curDir=os.path.dirname(__file__)
os.chdir(curDir)

log_file='data/analysis/monthly_expenses.yml'
transactions_file='data/transactions_general.yml'

monthly_expense_info={}
a=[]

def draft_log():
    global final_data, monthly_expense_info
    if os.path.isfile(log_file):
        with open(log_file) as f:
            prestored_data=yaml.safe_load(f)
    else:
        prestored_data={} # Nothing stored

    with open(transactions_file) as f:
        transactions=yaml.safe_load(f)

    for transaction in transactions['Transactions']:
        amount=transaction['amount']
        bound=transaction['bound']
        if not bound:
            amount*=-1
        TIME=transaction['datetime']
        TIME=dt.strptime(TIME, '%A, %d-%b-%Y @%I:%M:%S %p')

        a.append((TIME.strftime('%b-%Y'), amount))

    for month, amt in a:
        if (month in monthly_expense_info.keys()):
            monthly_expense_info[month]+=[amt]
        else:
            monthly_expense_info[month]=[amt]

    monthly_expense_info={
        month:
        {
            'exhanges':exchanges,
            'net':sum(exchanges)
        } for month, exchanges in monthly_expense_info.items()
    }

    if prestored_data:
        final_data={**prestored_data, **monthly_expense_info}
    else:
        final_data=monthly_expense_info

def update_log():
    global final_data
    with open(log_file, 'w') as f:
        prestored_data=yaml.safe_dump(final_data, f)

if __name__ == '__main__':
    draft_log()
    update_log()


