from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_pymongo import PyMongo
from bson import ObjectId
from datetime import datetime

app = Flask(__name__)
CORS(app)

# app.config['MONGO_DBNAME'] = 'Zomato'
app.config['MONGO_URI'] = 'mongodb+srv://tmxsmoke:aminocentesis@cluster0.zmgremb.mongodb.net/Zomato?retryWrites=true&w=majority'
mongo = PyMongo(app)

@app.route("/")
def welcome():
    return "Welcome to home page"


@app.route("/addDish", methods=["POST"])
def adddish():
    if request.method == 'POST':
        collection = mongo.db['dish']
        data = request.get_json()
        inserted_document = collection.insert_one(data)
        return jsonify('Dish has been added successfully')


@app.route("/menu", methods=["GET"])
def showmenu():
    if request.method == "GET":
        collection = mongo.db['dish']
        data = list(collection.find())
        for item in data:
            item['_id'] = str(item['_id'])        
        return jsonify(data)

    
@app.route("/delete/<string:Id>", methods=["DELETE"])
def deleteDish(Id):
    collection = mongo.db.dish
    result = collection.delete_one({"_id": ObjectId(Id)})
    
    if result.deleted_count > 0:
        return jsonify("Dish has been removed successfully")
    
    return jsonify("Dish not found")



@app.route("/updateDish/<string:id>", methods=["PATCH"])
def updateDish(id):
    if request.method == "PATCH":
        data = request.get_json()
        collection = mongo.db['dish']
        filter_query = {'_id': ObjectId(id)}
        update_query = {'$set': {'Quantity': data['Quantity'], 'Name': data['Name'],"Price":data["Price"],"Img":data["Img"]}}
        result = collection.update_one(filter_query, update_query)

        if result.matched_count > 0:
            return jsonify("Successfully updated the quantity and name")

        return jsonify("Id not found")


@app.route("/order",methods=["POST"])
def oderDish():
    if request.method == "POST":
        data = request.get_json()
        collection2=mongo.db["order"]
        dish = mongo.db["dish"].find_one({"Name": data["food"]})
        value=int(dish["Quantity"])
        finddata=list(collection2.find())
        for i in range(len(finddata)):
           if finddata[i]["email"]==data["email"] and finddata[i]["food"]==data["food"]:
               return jsonify("Dish already exist")

        if dish:
            mongo.db["dish"].update_one({"Name":data["food"]},{"$set":{"Quantity":value-1}})
            # {"Name": name}, {"$set": {"status": "preparing"}}
            data["Quantity"]=1
            data["Price"] = dish["Price"] 
            data["Img"]=dish["Img"]
            data["status"] = "received"
            collection2.insert_one(data)
            return jsonify("Order Created Successfully")

        return jsonify("food not found")


@app.route("/allorder/<email>", methods=["GET"])
def getOrder(email):
  
    collection = mongo.db.order
    data = list(collection.find({"email":email}))
    for item in data:
            item['_id'] = str(item['_id'])
        
    return jsonify(data)



@app.route("/all",methods=["GET"])
def getAll():
    collection=mongo.db.order
    data=list(collection.find())
   
    for i in data:
        i["_id"]=str(i["_id"])
    
    return jsonify(data)

# @app.route("/showlogin", methods=["GET"])
# def getOrder1():
#     collection = mongo.db.login
#     logins = collection.find()
#     return jsonify([login for login in logins])


@app.route("/login", methods=["POST"])
def getlogin():
    logindata = request.get_json()
    collection = mongo.db.login
    if logindata["email"]=="admin@gmail.com" and logindata["password"]=="pankaj":
       return jsonify("Welcome Admin","Pankaj Vashisht") 

    login = collection.find_one({"email": logindata["email"], "password": logindata["password"]})
    if login:
        login["_id"]=str(login["_id"])
        return jsonify("Login Successful", login)

    return jsonify("Wrong Credentials", "")


@app.route("/Signup", methods=["POST"])
def getSignup():
    Signup = request.get_json()
    collection = mongo.db.login

    existing_user = collection.find_one({"email": Signup["email"]})
    if existing_user:
        return jsonify("Email already exists")

    collection.insert_one(Signup)
    return jsonify("Successfully Created Account")



@app.route("/updateOrderQuan/<string:_id>",methods=["PATCH"])
def updateQuantity(_id):
    collection = mongo.db.order
    order1 =collection.find_one({"_id": ObjectId(_id)})
    dish=mongo.db.dish.find_one({"Name":order1["food"]})
  
    ok=int(order1["Quantity"])+1
    ok=ok*int(dish["Price"])

    order2 = collection.update_one({"_id": ObjectId(_id)},{"$set":{"Quantity":order1["Quantity"]+1,"Price":ok}})
    dish2=mongo.db.dish.update_one({"Name":order1["food"]},{"$set":{"Quantity":dish["Quantity"]-1}})
    return jsonify("Quantity Updated successfully")



@app.route("/updateOrderQuannegative/<string:_id>",methods=["PATCH"])
def updateQuantitynegative(_id):
    collection = mongo.db.order
    order1 =collection.find_one({"_id": ObjectId(_id)})
    dish=mongo.db.dish.find_one({"Name":order1["food"]})
  
    ok=int(order1["Quantity"])-1
    ok=ok*int(dish["Price"])
    order2 = collection.update_one({"_id": ObjectId(_id)},{"$set":{"Quantity":order1["Quantity"]-1,"Price":ok}})
    dish2=mongo.db.dish.update_one({"Name":order1["food"]},{"$set":{"Quantity":dish["Quantity"]+1}})
    return jsonify("Quantity Updated successfully")




@app.route("/updateOrder/<time>/<value>", methods=["PATCH"])
def UpdateOrder(value,time):
    collection = mongo.db.Paid
    order = collection.find({"time":time})
    if order:
        
        collection.update_many({"time":time}, {"$set": {"status": value}})
        return jsonify("order status Changed Successfully")
       

    return jsonify("Order with this name doesn't exist")




@app.route("/deleteOrder/<string:id>/<food>",methods=["DELETE"])
def deleteOrder(id,food):
    #body=request.get_json()

    data=mongo.db.order.find_one({"_id":ObjectId(id)})
    val=int(data["Quantity"])
    dish=mongo.db.dish.find_one({"Name":food})
    val2=int(dish["Quantity"])

    dish2=mongo.db.dish.update_one({"Name":food},{"$set":{"Quantity":val+val2}})
    val3=mongo.db.order.delete_one({"_id":ObjectId(id)})
    return jsonify("dish deleted successfully")


@app.route("/getCheckout/<email>",methods=["GET"])    
def getCheck(email):
    print(email)
    collection1=mongo.db["Paid"]
    collection2 = mongo.db.order
    data = list(collection2.find({"email": email}))
    now=str(datetime.now())
    for i in data:
        i["time"]=now
    inserted=collection1.insert_many(data)
    deleted=collection2.delete_many({"email":email})
    return jsonify("Order Placed Successfully")


@app.route('/getOrderedData',methods=["GET"])
def getAlldata():
      collection=mongo.db["Paid"]
      data=list(collection.find())
      for i in data:
          i["_id"]=str(i["_id"])

      return jsonify(data)    


if __name__ == '__main__':
    app.run(port=3002)
