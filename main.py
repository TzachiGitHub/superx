import pymysql
import json
from app import app
from db_config import mysql
from flask import flash, session, render_template, request, redirect, url_for
from werkzeug import generate_password_hash, check_password_hash
		
@app.route('/add', methods=['POST'])
def add_product_to_cart():
	cursor = None
	try:
		_quantity = int(request.form['quantity'])
		_code = request.form['itemCode']
		# validate the received values
		print(1)
		if _quantity and _code and request.method == 'POST':
			cursor = mysql.cursor()
			values = (_code, )
			cursor.execute("SELECT itemCode, itemId, itemName, itemPrice FROM item_info WHERE itemCode=%s", values)
			row = cursor.fetchone()
			print(row)
			
			print(2)
			
			header = ['itemCode', 'itemId', 'itemName', 'itemPrice']
			data = []
			data.append(dict(zip(header, row)))
	
			cursor.close()
			row = data[0]
			#TODO - delete the 'row['itemPrice'] = int(1) ' row later - when we have a price on mysql
			row['itemPrice'] = int(1)
			print(type(row['itemPrice']))
			print("row ==")
			print(row)
			itemArray = { str(row['itemCode']) : {'name' : row['itemName'], 'code' : row['itemCode'], 'quantity' : _quantity, 'price' : row['itemPrice'], 'total_price': _quantity * row['itemPrice']}}
			all_total_price = 0
			all_total_quantity = 0
			print(3)
		
			session.modified = True
			if 'cart_item' in session:
				# print("session==")
				# print(session)
				# print("session['cart_item']==")
				# print(session['cart_item'])
				# print("row['itemCode'] ==")
				# print(row['itemCode'])
				# print("end")
				if row['itemCode'] in session['cart_item']:
					for key, value in session['cart_item'].items():
						if row['itemCode'] == key:
							print(4)

							#session.modified = True
							#if session['cart_item'][key]['quantity'] is not None:
							#	session['cart_item'][key]['quantity'] = 0
							old_quantity = session['cart_item'][key]['quantity']
							total_quantity = old_quantity + _quantity
							session['cart_item'][key]['quantity'] = total_quantity
							session['cart_item'][key]['total_price'] = total_quantity * row['itemPrice']
				else:
					print("4b")
					print(session)
					session['cart_item'] = array_merge(session['cart_item'], itemArray)
					print(session)
					print("end of 4b")
				for key, value in session['cart_item'].items():
					individual_quantity = int(session['cart_item'][key]['quantity'])
					individual_price = float(session['cart_item'][key]['total_price'])
					all_total_quantity = all_total_quantity + individual_quantity
					all_total_price = all_total_price + individual_price
			else:
				session['cart_item'] = itemArray
				all_total_quantity = all_total_quantity + _quantity
				all_total_price = all_total_price + _quantity * row['price']
			
			session['all_total_quantity'] = all_total_quantity
			session['all_total_price'] = all_total_price
			
			return redirect(url_for('.products'))
		else:			
			return 'Error while adding item to cart'
	except Exception as e:
		print(e)
		return "failed in /add - line 59"


@app.route('/')
def products():
	try:
		cursor = mysql.cursor()	
		cursor.execute("SELECT itemCode, itemName, itemId, itemPrice FROM item_info")
		# problem with the headers
		rows = cursor.fetchall()
		cursor.close() 
		header = ['itemCode', 'itemName', 'itemId', 'itemPrice']
		# header = ['id', 'name', 'code', 'image', 'price']
		
		data = []
		for row in rows:
			data.append(dict(zip(header, row)))
		
		return render_template('products.html', products=data)
	except Exception as e:
		print(e)
		return "failed"

@app.route('/empty')
def empty_cart():
	try:
		session.clear()
		return redirect(url_for('.products'))
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
		
		#return redirect('/')
		return redirect(url_for('.products'))
	except Exception as e:
		print(e)
		
def array_merge( first_array , second_array ):
	if isinstance( first_array , list ) and isinstance( second_array , list ):
		return first_array + second_array
	elif isinstance( first_array , dict ) and isinstance( second_array , dict ):
		return dict( list( first_array.items() ) + list( second_array.items() ) )
	elif isinstance( first_array , set ) and isinstance( second_array , set ):
		return first_array.union( second_array )
	return False		
		
if __name__ == "__main__":
    app.run(debug=True)