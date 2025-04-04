
from flask import Flask, render_template, request, send_file,redirect,url_for,session, jsonify
import database
from database import create_connection
import requests
import os
from datetime import timedelta


app = Flask(__name__)
app.secret_key = os.urandom(24)
app.permanent_session_lifetime = timedelta(minutes=30)

def create_user_profile(username, password):
    conn=create_connection()
    cursor=conn.cursor()
    cursor.execute('INSERT INTO users (user_username, user_password) VALUES (%s, %s)', (username, password))
    conn.commit()

def authenticate_user(username, password):
    conn=create_connection()
    cursor=conn.cursor()
    cursor.execute('SELECT user_id FROM users WHERE user_username=%s AND user_password=%s', (username, password))
    user_id = cursor.fetchone()
    return user_id[0] if user_id else None


@app.route('/',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_id = authenticate_user(username, password)
        if user_id:
            session.permanent = True
            session['user_id'] = user_id
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        create_user_profile(username, password)
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/index',methods=['GET','POST'])
def index():
    if 'user_id' in session:
    
        return render_template('invoice.html')
    else:
        return render_template('login.html')

@app.route('/data',methods=['GET','POST'])
def data():
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("select * from invoices ")
    res = cur.fetchall()
    return render_template('invoice_list.html',res=res)


@app.route('/insert',methods=['GET','POST'])
def insert():
    if request.method == 'POST':
        inv_name=request.form['invoice_name']
        inv_num=request.form['invoice_number']
        inv_date=request.form['date']
        bus_name=request.form['business_name']
        bus_email=request.form['business_email']
        item=request.form['item_description_1']
        item_qnt=request.form['item_quantity_1']
        item_price=request.form['item_price_1']
        conn=create_connection()
        cur = conn.cursor()
        cur.execute("insert into invoices (invoice_name,invoice_number,invoice_date,business_name,business_email,item,item_qnt,item_price) values (%s,%s,%s,%s,%s,%s,%s,%s)",(inv_name,inv_num, inv_date,bus_name,bus_email,item,item_qnt,item_price))
        conn.commit()
        return render_template('invoice.html')
@app.route('/invoice',methods=['GET','POST'])
def invoice():
    if request.method=="POST":
        id=int(request.form['invoice_id'])
        conn=create_connection()
        cursor=conn.cursor()
        cursor.execute("select * from invoices where id = %s",(id,))
        result=cursor.fetchall()
        for i in result:
            item_quantity=i[7]
            item_price=i[8]
            total=item_quantity*item_price

        #API_URL = "http://127.0.0.1:5050/converter"
        API_URL = "http://x23306882-currency-api.eba-yxxbrdce.ap-northeast-1.elasticbeanstalk.com/converter"
        try:
            ##translating the name
            json_data = {"text": total }
            response = requests.get(API_URL, json=json_data, stream=True)
            if response.status_code == 200:
                data = response.json()
                converted_amt = data.get("Converted Amt", "No amt converted")
                print("TRANSLATED TEXT ---------->> ",converted_amt)
            else:
                converted_amt = "Failed to Convert. Error from API."
        except Exception as e:
            converted_amt = f"An error occurred: {str(e)}"
    return render_template('generated_invoice.html', res=result,total=total,amt=converted_amt)

@app.route('/convert', methods=['POST'])
def convert_to_json():
    try:
        invoice_data = request.json.get("invoice")
        if not invoice_data:
            return jsonify({"error": "No invoice data provided"}), 400
        
        json_data = {"table": invoice_data}
        
        #pdf_response = requests.post("http://127.0.0.1:5051/export/pdf", json=json_data)
        pdf_response = requests.post("http://invoice-app-scalable.eba-yz8ny2hw.ap-northeast-1.elasticbeanstalk.com/export/pdf", json=json_data)
        
        if pdf_response.status_code == 200:
            return pdf_response.content, 200, {'Content-Type': 'application/pdf'}
        else:
            return jsonify({"error": "Failed to generate PDF"}), pdf_response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/delete/<int:id>',methods=['GET'])
def delete(id):
    id=int(id)
    # id=int(request.form['invoice_id'])
    conn=create_connection()
    cursor=conn.cursor()
    cursor.execute("delete from invoices where id = %s",(id,))
    conn.commit()
    return redirect(url_for('data'))


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))
    
""" if __name__ == '__main__':
    app.run(debug=True) """


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)

    


