# Billing system analyser

# imports
import os
import sys
import yaml

# cd to work directory
curDir=os.path.dirname(__file__)
os.chdir(curDir)



with open('res/settings.yml') as f:
    settings=yaml.safe_load(f)

def create_resources():
    global transactions_general
    # Loading transactions data and settings
    with open('data/transactions_general.yml') as f:
        transactions_general=yaml.safe_load(f)

    if not os.path.isdir('data/analysis'):
        os.mkdir('data/analysis')

# Define variables
modes=settings['modes']
external_parties=[]
parties_transaction_history={}
dues={}

# if os.path.isfile('data/analysis/people.log'):
#     with open('data/analysis/people.log') as g:
#         preregistered_external_parties=g.read().splitlines()
# else:
#     preregistered_external_parties = []


# Writing logs and analysis data
def generate_statements_log():
    global external_parties
    with open('data/analysis/statements.log', 'w') as g:
        for transaction in transactions_general['Transactions']:
            bound=transaction['bound']
            amount=transaction['amount']
            if bound:
                amount = f'Cr {amount}'
            else:
                amount = f'Dr {amount}'

            g.write(amount+'\n')

    for transaction in transactions_general['Transactions']:
        parties=list(transaction['parties'].values())
        external_party=[
            party for party in parties
            if party != 'You' and
            party.strip() != ''
        ][0]

        external_parties.append(external_party)

    # Remove preregistered external parties, i.e. register only new external parties
    # external_parties=[i for i in external_parties if not i in preregistered_external_parties]

    # Add only unique members
    external_parties=list(set(external_parties))
    external_parties.sort()

def generate_peoples_log():
    global external_parties
    with open('data/analysis/people.log', 'w') as f:
        for external_party in list(sorted(external_parties, key=lambda x: x.upper())):
            f.write(str(external_party)+'\n')

def generate_summary_log():
    with open('data/analysis/statement_summaries.log', 'w') as f:
        for transaction in transactions_general['Transactions']:
            # bound, amount, datetime, location, mode, parties = list(transaction.keys())
            bound=transaction['bound']
            amount=transaction['amount']
            datetime=transaction['datetime']
            location=transaction['location']
            mode=transaction['mode']
            parties=transaction['parties']

            receiver, sender=parties

            # if type(mode)==str:
            #     try:
            #         mode=modes[int(mode)]
            #     except Exception:
            #         print('Internal error: Could not detect payment method type from its ID')

            if bound == True: # Inbound money -> You credited
                one_liner_statement=''\
                f'You received {int(amount):,.2f} from {sender} '\
                f'on {datetime} '
                if location:
                    one_liner_statement+=(f'from {location} ' if location else '')

                if type(mode)==int:
                    one_liner_statement+=f'via {modes[mode]}'
                else:
                    one_liner_statement+=f'via {mode}'

            elif bound == False: # Outbound money -> You debited
                one_liner_statement=''\
                f'You sent {int(amount):,.2f} to {receiver} '\
                f'on {datetime}" '
                if location:
                    one_liner_statement+=(f'from {location} ' if location else '')

                if type(mode)==int:
                    one_liner_statement+=f'via {modes[mode]}'
                else:
                    one_liner_statement+=f'via {mode}'


            f.write(one_liner_statement+'\n')

def transaction_history_with_person(ext_party):
    transactions_by_party = []
    # for ext_party in external_parties:
    # transactions_by_party
    for transaction in transactions_general['Transactions']:
        if transaction['parties']['sender'] == ext_party: # If ext_party is the sender
            transactions_by_party.append(transaction['amount']) # Add party's transaction as a credit
        elif transaction['parties']['receiver'] == ext_party: # If ext_party is the receiver
            transactions_by_party.append(-transaction['amount']) # Add party's transaction as a debit

    return transactions_by_party

def gen_transactions_by_party_yml():
    global parties_transaction_history
    for ext_party in external_parties:
        parties_transaction_history[ext_party]=transaction_history_with_person(ext_party)

    parties_transaction_history={
        key: {
            'exchanges': valuelist,
            'net_exchange': sum(valuelist)
            }
        for key,valuelist in parties_transaction_history.items()
    }

    parties_transaction_history={'user_specific_exchange_history': parties_transaction_history for key,value in parties_transaction_history.items()}
    with open('data/analysis/transactions_by_party.yml', 'w') as f:
        yaml.safe_dump(parties_transaction_history, f)


if __name__ == '__main__':
    create_resources()

    generate_statements_log()
    generate_peoples_log()
    generate_summary_log()
    gen_transactions_by_party_yml()

