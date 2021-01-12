#python web service for amica

import json
import base64
import pymongo
from bson import json_util

dbclient = pymongo.MongoClient("mongodb://localhost:27017")
db = dbclient["amica_database"]
collection_auth = db["id_clients"]
collection_customer = db["customer"]	
collection_activity = db["activity_info"]
collection_total = db["total"]
collection_datatosync = db["data to sync"]

from flask import Flask
from flask import request
from flask import jsonify
from flask import render_template
from flask import send_file

app = Flask(__name__)

@app.route("/")
def home():
	return render_template('sign_up.html')
	

@app.route("/register")
def register():
	return render_template("sign_up.html")

@app.route("/accueil ")	
def accueil():
	return render_template('accueil.html')

@app.route("/auth/signup", methods=['POST'])
def auth_signup():
	base64_message = request.headers.get("Authorization").split(" ")[1]
	#print(base64_message)
	basic_auth = base64.b64decode(base64_message).decode("ascii")
	#print(basic_auth)
	name = basic_auth.split(":")[0]
	email = basic_auth.split(":")[1]
	password = basic_auth.split(":")[2]
	#print(name)
	#print(email)
	#print(password)
	
	signup_info = {'name':name, 'email':email, 'password':password}
	result = collection_auth.insert_one(signup_info)
	print(result)
	print(result.inserted_id)

	return jsonify('{"success":"true"}')
	
	
@app.route("/log_in")
def login():
	return render_template("log_in.html")

@app.route("/auth/login", methods=['POST'])
def auth_login():
	base64_message = request.headers.get("Authorization").split(" ")[1]
	#print(base64_message)
	basic_auth = base64.b64decode(base64_message).decode("ascii")
	#print(basic_auth)
	email = basic_auth.split(":")[0]
	password = basic_auth.split(":")[1]
	#print(email)
	#print(password)
	
	#check with the db
	query_find_user = {'email':email, 'password':password}
	match = collection_auth.find(query_find_user)
	print(match.count())
	if match.count() > 0:
		return jsonify('{"success":"true"}')
	else:
		return jsonify('{"success":"false"}')

#insert data into mongodb
@app.route("/postdata", methods=['POST'])
def postdata():
	get_collection_name = request.args.get('collection')
	content = request.get_json(silent=True)
	print(content)

	if get_collection_name == 'customer':
		collection_customer.insert_one(content)
	elif get_collection_name == 'activity':
		collection_activity.insert_one(content)
	else :
		collection_total.insert_one(content)
	
	return("request handled")

#data processing aka total
@app.route("/total")
def total():
	print("data processing ongoing")
	#data = collection_total.find_one({},{'_id': False})
	#print(json.loads(json_util.dumps(data)))
	#return json.loads(json_util.dumps(data))
	
	data = collection_datatosync.find_one({},{'_id': False})
	print(json.loads(json_util.dumps(data)))
	return json.loads(json_util.dumps(data))
	

@app.route("/dashboard/")
def dashboard():
	return render_template("d2.html")

@app.route("/weekly")
def weekly():
	return render_template("weekly.html")

@app.route("/img")
def img():
	image_number = request.args.get('weekly')
	if image_number == "1":
		filename="./img/dp_weekly1.png"
	else:
		filename="./img/dp_weekly2.png"
	return send_file(filename, mimetype="image/png")

if __name__ == '__main__':
	app.run(debug=True)
