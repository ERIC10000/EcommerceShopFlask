# Ecommerce Project
from flask import Flask, render_template, url_for, request, redirect, session
import pymysql

# Database Connection
# parameters -> host='localhost', user='root', password='', database='EcommerceShopDB'
connection = pymysql.connect(host='localhost', user='root', password='', database='EcommerceShopDB')
print("Database Connection Succesfull")


def check_customer():
    if 'email' in session:
        return True
    else:
        return False


def array_merge(first_array, second_array):
    if isinstance(first_array, list) and isinstance(second_array, list):
        return first_array + second_array
    # takes the new product add to the existing and merge to have one array with two products
    elif isinstance(first_array, dict) and isinstance(second_array, dict):
        return dict(list(first_array.items()) + list(second_array.items()))
    elif isinstance(first_array, set) and isinstance(second_array, set):
        return first_array.union(second_array)
    return False


# start
app = Flask(__name__)
app.secret_key = "ILOveProgramming"


@app.route('/', methods=['POST', 'GET'])
def products():
    if request.method == 'POST':
        search = request.form['search']
        cursor_search = connection.cursor()
        sql = 'SELECT * FROM products  medicines WHERE product_name LIKE "%{}%" ORDER BY RAND() LIMIT 6'.format(search)
        cursor_search.execute(sql)

        data = cursor_search.fetchall()

        return render_template('results.html', data=data, message="Search Results for {}".format(search))

    else:

        cursor_phones = connection.cursor()
        sql_phones = 'SELECT * FROM products WHERE product_category="phones" ORDER BY RAND() LIMIT 6'
        cursor_phones.execute(sql_phones)

        phones = cursor_phones.fetchall()

        cursor_electronic = connection.cursor()
        sql_electronics = 'SELECT * FROM products WHERE product_category="shoes" ORDER BY RAND() LIMIT 6'
        cursor_electronic.execute(sql_electronics)

        electronics = cursor_electronic.fetchall()

        cursor_gaming = connection.cursor()
        sql_gaming = 'SELECT * FROM products WHERE product_category="gaming" ORDER BY RAND() LIMIT 6'
        cursor_gaming.execute(sql_gaming)

        gaming = cursor_gaming.fetchall()

        cursor_sports = connection.cursor()
        sql_sports = 'SELECT * FROM products WHERE product_category="sports" ORDER BY RAND() LIMIT 6'
        cursor_sports.execute(sql_sports)

        sports = cursor_sports.fetchall()

        return render_template('myproducts.html', phones=phones, electronics=electronics, gaming=gaming, sports=sports)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        user_email = request.form['email']
        user_password = request.form['pswd']

        cursor = connection.cursor()
        sql = 'SELECT * FROM users WHERE user_email=%s AND user_password=%s'
        cursor.execute(sql, (user_email, user_password))

        if cursor.rowcount == 0:
            return render_template('login_signup.html', error="Invalid Credential Try Again")
        elif cursor.rowcount == 1:
            row = cursor.fetchone()
            session['key'] = row[1]  # user_name
            session['email'] = row[2]  # Email
            return redirect('/cart')
        else:
            return render_template('login_signup.html', error="Something Wrong with your Credentials")

    else:
        return render_template('login_signup.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':

        user_name = request.form['txt']
        user_email = request.form['email']
        user_password = request.form['pswd']
        cursor = connection.cursor()
        sql = 'INSERT INTO users (user_name, user_email, user_password) VALUES (%s,%s,%s)'
        cursor.execute(sql, (user_name, user_email, user_password))

        connection.commit()

        return render_template('login_signup.html', message="Registered Successfully")

    else:
        return render_template('login_signup.html')


@app.route('/single/<product_id>')
def single(product_id):
    cursor = connection.cursor()
    sql = 'SELECT * FROM products WHERE product_id=%s'
    cursor.execute(sql, product_id)

    row = cursor.fetchone()

    return render_template('single.html', item_data=row)


@app.route('/logout')
def logout():
    if 'key' in session:
        session.clear()
        return redirect('/login')


import requests
import base64
import datetime

from requests.auth import HTTPBasicAuth


@app.route('/mpesa_payment', methods=['POST', 'GET'])
def mpesa():
    if request.method == 'POST':
        phone = request.form['phone']
        amount = request.form['amount']

        consumer_key = "GTWADFxIpUfDoNikNGqq1C3023evM6UH"
        consumer_secret = "amFbAoUByPV2rM5A"

        api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))

        data = r.json()

        access_token = "Bearer" + ' ' + data['access_token']

        #  GETTING THE PASSWORD
        timestamp = datetime.datetime.today().strftime('%Y%m%d%H%M%S')

        passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
        business_short_code = "174379"

        data = business_short_code + passkey + timestamp
        encoded = base64.b64encode(data.encode())
        password = encoded.decode('utf-8')

        payload = {
            "BusinessShortCode": "174379",
            "Password": "{}".format(password),
            "Timestamp": "{}".format(timestamp),
            "TransactionType": "CustomerPayBillOnline",
            "Amount":amount,  # use 1 when testing
            "PartyA": phone,  # change to your number
            "PartyB": "174379",
            "PhoneNumber": phone,
            "CallBackURL": "https://modcom.co.ke/job/confirmation.php",
            "AccountReference": "Modcom",
            "TransactionDesc": "Modcom"
        }

        headers = {
            "Authorization": access_token,
            "Content-Type": "application/json"
        }

        url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

        response = requests.post(url, json=payload, headers=headers)
        print(response.text)

        return render_template('mpesa_payment.html', message="Please Check Your Phone for Payment")


    else:
        return render_template('mpesa_payment.html')


@app.route('/add', methods=['POST'])
def add_product_to_cart():
    _quantity = int(request.form['quantity'])
    _code = request.form['code']
    # validate the received values
    if _quantity and _code and request.method == 'POST':
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM products WHERE product_id= %s", _code)
        row = cursor.fetchone()
        # An array is a collection of items stored at contiguous memory locations. The idea is to store multiple items of the same type together

        itemArray = {str(row['product_id']): {'product_name': row['product_name'], 'product_id': row['product_id'],
                                              'quantity': _quantity, 'product_cost': row['product_cost'],
                                              'image_url': row['image_url'],
                                              'total_price': _quantity * row['product_cost'],
                                              'product_brand': row['product_brand']}}
        print((itemArray))

        all_total_price = 0
        all_total_quantity = 0
        session.modified = True
        # if there is an item already
        if 'cart_item' in session:
            # check if the product you are adding is already there
            print("The test cart", type(row['product_id']))
            print("session hf", session['cart_item'])
            if str(row['product_id']) in session['cart_item']:
                print("reached here 1")

                for key, value in session['cart_item'].items():
                    # check if product is there
                    if str(row['product_id']) == key:
                        print("reached here 2")
                        # take the old quantity  which is in session with cart item and key quantity
                        old_quantity = session['cart_item'][key]['quantity']
                        # add it with new quantity to get the total quantity and make it a session
                        total_quantity = old_quantity + _quantity
                        session['cart_item'][key]['quantity'] = total_quantity
                        # now find the new price with the new total quantity and add it to the session
                        session['cart_item'][key]['total_price'] = total_quantity * row['product_cost']

            else:
                print("reached here 3")
                # a new product added in the cart.Merge the previous to have a new cart item with two products
                session['cart_item'] = array_merge(session['cart_item'], itemArray)

            for key, value in session['cart_item'].items():
                individual_quantity = int(session['cart_item'][key]['quantity'])
                individual_price = float(session['cart_item'][key]['total_price'])
                all_total_quantity = all_total_quantity + individual_quantity
                all_total_price = all_total_price + individual_price

        else:
            # if the cart is empty you add the whole item array
            session['cart_item'] = itemArray
            all_total_quantity = all_total_quantity + _quantity
            # get total price by multiplyin the cost and the quantity
            all_total_price = all_total_price + _quantity * float(row['product_cost'])

        # add total quantity and total price to a session
        session['all_total_quantity'] = all_total_quantity
        session['all_total_price'] = all_total_price
        print(int(session['all_total_price']))
        return redirect(url_for('.cart'))
    else:
        return 'Error while adding item to cart'


@app.route('/cart')
def cart():
        return render_template('cart.html')



@app.route('/customer_checkout')
def customer_checkout():
    if check_customer():
        return redirect('/cart')
    else:
        return redirect('/signup')


@app.route('/empty')
def empty_cart():
    try:
        if 'cart_item' in session or 'all_total_quantity' in session or 'all_total_price' in session:
            session.pop('cart_item', None)
            session.pop('all_total_quantity', None)
            session.pop('all_total_price', None)
            return redirect(url_for('.cart'))
        else:
            return redirect(url_for('.cart'))

    except Exception as e:
        print(e)


@app.route('/delete/<string:code>')
def delete_product(code):
    try:
        all_total_price = 0
        all_total_quantity = 0
        session.modified = True
        for item in session['cart_item'].items():
            if item[0] == code:
                session['cart_item'].pop(item[0], None)
                if 'cart_item' in session:
                    for key, value in session['cart_item'].items():
                        individual_quantity = int(session['cart_item'][key]['quantity'])
                        individual_price = float(session['cart_item'][key]['total_price'])
                        all_total_quantity = all_total_quantity + individual_quantity
                        all_total_price = all_total_price + individual_price
                break

        if all_total_quantity == 0:
            session.clear()
        else:
            session['all_total_quantity'] = all_total_quantity
            session['all_total_price'] = all_total_price

        # return redirect('/')
        return redirect(url_for('.cart'))
    except Exception as e:
        print(e)


app.run(debug=True)
#  End App

# Jinja Templating Engine in Flask -> Python code can be written in html files
# variable {{variable}}
# {% python statement%}, if conditions, for loops

# {% for item in mydata%}
# {% endfor %}

# Sessions
