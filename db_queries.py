import MySQLdb
from sql_param import sql_param
from main import my_db, cur


def get_customers_total_number():
    """
    :return: Total Customers number
    """
    cur.execute("SELECT count(idcustomers_data) FROM customers_data")
    data = cur.fetchone()
    return data[0] if data else '0'


def get_customers_total_number_by_sub(sub_type):
    """
    :param: str: subscription type
    :return: Total Customers number per one subscription type
    """
    cur.execute("SELECT count(idcustomers_data) FROM customers_data WHERE sub_type= %s", [sub_type])
    data = cur.fetchone()
    return data[0] if data else '0'


def get_house_total_stat_by_num(house_num):
    """
    :param house_num: int: number of houses per one sub
    :return: tuple: (total_sub, total_income)
    """
    cur.execute(
        "SELECT count(idcustomers_data), SUM(total_paid) FROM customers_data WHERE sub_type= 'منزل' AND sub_count=%s",
        [house_num])
    data = cur.fetchone()
    return data


def get_customers_filtered_number(fltr):
    """
    :param fltr: str
    :return: total of customers using the filter
    """
    cur.execute("SELECT count(idcustomers_data) FROM customers_data WHERE active = %s", [fltr])
    data = cur.fetchone()[0]
    return data if data else '0'


def get_customers_with_filter(fltr):
    cur.execute(
        '''SELECT * FROM customers_data WHERE active = %s''', [fltr])
    data = cur.fetchall()
    return data


def get_last_id_by_branch(branch):
    """
    :param branch: str
    :return: Total customers in the branch
    """
    if branch == 'بسيون':
        cur.execute("SELECT MAX(idcustomers_data) FROM customers_data WHERE idcustomers_data LIKE '11%' ")
    data = cur.fetchone()
    return data[0]


def insert_new_customer(data):
    """
    :param data: list[] containing the customer data
    :return: None
    """
    cur.execute(
        '''INSERT INTO customers_data (idcustomers_data, name,nickname,phone_number,address,landmark,national_id,
        sub_type,sub_count,total_paid, last_pay_date, months, active) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
        data)

    my_db.commit()


def get_all_customers_data():
    """
    :return: tuple of all customers data

    """
    cur.execute(
        f''' SELECT * FROM customers_data ''')

    data = cur.fetchall()
    return data


def get_total_income():
    """
    :return: total income
    """
    cur.execute('''SELECT SUM(total_paid) from customers_data ''')
    data = cur.fetchone()
    return data[0] if data else '0'


def get_total_income_by_type(sub_type):
    """
    :param sub_type: str : subsctiption type
    :return: total income for one subsctiption type
    """
    cur.execute(f'''SELECT SUM(total_paid) from customers_data WHERE sub_type = %s''', [sub_type])
    data = cur.fetchone()
    return data[0] if data else '0'


def get_all_sub_types():
    """
    :return: tuple of all subscription types
    """
    cur.execute('''SELECT type FROM subscription_types ''')
    data = cur.fetchall()
    return data


def get_sub_price(sub):
    """
    :param sub: str
    :return data: int: subscription unit price
    """
    cur.execute('''SELECT price FROM subscription_types WHERE type=%s''', [sub])
    data = cur.fetchone()
    return data[0]


def get_customer_data_by_id(customer_id):
    """
    :param customer_id: str
    :return: tuple of customer data
    """
    cur.execute('''SELECT * FROM customers_data WHERE idcustomers_data=%s''', [customer_id])
    data = cur.fetchone()
    return data


def get_customers_data_by_name(name):
    """
    :param name: str
    :return: tuple of customer data
    """
    cur.execute('''SELECT * FROM customers_data WHERE name LIKE '%{}%' '''.format(name))
    data = cur.fetchall()
    return data


def get_customer_one_attr(customer_id, attr):
    """
    :param attr: str: attribute to get from database
    :param customer_id: str
    :return: str: attribute value for the customer
    """
    cur.execute(f'''SELECT {attr} FROM customers_data WHERE idcustomers_data=%s''', [customer_id])
    data = cur.fetchone()[0]
    return data


def update_customer_one_attr(customer_id, attr, value):
    """
    :param customer_id: str
    :param attr: str : attribute to update its value
    :param value: str: new value
    :return: None
    """
    cur.execute(f'''UPDATE customers_data SET {attr} =%s WHERE idcustomers_data=%s''', [value, customer_id])
    my_db.commit()


def reset_all_customers_sub():
    """
    Changes the value of one attribute to all records
    Used monthly to reset the customers subscription
    """
    cur.execute('''UPDATE customers_data SET active = 'لم يتم الدفع' ''')
    my_db.commit()


def update_customer_data(data):
    """
    :param data: list:  new values + customer_id
    :return: None
    """
    cur.execute(
        '''UPDATE customers_data SET name=%s, nickname=%s, phone_number=%s, address=%s, landmark=%s, national_id=%s,
         sub_type=%s, sub_count=%s WHERE idcustomers_data=%s''', data)
    my_db.commit()
