import threading
from typing import TypedDict
import mariadb


db_host = "127.0.0.1"
db_user = "root"
db_password = "password"
db_name = "atm"


class Balance(TypedDict):
    previous: float
    current: float


class AccountNotFoundError(Exception):
    def __init__(self, account: str, message="The specified account was not found."):
        self.account = account
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.account} -> {self.message}"


class UserExistsError(Exception):
    def __init__(self, ssn: str, message="An account already exists for the specified SSN."):
        self.ssn = ssn
        self.message = message
        super().__init__(self.message)


class AccountExistsError(Exception):
    def __init__(self, account: str, message="The specified account number is already being used."):
        self.account = account
        self.message = message
        super().__init__(self.message)


    def __str__(self):
        return f"{self.account} -> {self.message}"


class InvalidParameterError(Exception):
    def __init__(self, parameter: str, value: any, message: str):
        self.parameter = parameter
        self.value = value
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.parameter}: {self.value} -> {self.message}"


class OverdraftError(Exception):
    def __init__(self, balance: float, amount: float, message="Insufficient funds to complete transaction."):
        self.balance = balance
        self.amount = amount
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.balance} - {self.amount} = {self.balance-self.amount}\n{self.message}"


class Connection:
    transaction_lock = threading.Lock()
    registration_lock = threading.Lock()

    def __init__(self, host: str, user: str, password: str, database: str):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def __enter__(self):
        try:
            self.conn = mariadb.connect(host=self.host,
                                        user=self.user,
                                        password=self.password,
                                        database=self.database,
                                        autocommit=False
                                        )
            self.cur = self.conn.cursor(named_tuple=True)
            print("CONNECTION TO DATABASE OPENED")
            return self
        except Exception as e:
            print(e)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()
        print("CONNECTION TO DATABASE CLOSED")


def register(ssn: str, first_name: str, last_name: str, account_num: str, pin: str):
    validate(ssn=ssn, first_name=first_name, last_name=last_name, account_num=account_num, pin=pin)
    with Connection(db_host, db_user, db_password, db_name) as db, db.registration_lock:
        try:
            db.cur.execute("INSERT INTO `Users` (`ssn`, `first_name`, `last_name`) VALUES (?, ?, ?)", (ssn, first_name, last_name))
        except mariadb.IntegrityError:
            raise UserExistsError(ssn=ssn)
        try:
            db.cur.execute("INSERT INTO `Accounts` (`number`, `pin`, `user_ssn`) VALUES (?, ?, ?)", (account_num, pin, ssn))
        except mariadb.IntegrityError:
            raise AccountExistsError(account=account_num)
        db.conn.commit()


def getPin(account_num: str) -> str:
    validate(account_num=account_num)
    with Connection(db_host, db_user, db_password, db_name) as db:
        db.cur.execute("SELECT `pin` FROM `Accounts` WHERE `number`=?", (account_num,))
        res = db.cur.fetchone()
        if res is None: raise AccountNotFoundError(account_num)
        return res.pin


def getBalance(account_num: str) -> Balance:
    validate(account_num=account_num)
    with Connection(db_host, db_user, db_password, db_name) as db, db.transaction_lock:
        db.cur.execute("SELECT `balance` FROM `Accounts` WHERE `number`=?", (account_num,))
        res = db.cur.fetchone()
        if res is None: raise AccountNotFoundError(account_num)
        return {"previous": float(res.balance), "current": float(res.balance)}


def deposit(account_num: str, amount: float) -> Balance:
    validate(account_num=account_num, amount=amount)
    balance = {"previous": 0.0, "current": 0.0}
    with Connection(db_host, db_user, db_password, db_name) as db, db.transaction_lock:
        db.cur.execute("SELECT `balance` FROM `Accounts` WHERE `number`=?", (account_num,))
        res = db.cur.fetchone()
        if res is None: raise AccountNotFoundError(account_num)
        balance["previous"] = float(res.balance)
        db.cur.execute("UPDATE Accounts SET `balance`=`balance`+? WHERE `number`=?", (amount, account_num))
        db.conn.commit()
        db.cur.execute("SELECT `balance` FROM `Accounts` WHERE `number`=?", (account_num,))
        res = db.cur.fetchone()
        balance["current"] = float(res.balance)
        return balance


def withdraw(account_num: str, amount: float) -> Balance:
    validate(account_num=account_num, amount=amount)
    balance = {"previous": 0.0, "current": 0.0}
    with Connection(db_host, db_user, db_password, db_name) as db, db.transaction_lock:
        db.cur.execute("SELECT `balance` FROM `Accounts` WHERE `number`=?", (account_num,))
        res = db.cur.fetchone()
        if res is None: raise AccountNotFoundError(account_num)
        balance["previous"] = float(res.balance)
        if balance["previous"] - amount < 0.0: raise OverdraftError(balance=balance["previous"], amount=amount)
        db.cur.execute("UPDATE Accounts SET `balance`=`balance`-? WHERE `number`=? AND `balance`-? >= 0", (amount, account_num, amount))
        db.conn.commit()
        db.cur.execute("SELECT `balance` FROM `Accounts` WHERE `number`=?", (account_num,))
        res = db.cur.fetchone()
        balance["current"] = float(res.balance)
        return balance


def validate(**kwargs):
    account_num: str = kwargs.get('account_num', None)
    ssn: str = kwargs.get('ssn', None)
    first_name: str = kwargs.get('first_name', None)
    last_name: str = kwargs.get('last_name', None)
    amount: float = kwargs.get('amount', None)
    pin: str = kwargs.get('pin', None)
    if account_num is not None:
        if type(account_num) is not str: raise TypeError()
        if len(account_num) != 16: raise InvalidParameterError(parameter='account_num', value=account_num, message="Account number must be 16 characters in length.")
        if not account_num.isdecimal(): raise InvalidParameterError(parameter='account_num', value=account_num, message="Account number must contain only decimal characters 0-9")
    if ssn is not None:
        if type(ssn) is not str: raise TypeError()
        if len(ssn) != 9: raise InvalidParameterError(parameter='ssn', value=ssn, message="SSN must be 9 characters in length.")
        if not ssn.isdecimal(): raise InvalidParameterError(parameter=ssn, value=ssn, message="SSN must contain only decimal characters 0-9")
    if first_name is not None:
        if type(first_name) is not str: raise TypeError()
        if len(first_name) > 45: raise InvalidParameterError(parameter='first_name', value=first_name, message="First name must be 45 characters or less in length.")
    if last_name is not None:
        if type(last_name) is not str: raise TypeError()
        if len(last_name) > 45: raise InvalidParameterError(parameter='last_name', value=last_name, message="Last name must be 45 characters or less in length.")
    if amount is not None:
        if type(amount) is not float: raise TypeError()
        if amount < 0: raise InvalidParameterError(parameter="amount", value=amount, message="Amount must be greater than or equal to zero.")
    if pin is not None:
        if type(pin) is not str: raise TypeError()
        if len(pin) != 4: raise InvalidParameterError(parameter='pin', value=pin, message="Pin must be 4 characters in length.")
        if not pin.isdecimal(): raise InvalidParameterError(parameter='pin', value=pin, message="Pin must contain only decimal characters 0-9")
