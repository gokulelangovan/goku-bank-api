from repositories.customer_repository import CustomerRepository
from repositories.account_repository import AccountRepository
from repositories.transaction_repository import TransactionRepository
from services.banking_service import BankingService


def get_banking_service():

    customer_repo = CustomerRepository()
    account_repo = AccountRepository()
    transaction_repo = TransactionRepository()

    return BankingService(customer_repo, account_repo, transaction_repo)