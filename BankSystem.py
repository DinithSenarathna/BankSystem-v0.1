import json  # Importing JSON module to handle JSON file operations
import os  # Importing OS module to interact with the operating system, like checking file existence
import random  # Importing Random module to generate random numbers
import base64  # Importing Base64 module to encode and decode data
from datetime import datetime  # Importing Datetime to handle date and time
from cryptography.fernet import Fernet, InvalidToken  # Importing Fernet for encryption and InvalidToken for handling decryption errors

# Class to manage encryption and decryption processes
class EncryptionManager:
    def __init__(self, key_file='secret.key'):
        self.key_file = key_file  # Setting the file where the encryption key will be stored
        self.key = self.load_or_generate_key()  # Load an existing key or generate a new one

    # Load the key from file if it exists, otherwise generate a new key
    def load_or_generate_key(self):
        if os.path.exists(self.key_file):  # Check if the key file exists
            with open(self.key_file, 'rb') as file:  # Open the key file in binary read mode
                return file.read()  # Return the key
        else:
            key = Fernet.generate_key()  # Generate a new encryption key
            with open(self.key_file, 'wb') as file:  # Open the key file in binary write mode
                file.write(key)  # Write the key to the file
            return key  # Return the newly generated key

    # Encrypt the provided data using the encryption key
    def encrypt(self, data):
        f = Fernet(self.key)  # Initialize Fernet with the encryption key
        encrypted_data = f.encrypt(data.encode())  # Encrypt the data (converted to bytes)
        return base64.urlsafe_b64encode(encrypted_data).decode('utf-8')  # Encode the encrypted bytes to a URL-safe string for JSON storage

    # Decrypt the provided encrypted data
    def decrypt(self, data):
        f = Fernet(self.key)  # Initialize Fernet with the encryption key
        try:
            encrypted_data = base64.urlsafe_b64decode(data)  # Decode the URL-safe string back to bytes
            return f.decrypt(encrypted_data).decode()  # Decrypt the data and convert it back to a string
        except InvalidToken:
            print("Warning: Could not decrypt data. Skipping.")  # Handle cases where decryption fails
            return None

# Class representing a bank account
class BankAccount:
    def __init__(self, account_number, account_holder, balance=0.0, transactions=None, encryption_manager=None):
        self.account_number = account_number  # Store the account number
        self.encryption_manager = encryption_manager  # Store the encryption manager

        # Encrypt account holder's name and balance
        self.encrypted_account_holder = self.encryption_manager.encrypt(account_holder)
        self.encrypted_balance = self.encryption_manager.encrypt(str(balance))

        self.transactions = transactions if transactions is not None else []  # Initialize transactions list

    # Decrypt and return the account holder's name
    @property
    def account_holder(self):
        return self.encryption_manager.decrypt(self.encrypted_account_holder)

    # Decrypt and return the balance as a float
    @property
    def balance(self):
        return float(self.encryption_manager.decrypt(self.encrypted_balance))

    # Update the balance by encrypting the new balance value
    def update_balance(self, new_balance):
        self.encrypted_balance = self.encryption_manager.encrypt(str(new_balance))

    # Add a transaction record after encrypting it
    def add_transaction(self, action, amount):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Record the current date and time
        transaction_record = {
            "action": action,
            "amount": amount,
            "date_time": timestamp
        }
        encrypted_record = self.encryption_manager.encrypt(json.dumps(transaction_record))  # Encrypt the transaction record
        self.transactions.append(encrypted_record)  # Add the encrypted record to the transactions list

    # Method to deposit money into the account
    def deposit(self, amount):
        new_balance = self.balance + amount  # Calculate the new balance
        self.update_balance(new_balance)  # Update the balance
        self.add_transaction("Deposit", amount)  # Add the deposit transaction
        print(f"{amount} has been deposited. New balance: {new_balance}")

    # Method to withdraw money from the account
    def withdraw(self, amount):
        if amount > self.balance:  # Check if the account has enough funds
            print("Insufficient funds.")
        else:
            new_balance = self.balance - amount  # Calculate the new balance
            self.update_balance(new_balance)  # Update the balance
            self.add_transaction("Withdraw", amount)  # Add the withdrawal transaction
            print(f"{amount} has been withdrawn. New balance: {new_balance}")

    # Method to transfer money from this account to another
    def transfer(self, target_account, amount):
        if amount > self.balance:  # Check if the account has enough funds
            print("Insufficient funds.")
        else:
            new_balance = self.balance - amount  # Calculate the new balance of this account
            target_new_balance = target_account.balance + amount  # Calculate the new balance of the target account
            self.update_balance(new_balance)  # Update this account's balance
            target_account.update_balance(target_new_balance)  # Update the target account's balance
            self.add_transaction(f"Transfer to {target_account.account_number}", amount)  # Add the transfer transaction to this account
            target_account.add_transaction(f"Transfer from {self.account_number}", amount)  # Add the transfer transaction to the target account
            print(f"Transferred {amount} to account {target_account.account_number}. New balance: {new_balance}")

    # Method to print the transaction receipt
    def print_receipt(self):
        print("\nTransaction Receipt")
        print("-------------------")
        print(f"Account Holder: {self.account_holder}")
        print(f"Account Number: {self.account_number}")
        print(f"Balance: {self.balance}")
        print("Recent Transactions:")
        for encrypted_transaction in self.transactions[-5:]:  # Only show the last 5 transactions
            transaction_json = self.encryption_manager.decrypt(encrypted_transaction)  # Decrypt the transaction record
            if transaction_json:
                transaction = json.loads(transaction_json)  # Convert the decrypted JSON string back to a dictionary
                print(f"- {transaction['date_time']}: {transaction['action']} {transaction['amount']}")
        print("-------------------\n")

# Class representing the overall bank system
class BankSystem:
    def __init__(self, data_file='bank_data.json'):
        self.data_file = data_file  # Set the file to store account data
        self.encryption_manager = EncryptionManager()  # Initialize the encryption manager
        self.accounts = self.load_accounts()  # Load accounts from the data file

    # Load accounts from the JSON data file, decrypting them as necessary
    def load_accounts(self):
        if os.path.exists(self.data_file):  # Check if the data file exists
            with open(self.data_file, 'r') as f:  # Open the data file in read mode
                try:
                    data = json.load(f)  # Load the JSON data
                    accounts = {}
                    for acc_num, details in data.items():
                        accounts[acc_num] = BankAccount(
                            account_number=acc_num,
                            account_holder=self.encryption_manager.decrypt(details['account_holder']),
                            balance=float(self.encryption_manager.decrypt(details['balance'])),
                            transactions=details.get('transactions', []),
                            encryption_manager=self.encryption_manager
                        )
                    return accounts
                except json.JSONDecodeError:
                    print("Error: Could not decode JSON data. The file might be corrupted.")
                    return {}
        return {}

    # Save the account details back to the JSON data file, encrypting them before saving
    def save_accounts(self):
        data = {acc_num: {
                    "account_holder": acc.encrypted_account_holder,
                    "balance": acc.encrypted_balance,
                    "transactions": acc.transactions
                }
                for acc_num, acc in self.accounts.items()}
        with open(self.data_file, 'w') as f:  # Open the data file in write mode
            json.dump(data, f, indent=4)  # Save the JSON data with indentation for readability

    # Create a new bank account
    def create_account(self, account_holder):
        account_number = str(random.randint(10000000, 99999999))  # Generate a random 8-digit account number
        while account_number in self.accounts:  # Ensure the account number is unique
            account_number = str(random.randint(10000000, 99999999))
        self.accounts[account_number] = BankAccount(account_number, account_holder, encryption_manager=self.encryption_manager)
        self.save_accounts()  # Save the newly created account
        print(f"Account created successfully. Account Number: {account_number}")

    # Find an account by its account number
    def find_account(self, account_number):
        return self.accounts.get(account_number)

    # Main menu to interact with the banking system
    def main_menu(self):
        while True:
            print("\n--- Welcome to the Banking System ---")
            print("1. Create Account")
            print("2. Deposit Money")
            print("3. Withdraw Money")
            print("4. Transfer Money")
            print("5. View Receipt")
            print("6. Exit")
            choice = input("Choose an option: ")

            if choice == "1":
                account_holder = input("Enter the account holder's name: ")
                self.create_account(account_holder)

            elif choice == "2":
                account_number = input("Enter your account number: ")
                account = self.find_account(account_number)
                if account:
                    amount = float(input("Enter amount to deposit: "))
                    account.deposit(amount)
                    self.save_accounts()  # Save after depositing
                else:
                    print("Account not found.")

            elif choice == "3":
                account_number = input("Enter your account number: ")
                account = self.find_account(account_number)
                if account:
                    amount = float(input("Enter amount to withdraw: "))
                    account.withdraw(amount)
                    self.save_accounts()  # Save after withdrawing
                else:
                    print("Account not found.")

            elif choice == "4":
                source_account_number = input("Enter your account number: ")
                source_account = self.find_account(source_account_number)
                if source_account:
                    target_account_number = input("Enter target account number: ")
                    target_account = self.find_account(target_account_number)
                    if target_account:
                        amount = float(input("Enter amount to transfer: "))
                        source_account.transfer(target_account, amount)
                        self.save_accounts()  # Save after transferring
                    else:
                        print("Target account not found.")
                else:
                    print("Source account not found.")

            elif choice == "5":
                account_number = input("Enter your account number: ")
                account = self.find_account(account_number)
                if account:
                    account.print_receipt()
                else:
                    print("Account not found.")

            elif choice == "6":
                print("Goodbye!")
                break

            else:
                print("Invalid choice. Please select a valid option.")
5
if __name__ == "__main__":
    bank = BankSystem()
    bank.main_menu()
