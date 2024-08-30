# BankSystem-v0.1
BankSystem v0.1 is a Python-based banking system that enables users to manage accounts, perform transactions, and securely store sensitive data using encryption.

# Overview
*BankSystem v0.1 is a simple Python-based banking system that allows users to create and manage bank accounts, perform transactions such as deposits, withdrawals, and transfers, and view transaction receipts. The system uses encryption to securely store sensitive data, such as account holder names and balances.*

# Features
- Account Management: *Create new bank accounts with unique account numbers.*
- Secure Data Storage: *Encrypts sensitive information like account holder names, balances, and transactions using the Fernet encryption from the cryptography library.*
- Deposits and Withdrawals: *Easily deposit or withdraw money from your account.*
- Transfers: *Transfer money between accounts securely.*
- Transaction History: *View a detailed receipt of your recent transactions.*
- Data Persistence: *Account data is saved to a JSON file with encryption, ensuring that your data is preserved between sessions.*

# Installation
To use BankSystem v0.1, follow these steps:
1. Clone the Repository:
  git clone https://github.com/DinithSenarathna/banksystem-v0.1.git
  cd banksystem-v0.1
2. Install Dependencies:
   *This project requires Python 3.6 or later and the cryptography library. You can install the required dependencies using pip:*
   pip install cryptography
3. Run the Application:
  python banksystem.py

# Project Structure
.
├── banksystem.py          # Main application file
├── secret.key             # Generated encryption key (created after the first run)
├── bank_data.json         # Encrypted account data (created after the first run)
└── README.md              # This readme file

# Latest Updates
# Version 0.1
- Added encryption: *Sensitive data like account holder names and balances are now encrypted for security.*
- Improved transaction logging: *Transactions are logged and encrypted, making the system more secure.*

# Future Enhancements
- User Authentication: *Adding a login system with encrypted credentials.*
- Interest Calculation: *Automatically calculating and applying interest to savings accounts.*
- Improved UI: *Developing a graphical user interface (GUI) for a more user-friendly experience.*
