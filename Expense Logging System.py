# Basic Billing Registration System

# Help documentation and basic information not yet created

import os
import sys

# cd to work directory
# curDir=os.path.dirname(sys.argv[0])
curDir=os.path.dirname(__file__)
os.chdir(curDir)

# Imports
import yaml
import analysis
import monthly_expense_logging_system as mels

from tabulate import tabulate as tbl
from datetime import datetime as dt

today=dt.now().date()
logged_out=False
transaction_log_count=0
essential_files={
    'settingsFile': 'res/settings.yml',
    'transactionsGenFile': 'data/transactions_general.yml'
}

def create_resources():
    for file in essential_files.values():
        if not os.path.isfile(file):
            print(f'File {file} not found, creating new...')
            with open(file, 'w') as f:
                f.write('')

# Loading transactions data and settings
if not os.path.isfile(essential_files['transactionsGenFile']):
    with open(essential_files['transactionsGenFile'], 'w') as f:
        pass

with open(essential_files['transactionsGenFile']) as f:
    transactions_general=yaml.safe_load(f)

with open(essential_files['settingsFile']) as f:
    settings=yaml.safe_load(f)

modes=settings['modes']

# with open('data/transactions_people.yml') as f:
#     transactions_people=yaml.safe_load(f)

def save_transaction_count_log():
    '''Save number of transactions logged today (Do this everyday the program is run)'''

    global transaction_log_count

    try:
        with open("data/analysis/transaction_count_per_day.yml") as f:
            transactions_per_day=yaml.safe_load(f)['transactions_per_day']
    except Exception:
        transactions_per_day={} # Set as empty if no data for "transaction count per day" exists

    try:
        # Increment today's transaction log count by that of current session
        transactions_today=transactions_per_day[today]+transaction_log_count
    except KeyError:
        # No transactions today except that of current session
        transactions_today=transaction_log_count

    with open("data/analysis/transaction_count_per_day.yml", 'w') as f:
        transactions_per_day={'transactions_per_day': transactions_per_day}
        transactions_per_day['transactions_per_day'][today]=transactions_today

        yaml.safe_dump(transactions_per_day, f)




def save_data():
    print("Saving data")
    # Loading transactions data and settings
    with open('data/transactions_general.yml', 'w') as f:
        yaml.dump(transactions_general, f)

    print('Preparing analysis')
    analysis.create_resources()

    save_transaction_count_log()

    analysis.generate_statements_log()
    analysis.generate_peoples_log()
    analysis.generate_summary_log()
    analysis.gen_transactions_by_party_yml()
    print('Analysis prepared')

    print('Updating Logs')
    mels.draft_log()
    mels.update_log()
    print('Logs updated')


def logout():
    global logged_out
    confirm_logout = input('Press "y" to save and logout or any other key to abort session and logout: ')
    if confirm_logout.lower().strip() == 'y':
        save_data()
        print('\nThank you for using this application\nYou have been safely logged out.')
        _ = input('Hit enter to close this window now. . .')

        logged_out=True

    else:
        print('\nThank you for using this application\nNo data was saved and you have been successfully logged out.')
        _ = input('Hit enter to close this window now. . .')

        # os._exit(0)

def aborted_logout():
    '''May be changed later for some kind of use...'''
    print('Logout aborted')

def _input(_prompt, _type=float): # Prolly finished?
    user_input=''

    if _type in [float, 'mode'] or type(_type) in [list, tuple]:
        if _type == float:
            while not user_input.isdigit():
                user_input=input(_prompt)
                if user_input.lower().strip() == 'logout':
                    logout()
                    if logged_out:
                        break
                    else:
                        aborted_logout()
                if not user_input.isdigit():
                    print('Invalid, please retry...')

        elif _type == 'mode':
            asking_first_time = True
            while True:
                user_input=input(_prompt*asking_first_time)
                if user_input.lower().strip() == 'logout':
                    logout()
                    if logged_out:
                        break
                    else:
                        aborted_logout()
                if user_input.lower().strip() != 'a' and user_input.lower().strip() != '':
                    break
                if user_input.lower().strip() != '':
                    print('    Choose index corresponding to your mode of payment:')
                    print(
                        tbl(
                            [[i] for i in modes],
                            tablefmt='pretty',
                            headers=('Index', 'Payment mode'),
                            colalign=('right', 'left'),
                            showindex=True,
                        )
                    )
                    print('    or type a custom mode\n  or\n"a" again for options: ', end='')
                asking_first_time = False

                if user_input == '':
                    print('    Custom mode can\'t be empty, please retry... ', end='')
                elif user_input.isspace():
                    print('    Custom mode can\'t be only spaces or tabs, some characters are needed\nplease retry... ', end='')

            if not user_input.isdigit():
                if user_input.lower().strip() != 'a':
                    if len(user_input) >= 28:
                        print(f'      #Custom mode: {user_input[:14].strip()}...{user_input[-14:].strip()}')
                    else:
                        print(f'      #Custom mode: {user_input}')
                else: # here mode == a
                    pass
            else:
                if int(user_input) >= 0:
                    print(f'      #Mode: {modes[int(user_input)]}')
                else:
                    print('      Mode can\'t be a negative number')

        else:
            if type(_type) in [list, tuple]:
                while not user_input in _type:
                    user_input=input(_prompt)
                    if user_input.lower().strip() == 'logout':
                        logout()
                        if logged_out:
                            break
                        else:
                            aborted_logout()
                    if not user_input in _type:
                        print('@Invalid, please retry...')
            else:
                print('Invalid constraint_')
                return None
    else:
        print('Invalid constraint')
        return None

    return user_input

def process(x): # ~TBD!!
    global transactions_general, transaction_log_count
    '''
    Processes a user commands related to billing,
    transactions and the analysis thereof
    '''

    # New transaction
    if x.lower().strip() == '':
        transaction_log_count+=1 # New transaction recording started
        print('='*80)
        print('::New transaction commenced')

        amount = _input('  Amount: ', _type=float)
        print(f'      #Amount: {float(amount):,.2f}\n')

        bound = _input('  [c]redit or [d]ebit?: ', _type=['c', 'd'])
        if bound == 'd':
            sender='You'
            receiver=input('      @Receiver: ')
            print(f'    #Debited amount: {float(amount):,.2f}\n')
        else:
            sender=input('      @Sender: ')
            receiver='You'
            print(f'      #Credited amount: {float(amount):,.2f}\n')

        mode = _input('  Mode of payment ["a" to list all, or type custom]: ', _type='mode')
        try:
            if mode.isdigit():
                mode = int(mode)
        except Exception:
            pass

        print()

        location = input('  *Location [optional]: ')
        if location.lower().strip() == '':
            location = ''
        print()

        # Final transaction summary
        print('::Transaction Summary')


        NOW=dt.now().strftime('%A, %d-%b-%Y @%I:%M:%S %p')
        if bound.lower().strip() == 'c': # Inbound money -> You credited
            print(f'  You received {float(amount):,.2f} from {sender}\n')
            print(f'  Time: {NOW}')
            if type(mode)==int:
                print(f'  {location} via {modes[mode]}')
            else:
                print(f'  {location} via {mode}')

        elif bound.lower().strip() == 'd': # Outbound money -> You debited
            print(f'  You sent {float(amount):,.2f} to {receiver}\n')
            print(f'  Time: {NOW}')
            if type(mode)==int:
                print(f'  {location} via {modes[mode]}')
            else:
                print(f'  {location} via {mode}')
        else:
            print('  Error: Could not create summary')

        if transactions_general is None:
            transactions_general={'Transactions': []}

        # print(transactions_general)

        transactions_general['Transactions'].append(
            {
                "amount": float(amount),
                "bound": bound.lower().strip()=='c',
                "mode": mode,
                "parties": {
                    "sender": sender,
                    "receiver": receiver
                },
                "location": (location if location else None),
                "datetime": NOW
            }
        )


        print('::Transaction Ended')
        print('='*80)

def main():
    new = '' # Initializing `new`
    create_resources()
    while not new.lower().strip().replace(' ', '') == 'logout':
        new = input(f'(log count: {transaction_log_count})~ ')
        process(new)
    else:
        logout()
        # break

if __name__ == '__main__':
    p=input('$ Password: ')
    if p.lower().strip() == '123':
        main()
    else:
        print('Invalid password')
    # pass
