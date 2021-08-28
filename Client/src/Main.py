#!/usr/bin/env python

import signal
from os import name, system
import sys
from API import Client


def catch_sigint(sig, frame):
    return


def clear():
    # for windows
    if name == 'nt':
        _ = system('cls')

    # for mac and linux(here, os.name is 'posix')
    else:
        _ = system('clear')


def main():
    while 1:
        clear()
        print("Welcome To The Bank,\n")
        print("Please choose an option to continue:")
        print("1. Open an Account")
        print("2. Login")
        try:
            choice = input("\n>>  ")
            choice.strip().split(" ")
            if choice[0] == "1":
                register()
            if choice[0] == "2":
                login()
        except EOFError:
            sys.exit(0)
        except IndexError:
            pass


def register():
    client = Client("127.0.0.1", 56789)
    clear()
    print("Please provide the following information:")
    first_name = input("First Name: ")
    last_name = input("Last Name: ")
    ssn = input("Social Security Number: ")
    res = client.register(ssn=ssn, first_name=first_name, last_name=last_name)
    clear()
    if res[0] == "REGISTER" and len(res) == 2:
        account_info = res[1].split(",")
        print("Your account has been opened! Please write down your account information in a safe place.\n")
        print(f"Account number:  {account_info[0]}\nSecret Pin: {account_info[1]}\n")
    else:
        print("An error has occurred during registration. Do you already have an account with us?\n")
    input("Press Enter To Continue")


def protected_routes(token):
    client = Client("127.0.0.1", 56789)
    client.token = token
    logged_in = True

    def check_balance():
        nonlocal logged_in
        clear()
        res = client.balance()
        if res[0] == "BALANCE" and len(res) == 2:
            balance = "{:.2f}".format(float(res[1]))
            print(f"Current Account Balance:    {balance}\n")
        else:
            print("There was an error processing your request.\n")
            logged_in = False
        input("Press Enter To Continue")

    def deposit():
        nonlocal logged_in
        clear()
        print("Please enter the following information:")
        amount = input("Amount To Deposit: ") or 0
        res = client.deposit(amount)
        clear()
        if res[0] == "DEPOSIT" and len(res) == 2:
            balance_info = res[1].split(",")
            prev_bal, balance = float(balance_info[0]), float(balance_info[1])
            actual_deposit = abs(balance-prev_bal)
            print("Deposit Successful!\n")
            print(f"Previous Balance: {prev_bal}")
            print(f"Amount Deposited: {actual_deposit}")
            print(f"Current Balance:  {balance}\n")
        else:
            print("There was an error processing your transaction.\n")
            logged_in = False
        input("Press Enter To Continue")

    def withdraw():
        nonlocal logged_in
        clear()
        print("Please enter the following information:")
        amount = input("Amount To Withdraw: ") or '0'
        res = client.withdraw(amount)
        clear()
        if res[0] == "WITHDRAW" and len(res) == 2:
            balance_info = res[1].split(",")
            prev_bal, balance = float(balance_info[0]), float(balance_info[1])
            actual_withdraw = abs(prev_bal-balance)
            if actual_withdraw > 0 or amount == '0':
                print("Withdraw Successful!\n")
                print(f"Previous Balance: {prev_bal}")
                print(f"Amount Withdrew: {actual_withdraw}")
                print(f"Current Balance:  {balance}\n")
            else:
                print("Withdraw Unsuccessful. Insufficient funds to complete transaction.\n")
        else:
            print("There was an error processing your transaction.\n")
            logged_in = False
        input("Press Enter To Continue")

    while logged_in:
        clear()
        print("Welcome! Please choose an option to continue:\n")
        print("1. Check Account Balance")
        print("2. Deposit Money")
        print("3. Withdraw Money")
        print("4. Logout")
        choice = input("\n>>  ").strip().split(" ")
        if choice[0] == "1":
            check_balance()
        elif choice[0] == "2":
            deposit()
        elif choice[0] == "3":
            withdraw()
        elif choice[0] == "4":
            logged_in = False


def login():
    clear()
    client = Client("127.0.0.1", 56789)
    print("Please provide the following information:")
    account_number = input("Account Number: ")
    pin = input("Secret Pin: ")
    res = client.authenticate(account_number, pin)
    clear()
    if res[0] == "AUTHENTICATE" and len(res) == 2:
        return protected_routes(res[1])
    else:
        print("Authentication Failed.\n")
        input("Press Enter To Continue")


if __name__ == '__main__':
    signal.signal(signal.SIGINT, catch_sigint)
    main()
