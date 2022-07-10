from flask import *
from flask_cors import CORS
from flask import session
import requests


app=Flask(__name__)
CORS(app)

app.config["JSON_AS_ASCII"] = False
app.config["TEMPLATES_AUTO_RELOAD"]=True

import mysql.connector

# connection pool
from mysql.connector import Error, pooling

# 取得 .env 裡的值
import os
from dotenv import load_dotenv
load_dotenv()
mysql_password = os.getenv("mysql_password")

pool = pooling.MySQLConnectionPool(
	host = "localhost",
	user = "jerry",
	password = mysql_password,
	database = "tourist_data",
	pool_name = "mypool",
	pool_size = 3,
)

app.secret_key="any string but secret" # 設定 Session 的密鑰

# Pages
@app.route("/")
def index():
	return render_template("index.html")
@app.route("/attraction/<id>")
def attraction(id):
	return render_template("attraction.html")
@app.route("/booking")
def booking():
	return render_template("booking.html")
@app.route("/thankyou")
def thankyou():
	return render_template("thankyou.html")

@app.route("/api/attractions")
def api_attractions():
	try:
		db_connection = pool.get_connection()
		my_cursor = db_connection.cursor()
		my_cursor.execute("SELECT COUNT(*) FROM `sub_data`")
		result = my_cursor.fetchone()
		if result != None:
			# 求資料長度
			data_count = result[0] # 資料長度
			data_count_for_page = data_count//12 # 每頁裝 12 筆，共有 (data_count_for_page)+1 頁

			# 兩個變數 page 和 keyword
			keyword = request.args.get("keyword")
			page_str = request.args.get("page")

			# 當 page 是大於等於0的整數:
			if page_str.isnumeric():
				page = int(page_str)
				# step1-1. 有 keyword
				if keyword != None:
					if page < data_count_for_page:
						nextPage = page+1
					else: nextPage = None
					page12 = str(page*12)
					my_cursor.execute("SELECT * FROM `sub_data` WHERE `name` LIKE '%"+keyword+"%' LIMIT "+page12+",13")
					keyword_result = my_cursor.fetchall()# 用 keyword 搜尋到的資料集合
					# step 2-1. 搜尋到的資料集合有東西
					if keyword_result != []:
						# 如果不到 12 筆
						show_keyword0_to_full = []
						if len(keyword_result)<12:
							for k in range(len(keyword_result)):
								keyword_data_k_9 = keyword_result[k][9].split(" ",-1)

								keyword_show = {
									"id": keyword_result[k][0],
									"name": keyword_result[k][1],
									"category": keyword_result[k][2],
									"description": keyword_result[k][3],
									"address": keyword_result[k][4],
									"transport": keyword_result[k][5],
									"mrt": keyword_result[k][6],
									"latitude": keyword_result[k][7],
									"longitude": keyword_result[k][8],
									"images": keyword_data_k_9
								}
								show_keyword0_to_full.append(keyword_show.copy())
							return jsonify({"nextPage":None,"data":show_keyword0_to_full}) # 沒有nextPage
						# 有到 12 筆
						else:
							for k in range(12):
								keyword_data_k_9 = keyword_result[k][9].split(" ",-1)

								keyword_show={
									"id": keyword_result[k][0],
									"name": keyword_result[k][1],
									"category": keyword_result[k][2],
									"description": keyword_result[k][3],
									"address": keyword_result[k][4],
									"transport": keyword_result[k][5],
									"mrt": keyword_result[k][6],
									"latitude": keyword_result[k][7],
									"longitude": keyword_result[k][8],
									"images": keyword_data_k_9
								}
								show_keyword0_to_full.append(keyword_show.copy())
							if len(keyword_result) == 12:
								return jsonify({"nextPage":None,"data":show_keyword0_to_full})# 沒有nextPage
							else:
								return jsonify({"nextPage":nextPage,"data":show_keyword0_to_full})
					# step 2-1. 搜尋到的資料集合沒有東西
					else:
						return jsonify({"error": True,"message": "沒有此關鍵字的資料"})
				
				# step1-2. 沒有 keyword，只有 page
				else:
					# 當 page 是數字
					page_is_N = page_str.isnumeric()
					if page_is_N:
						# page 在 4 之內
						if page <= data_count_for_page:
							# 處理 nextPage
							if page < data_count_for_page:
								nextPage = page+1
							else: nextPage = None

							# 用page把資料抓下來
							page12 = str(page*12)
							my_cursor.execute("SELECT * FROM `sub_data` LIMIT "+page12+",12")
							page_data = my_cursor.fetchall()
							show_page0_to_full = [] # 所有符合 page 的資料
							for j in range(12):
								if j+1 <= len(page_data):
									page_data_j_9 = page_data[j][9].split(" ",-1)

									page_show = {
										"id": page_data[j][0],
										"name": page_data[j][1],
										"category": page_data[j][2],
										"description": page_data[j][3],
										"address": page_data[j][4],
										"transport": page_data[j][5],
										"mrt": page_data[j][6],
										"latitude": page_data[j][7],
										"longitude": page_data[j][8],
										"images": page_data_j_9
									}
									show_page0_to_full.append(page_show.copy())
							return jsonify({"nextPage":nextPage,"data":show_page0_to_full})
							
						# page 不在 4 之內
						else:
							return jsonify({"error": True,"message": "超過分頁"})
			# 當 page 不是大於等於0的整數:
			else:
				return jsonify({"error": True,"message": "請輸入大於等於 0 的整數"})
		else:
			return jsonify({"error": True}), 400
	except:
		return jsonify({"error": True}), 500
	finally:
		db_connection.close()

@app.route("/api/attraction/<attractionId>")
def api_attraction_id(attractionId):
	try:
		db_connection = pool.get_connection()
		my_cursor = db_connection.cursor()
		my_cursor.execute("SELECT COUNT(*) FROM `sub_data`")

		result = my_cursor.fetchone()
		if result != None:
			# 求資料長度
			data_count = result[0] # 資料長度

			# 當 attractionId 是數字
			attractionid_is_N = attractionId.isnumeric()
			if attractionid_is_N:
				attractionId = int(attractionId)
				if attractionId > data_count:
					return jsonify({"error": True,"message": "景點編號太大"})
				elif attractionId < 1:
					return jsonify({"error": True,"message": "景點編號太小"})
				else:
					my_cursor.execute("SELECT * FROM `sub_data` WHERE `id`=%s" %attractionId)
					page_data = my_cursor.fetchone()
					page_data9 = page_data[9].split(" ",-1)

					page_show={
						"id": page_data[0],
						"name": page_data[1],
						"category": page_data[2],
						"description": page_data[3],
						"address": page_data[4],
						"transport": page_data[5],
						"mrt": page_data[6],
						"latitude": page_data[7],
						"longitude": page_data[8],
						"images": page_data9
					}
					return jsonify({"data": page_show})
			else:
				return jsonify({"error": True, "message" : "請輸入正整數"})
		else:
			return jsonify({"error": True}), 400
	except:
		return jsonify({"error": True}), 500
	finally:
		db_connection.close()

# @app.route("/api/user")
# def api_user_get():
	# if session!={}:
	# 	if session["email"]!="logout":
	# 		try:
	# 			db_connection=pool.get_connection()
	# 			my_cursor=db_connection.cursor()
	# 			my_cursor.execute("SELECT `id`,`name` FROM `user` WHERE email='%s'" %session["email"])
	# 			result=my_cursor.fetchone()
	# 			return jsonify({
	# 				"data":{
	# 					"id":result[0],
	# 					"name":result[1],
	# 					"email":session["email"]
	# 				}
	# 			})
	# 		except:
	# 			return jsonify({"error":True}), 500
	# 		finally:
	# 			db_connection.close()
	# 	else:
	# 		return jsonify({"data":None})
	# else:
	# 	return jsonify({"data":None})
	
# @app.route("/api/user", methods=["POST",])
# def api_user():
# 	name_signup=request.json["name_signup"]
# 	email_signup=request.json["email_signup"]
# 	password_signup=request.json["password_signup"]
# 	try:
# 		db_connection=pool.get_connection()
# 		my_cursor=db_connection.cursor()
# 		my_cursor.execute("SELECT `name`,`email`,`password` FROM `user` WHERE email='%s'" %email_signup)
# 		result=my_cursor.fetchone()
# 		if result!=None:
# 			return jsonify({"error":True,"message":"Email 已經被註冊"})
# 		else:
# 			my_cursor.execute("INSERT INTO user (name, email, password) VALUES (%s, %s, %s);", (name_signup, email_signup, password_signup))
# 			db_connection.commit()
# 			return jsonify({"ok":True}), 200
# 	except:
# 		return jsonify({"error":True}), 500
# 	finally:
# 		db_connection.close()

# @app.route("/api/user", methods=["PATCH"])
# def api_user_patch():
# 	email_login=request.json["email_login"]
# 	password_login=request.json["password_login"]
# 	try:
# 		db_connection=pool.get_connection()
# 		my_cursor=db_connection.cursor()
# 		my_cursor.execute("SELECT `name`,`email`,`password` FROM `user` WHERE email='%s'" %email_login)
# 		result=my_cursor.fetchone()
# 		if result!=None:
# 			# 登入成功
# 			if password_login==result[2]:
# 				session["email"]=result[1]
# 				return jsonify({"ok":True}), 200
# 			# 密碼錯誤
# 			else:
# 				return jsonify({"error":True,"message":"密碼錯誤"}), 400
# 		# 此Email 未註冊帳號
# 		else:
# 			return jsonify({"error":True,"message":"此Email 未註冊帳號"}), 400
# 	except:
# 		return jsonify({"error":True}), 500
# 	finally:
# 		db_connection.close()

# @app.route("/api/user", methods=["DELETE"])
# def api_user_delete():
# 	session["email"]="logout"
# 	return jsonify({"ok":True}), 200

from view.api_user import api_User

app.register_blueprint(api_User)

@app.route("/api/booking", methods=["POST"])
def api_booking_post():
	if session != {}:
		if session["email"] != "logout":
			attractionId = request.json["attractionId"]
			date = request.json["date"]
			time = request.json["time"]
			price = request.json["price"]
			if attractionId.isdigit() and (time == "上半天" or "下半天") and (price == "2500" or "2000"):
				try:
					db_connection = pool.get_connection()
					my_cursor = db_connection.cursor()
					my_cursor.execute("SET SQL_SAFE_UPDATES = 0")
					my_cursor.execute("UPDATE `user` SET `attractionId` = '"+attractionId+"', `date` = '"+date+"', `time` = '"+time+"', `price` = '"+price+"' WHERE `email` = '"+session["email"]+"'")
					db_connection.commit()
					return jsonify({"ok": True}), 200
				except:
					return jsonify({"error": True,"message":"伺服器內部錯誤"}), 500
				finally:
					db_connection.close()
			else:
				return jsonify({"error": True,"message":"錯誤的資料"}), 400
		else:
			return jsonify({"error": True,"message":"未登入"}), 403
	else:
			return jsonify({"error": True,"message":"未登入"}), 403
		
@app.route("/api/booking")
def api_booking_get():
	if session != {}:
		if session["email"] != "logout":
			try:
				db_connection = pool.get_connection()
				my_cursor = db_connection.cursor()
				my_cursor.execute("SELECT `date`,`time`,`price`,`attractionId` FROM `user` WHERE `email`='"+session["email"]+"'")
				result_user = my_cursor.fetchone()
				my_cursor.execute("SELECT `name`,`address`,`image` FROM `sub_data` WHERE `id` = '"+str(result_user[3])+"'")
				result_data=my_cursor.fetchone()
				if result_data == None:
					return jsonify({"data":None})
				return jsonify({
					"data": {
						"attraction": {
							"id": result_user[3],
							"name": result_data[0],
							"address": result_data[1],
							"image": result_data[2]
						},
						"date": result_user[0],
						"time": result_user[1],
						"price": result_user[2]
					}
				})
			except:
				return jsonify({"error": True,"message": "伺服器內部錯誤"}), 500
			finally:
					db_connection.close()
		else:
			return jsonify({"error": True,"message": "未登入"}), 403
	else:
		return jsonify({"error": True,"message": "未登入"}), 403
@app.route("/api/booking", methods = ["DELETE"])
def api_booking_delete():
	if session != {}:
		if session["email"] != "logout":
			try:
				db_connection = pool.get_connection()
				my_cursor = db_connection.cursor()
				my_cursor.execute("UPDATE `user` SET `date` = NULL, `time` = NULL, `price` = NULL, `attractionId` = NULL WHERE `email` = '"+session["email"]+"'")
				db_connection.commit()
				return jsonify({"ok": True})
			except:
				return jsonify({"error": True,"message": "伺服器內部錯誤"}), 500
			finally:
				db_connection.close()
		else:
			return jsonify({"error": True,"message": "未登入"}), 403
	else:
		return jsonify({"error": True,"message": "未登入"}), 403

# 到 .env 取 partner_key 和 merchant_id
partner_key = os.getenv("partner_key")
merchant_id = os.getenv("merchant_id")

order_number_list = []
for i in range(1,30):
	order_number_list.append(str(i).rjust(3,"0"))
@app.route("/api/orders", methods = ["POST"])
def api_orders_post():
	if session != {}:
		if session["email"] != "logout":
			try:
				prime = request.json["prime"]
				price = request.json["order"]["price"]
				date = request.json["order"]["trip"]["date"]
				time = request.json["order"]["trip"]["time"]
				phone = request.json["order"]["contact"]["phone"]
				name = request.json["order"]["contact"]["name"]
				contact_email = request.json["order"]["contact"]["email"]
				attractionId = request.json["order"]["trip"]["attraction"]["id"]
				# 須注意 "聯絡 email" 與 "登入 email" 一致
				email = request.json["order"]["contact"]["email"]
				db_connection = pool.get_connection()
				my_cursor = db_connection.cursor()
				# 生成訂單編號
				time_to_orderNumber = 0
				if time == "上半天":
					time_to_orderNumber = "1"
				else:
					time_to_orderNumber = "2"
				order_number = date.replace("-","")+time_to_orderNumber+phone[-8:]+order_number_list[0]
				order_number_list.remove(order_number_list[0])
				my_cursor.execute("SET SQL_SAFE_UPDATES = 0")
				my_cursor.execute("UPDATE `user` SET `phone` = '"+phone+"', `order status`='unpaid', `order number` = '"+order_number+"' WHERE `email` = '"+session["email"]+"' AND `date` = '"+date+"' AND `time` = '"+time+"'")
				my_cursor.execute("INSERT INTO `order_list` (`order_number`, `contact_name`, `contact_email`, `phone`, `attractionId`, `date`, `time`) VALUES ('"+str(order_number)+"', '"+name+"', '"+contact_email+"', '"+phone+"', '"+str(attractionId)+"', '"+date+"', '"+time+"');")
				db_connection.commit()
				res=requests.post("https://sandbox.tappaysdk.com/tpc/payment/pay-by-prime",
					headers={"Content-Type": "application/json", "x-api-key": partner_key} ,
					json={
						"prime": prime,
						"partner_key": partner_key,
						"merchant_id": merchant_id,
						"details": "TapPay Test",
						"amount": price,
						"cardholder": {
							"phone_number": phone,
							"name": name,
							"email": email
						},
						"remember": True
					}
				)
				
				Tappay_return=json.loads(res.text)
				if Tappay_return["status"] == 0:
					my_cursor.execute("UPDATE `user` SET `order status`='paid' WHERE `order number` = '"+str(order_number)+"'")
					my_cursor.execute("UPDATE `user` SET `attractionId`=NULL,`date` = NULL,`time` = NULL,`price`=NULL WHERE `email` = '"+session["email"]+"'")
					my_cursor.execute("UPDATE `order_list` SET `order_status` = 'paid' WHERE `order_number` = '"+str(order_number)+"'")
					db_connection.commit()
					return jsonify({"訂單編號": str(order_number), "message": "付款完成"})
				else:
					return jsonify({"訂單編號": str(order_number), "message": "付款未完成"})
			except mysql.connector.Error as err:
				print(err)
				return jsonify({"error": True, "message": "伺服器內部錯誤"}), 500
			finally:
				db_connection.close()
		else:
			return jsonify({"error": True, "message": "未登入"}), 403
	else:
		return jsonify({"error": True, "message": "未登入"}), 403

@app.route("/api/orders")
def api_orders_get():
	if session != {}:
		if session["email"] != "logout":
			try:
				db_connection = pool.get_connection()
				my_cursor = db_connection.cursor(buffered=True)
				order_number = request.args.get("number")
				my_cursor.execute("SELECT `contact_email`, `contact_name`, `phone`, `attractionId`, `date`, `time`, `order_status` FROM `order_list` WHERE `order_number` = '"+order_number+"'")
				order_get_result_data_user=my_cursor.fetchone()
				if order_get_result_data_user != None:
					my_cursor.execute("SELECT `name`, `address`, `image` FROM `sub_data` WHERE `id` = '"+str(order_get_result_data_user[3])+"'")
					order_get_result_data_subdata = my_cursor.fetchone()
					return jsonify({
						"data": {
							"number": order_get_result_data_user[0],
							"price": "price",
							"trip": {
								"attraction": {
									"id": order_get_result_data_user[3],
									"name": order_get_result_data_subdata[0],
									"address": order_get_result_data_subdata[1],
									"image": order_get_result_data_subdata[2]
								},
								"date": order_get_result_data_user[4],
								"time": order_get_result_data_user[5]
							},
							"contact": {
								"name": order_get_result_data_user[1],
								"email": order_get_result_data_user[0],
								"phone": order_get_result_data_user[2]
							},
							"status": order_get_result_data_user[6]
						}
					})
				else:
					return jsonify({"error": True, "message": "無此訂單"})
			except mysql.connector.Error as err:
				print(err, "error msg")
				return jsonify({"error": True, "message": "伺服器內部錯誤"}), 500
			finally:
				db_connection.close()
		else:
			return jsonify({"error": True, "message": "未登入"}), 403
	else:
		return jsonify({"error": True, "message": "未登入"}), 403

app.run(host="0.0.0.0",port=4000)