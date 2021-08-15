import mariadb


pool = mariadb.ConnectionPool(
    pool_name='pool1',
    pool_size=3,
    pool_reset_connection=False,
    host='127.0.0.1',
    user='root',
    password='password',
    database='atm',
    autocommit=True
)


def get_connection():
    conn = pool.get_connection()
    cur = conn.cursor(named_tuple=True)
    return conn, cur


def register(ssn: str, first_name: str, last_name: str, account_num: str, pin: str) -> bool:
    res = False
    conn, cur = None, None
    try:
        conn, cur = get_connection()
        cur.execute("INSERT INTO `Users` (`ssn`, `first_name`, `last_name`) VALUES (?, ?, ?)",
                    (ssn, first_name, last_name))
        cur.execute("INSERT INTO `Accounts` (`number`, `pin`, `user_ssn`) VALUES (?, ?, ?)",
                    (account_num, pin, ssn))
        conn.close()
        conn.commit()
        res = True
    except Exception as e:
        print(f"Mariadb Error: {e}")
        if conn:
            conn.rollback()
            conn.close()
    finally:
        return res


def authenticate(account_num: str, pin: str) -> bool:
    res = False
    conn, cur = None, None
    try:
        conn, cur = get_connection()
        cur.execute("SELECT `pin` FROM `Accounts` WHERE `number`=?", (account_num,))
        row = cur.fetchone()
        conn.close()
        res = False if (row is None) else row.pin == pin
    except Exception as e:
        print(f"Mariadb Error: {e}")
        if conn is not None:
            conn.close()
    finally:
        return res


def balance(account_num):
    conn, cur = None, None
    try:
        conn, cur = get_connection()
        cur.execute("SELECT `balance` FROM `Accounts` WHERE `number`=?", (account_num,))
        row = cur.fetchone()
        conn.close()
        return None if row is None else row.balance
    except Exception as e:
        print(f"Mariadb Error: {e}")
        if conn:
            conn.close()
        return None


def deposit(account_num: str, amount: float):
    conn, cur = None, None
    try:
        conn, cur = get_connection()
        cur.execute("UPDATE Accounts SET `balance`=`balance`+? WHERE `number`=? AND `balance`+? >= 0",
                    (amount, account_num, amount))
        conn.commit()
        conn.close()
    except Exception as e:
        if conn:
            conn.close()


def withdraw(account_num: str, amount: float):
    return deposit(account_num, -amount)
