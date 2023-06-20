import random
from flask import Flask, render_template, redirect,url_for
from google.cloud import datastore
import google.oauth2.id_token
from flask import Flask, render_template, request
from google.auth.transport import requests


app = Flask(__name__)
datastore_client = datastore.Client()
firebase_request_adapter = requests.Request()


#########################  Create and Store UserInfo #########################


def createUserInfo(claims):
 entity_key = datastore_client.key('UserInfo', claims['email'])
 entity = datastore.Entity(key = entity_key)
 if "name" in claims.keys():
    ssName = claims["name"]
 else: 
    ssName = claims["email"]
 entity.update({
 'email': claims['email'],
 'name': ssName,
 'EV_list': []
 })
 datastore_client.put(entity)

def retrieveUserInfo(claims):
 entity_key = datastore_client.key('UserInfo', claims['email'])
 entity = datastore_client.get(entity_key)
 return entity

def checkUserData():
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    user_info = None
    addresses = None
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token,firebase_request_adapter)
        except ValueError as exc:
            error_message=str(exc)
    return claims
#########################  Create and Store EV info #########################
def createElectronic_Vehicle(claims, name, manufacturer, year, battery, range, cost, power):
    

    #reterive all EV
   query = datastore_client.query(kind="EV")
   query.add_filter('name', '=', name)
   query.add_filter('manufacturer', '=', manufacturer)
   query.add_filter('year', '=', year)
   result = query.fetch()
   count = 0
   for ev in list(result):
      count = count+1
   if count == 0:
      id = random.getrandbits(63)
      entity_key = datastore_client.key('EV', id)
      entity = datastore.Entity(key = entity_key)
      entity.update({
         'name': name,
         'manufacturer': manufacturer,
         'year': year,
         'battery': battery,
         'range': range,
         'cost': cost,
         'power': power,
         'review_list': [],
         'avg_r': 0

      })
      datastore_client.put(entity)
      return id
   else: 
      return False

def retrieveElectronic_Vehicles(id):
    entity_key = datastore_client.key('EV', id)
    entity = datastore_client.get(entity_key)
    return entity

def retrieveAllVehicles():
   EV_list = []
   query = datastore_client.query(kind="EV")
   result = query.fetch()
   EV_list.append(result)
   return EV_list



def retrieveElectronic_Vehicle(user_info):
 # make key objects out of all the keys and retrieve them
   EV_id = user_info['EV_list']
   EV_keys = []
   for i in range(len(EV_id)):
      EV_keys.append(datastore_client.key('EV', EV_id[i]))
   EV_list = datastore_client.get_multi(EV_keys)
  
   return EV_list
#########################  bind the vehicle info to the user #########################
def addElectronic_VehicleToUser(user_info, id):
   EV_keys = user_info['EV_list']
   EV_keys.append(id)
   user_info.update({
         'EV_list': EV_keys
   })
   datastore_client.put(user_info)

#########################  Update the EV info in the EV list #########################
def updateEV(id, name, manufacturer, year, battery, range, cost, power):
   entity_key = datastore_client.key('EV', id)
   EV = datastore_client.get(entity_key)
   EV.update({
            'name' : name,
            'manufacturer': manufacturer,
            'year': year,
            'battery': battery,
            'range': range,
            'cost': cost,
            'power': power,
   })
   datastore_client.put(EV)
   return EV
#########################  Delete the EV info from the EV list #########################
def deleteEV(claims, id):
    user_info = retrieveUserInfo(claims)
    EV_list_keys = user_info['EV_list']

    EV_key = datastore_client.key('EV', id)
    datastore_client.delete(EV_key)
    EV_list_keys.remove(id)
    user_info.update({
        'EV_list' : EV_list_keys
    })
    datastore_client.put(user_info)





#########################  Serach function to fetch all the EV info from the kind EV list #########################
def searchdata():
    EV = datastore_client.query(kind="EV")
    EV = EV.fetch()
    return EV
#########################  Create Userreview info #########################
def UserReview(username, reviewbox, rating):
    entity = datastore.Entity()
    entity.update({
        'username': username,
        'reviewbox': reviewbox,
        'rating': rating
    })
    return entity
#########################  Binding it to EV list the User review#########################
def EVReview(EV, review):
    result = EV['review_list']
    result.append(review)
    EV.update({
        'review_list': result
    })
    datastore_client.put(EV)
#########################  Calculating the Average  #########################
def Average(review):
    print(avg_r)
    avg_r = 0
    for i in review:
        avg_r = avg_r + i
    avg_r = avg_r/len(review)
    return round(avg_r, 1)

#########################  putting the average rating in the list #########################
def EVAverage(EV, rating):
    EV.update({
        'avg_r': rating
    })
    datastore_client.put(EV)

#########################  app route function for adding the EV info into the EV list #########################
@app.route('/add_Electronic_Vehicle', methods=["GET","POST"])
def addElectronic_Vehicle():
   id_token = request.cookies.get("token")
   user_data=None
   error_message = None
   user_info = None
   EV = None
   if request.method == "POST":
      if id_token:
         try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token,firebase_request_adapter)
            user_info = retrieveUserInfo(claims)
            id = createElectronic_Vehicle(claims, request.form['name'],request.form['manufacturer'], request.form['year'], request.form['battery'],request.form['range'],request.form['cost'],request.form['power'])
            if id != False:
               addElectronic_VehicleToUser(user_info, id)
         except ValueError as exc:
            error_message = str(exc)
      return render_template('add_Electronic_Vehicle.html', user_data=claims, error_message=error_message,user_info=user_info, EV=EV)
   else:
      if id_token:
         try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token,firebase_request_adapter)
            user_info = retrieveUserInfo(claims)
            EV=retrieveElectronic_Vehicle(user_info)
         except ValueError as exc:
            error_message = str(exc)
      return render_template('add_Electronic_Vehicle.html', user_data=claims, error_message=error_message,user_info=user_info)

#########################  app route function for Update the EV info from the EV list #########################
@app.route('/EVupdate/<int:id>', methods=['GET','POST'])
def update_vehicle(id):
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    EV = None
    user_info = None
    unique_id = id
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
        except ValueError as exc:
            error_message = str(exc)
    if request.method == 'POST':
      EV = updateEV(id, request.form['name'], request.form['manufacturer'], request.form['year'], request.form['battery'], request.form['range'], request.form['cost'], request.form['power'])
        
    return redirect(url_for("view_EV", id= unique_id,user_data=claims,user_info=user_info))






#########################  app route function for deleting the EV info from the EV list #########################
@app.route('/delete_EV/<int:id>', methods=['GET','POST'])
def deleteEVFromUser(id):
    id_token = request.cookies.get("token")
    error_message = None

    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
            deleteEV(claims, id)
        except ValueError as exc:
            error_message = str(exc)
        return redirect('/EV_list')




#########################  app route function for displaying the EV list with details#########################

@app.route('/EV_list', methods=["GET","POST"])
def list_Vehicle():
   id_token = request.cookies.get("token")
   user_data=None
   error_message = None
   user_info = None
   EV = None

   if id_token:
      try:
         claims = google.oauth2.id_token.verify_firebase_token(id_token,firebase_request_adapter)
         user_info = retrieveUserInfo(claims)
         EV=retrieveElectronic_Vehicle(user_info)
      except ValueError as exc:
         error_message = str(exc)
   return render_template('EV_list.html', user_data=claims, error_message=error_message,user_info=user_info,EV=EV)








#########################  app route function for serach the EV info from the EV list #########################

@app.route('/searchEV', methods=['GET','POST'])
def Search():
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    user_info = None
    if id_token:
            try:
                claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
            except ValueError as exc:
                error_message = str(exc)
    EV = searchdata()
    if request.method == 'POST':
        query = datastore_client.query(kind='EV')
        if request.form['name'] == '':
            pass
        else:
            name = request.form['name']
            query.add_filter('name', '=', name)

        if request.form['manufacturer'] == '':
            pass
        else:
            manufacturer = request.form['manufacturer']
            query.add_filter('manufacturer', '=', manufacturer)

        if request.form['year'] == '':
            pass
        else:
            year = request.form['year']
            query.add_filter('year', '=', year)

        if request.form['battery'] == '':
            pass
        else:
            battery = request.form['battery']
            query.add_filter('battery', '=', battery)

        if request.form['range'] == '':
            pass
        else:
            range = request.form['range']
            query.add_filter('range', '=', range)

        if request.form['cost'] == '':
            pass
        else:
            cost = request.form['cost']
            query.add_filter('cost', '=', cost)

        if request.form['power'] == '':
            pass
        else:
            power = request.form['power']
            query.add_filter('power', '=', power)
        EV = query.fetch()
    return render_template('searchEV.html', user_data=claims, error_message=error_message, user_info=user_info, EV=EV)

#########################  app route function for renderig the comparing page #########################
@app.route('/compare_page')
def comparecar():
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    user_info = None
    if id_token:
            try:
                claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
            except ValueError as exc:
                error_message = str(exc)

    return render_template('compare_page.html',user_data=claims, error_message=error_message, user_info=user_info)

#########################  app route function for adding the EV info for comparing the EV attributes #########################
@app.route('/add_compare_EV')

def InputEVcomparecars():
    id_token = request.cookies.get("token")
    claims = None
    user_info = None
    result = None
    error_message = None
    if id_token:
     try:
        claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
        query = datastore_client.query(kind="EV")
        result = query.fetch()
     except ValueError as exc:
         error_message = str(exc)
    return render_template("add_compare_EV.html",EV=result,error_message=error_message,user_data=claims,user_info=user_info)


#########################  app route function for Comparing  the EV  #########################
@app.route('/add_compare_EV', methods = ['POST'])
def comparingEV():
    claims = None
    user_info = None
    EV_list = []
    compare_list = []
    n_list = []
    result_list = request.form.getlist('input_cars')
    for i in result_list:
        EV_list.append(retrieveElectronic_Vehicles(int(i)))
    for index, j in enumerate(EV_list):
        compare_list.append(dict(EV_list[index]))
    print(compare_list)

    compareKeys = list()
    for j in compare_list:
        for key, values in j.items():
            if key == 'name' or key == 'manufacturer' or key == 'review_list':
                compareKeys.append(key)


    for key in compareKeys:
        for j in compare_list:
            if key in j:
                del j[key]
    n_list = [dict([a, float(int(x))] for a, x in c.items()) for c in compare_list]
    print(n_list)



    min_cost = min(value['cost'] for value in n_list)
    max_cost = max(value['cost'] for value in n_list)
    min_power = min(value['power'] for value in n_list)
    max_power = max(value['power'] for value in n_list)
    min_battery_size = min(value['battery'] for value in n_list)
    max_battery_size = max(value['battery'] for value in n_list)
    min_WLTP_range = min(value['range'] for value in n_list)
    max_WLTP_range = max(value['range'] for value in n_list)
    

    return render_template('compare_page.html', EV_list=EV_list, min_cost=min_cost, max_cost=max_cost, min_power=min_power, max_power=max_power, min_battery_size=min_battery_size, max_battery_size=max_battery_size, min_WLTP_range=min_WLTP_range, max_WLTP_range=max_WLTP_range,user_data=claims,user_info=user_info)


#########################  app route function for Viewing the EV info into the EV list #########################
@app.route('/View_vehicle/<int:id>', methods=['GET','POST'])
def view_EV(id):
   id_token = request.cookies.get("token")
   error_message = None
   claims = None
   EV = None
   user_info = None
   unique_id = None
   review = None
   avg_r = None
   review_list = []
   if id_token:
      try:
         claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
         user_info = retrieveUserInfo(claims)
         EV = retrieveElectronic_Vehicles(id)
         if request.method == "post":
            text = request.form['text1']
            rating = request.form['rating']
            email = user_info['email']
            review = UserReview(email, text, rating)
            EVReview(EV, review)
         for i in EV['review_list']:
            review_list.append(int(i['rating']))
            avg_r = Average(review_list)
            EVAverage(EV, avg_r) 
      except ValueError as exc:
         error_message = str(exc)
   
   return render_template('View_vehicle.html', user_data=claims, user_info=user_info, EV=EV, unique_id = id,review=review,avg_r=avg_r)







#########################  app route function for def root to render the home and index page according to login user info #########################

@app.route('/', methods=["GET","POST"])
def root():
   id_token = request.cookies.get("token")
   error_message = None
   claims = None
   user_info = None
   EV = None
   if request.method == "GET":
      if id_token:
         try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token,firebase_request_adapter)
            user_info = retrieveUserInfo(claims)
            if user_info == None:
               createUserInfo(claims)
               user_info = retrieveUserInfo(claims)
            EV =  retrieveElectronic_Vehicle(user_info)
         except ValueError as exc:
            error_message = str(exc)

      return render_template('home.html', user_data=claims, error_message=error_message,user_info=user_info,EV=EV)
   else:
      return render_template('index.html')



#########################  app route function for rredirecting the index page #########################
@app.route('/index', methods=["GET","POST"])
def mainpage():
   return render_template('index.html')





if __name__ == '__main__':
 app.run(host='127.0.0.1', port=8080, debug=True)


