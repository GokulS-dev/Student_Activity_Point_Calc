from flask import Flask, request, jsonify, make_response, render_template, session, redirect, send_file
from werkzeug.utils import secure_filename
import jwt
from datetime import datetime, timedelta, timezone
from functools import wraps
from connection import get_mongo_client
import os
import easyocr
import pymongo
import pandas as pd
from bson import ObjectId
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DATABASE_URL")
secret_key = os.getenv("SECRET_KEY")

app = Flask(__name__)

# Specify the directory where uploaded files should be saved
UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'])

# Create the upload folder if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'])

app.config['SECRET_KEY'] = secret_key

def display_points(text):
    try:
        # Get the MongoDB client object
        client = get_mongo_client()
        print("Connected successfully!")

        db = client["SAP"]
        collection = db["COLLEGES"]

        # Initialize points
        points = 0

        # Iterate over the documents in the collection
        for college in collection.find():
            if text.find(college['college_name']) != -1:  # Check if college name exists in the text
                print(college)
                if college.get("institute_type") == "PREMIERE":
                    points += 30
            else:
                points += 10
            break
        return points  # Return the calculated points

    except pymongo.errors.ServerSelectionTimeoutError as e:
        print("Error connecting to the MongoDB cluster:", e)
        return None

    except Exception as e:
        print("An unexpected error occurred:", e)
        return None

    except pymongo.errors.ServerSelectionTimeoutError as e:
        print("Error connecting to the MongoDB cluster:", e)

    except Exception as e:
        print("An unexpected error occurred:", e)

def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        print(token)

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            # Decode the token
            payload = jwt.decode(token, app.config['SECRET_KEY'])
            # Pass the decoded token payload to the wrapped function
            return func(*args, **kwargs, user=payload['user'])
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401

    return decorated

# Home route
@app.route('/')
def home():
    return render_template('index.html')


# Student Login route
@app.route('/Student_login')
def Student_login(): 
    return render_template('Student_login.html')

# Faculty Login route
@app.route('/Faculty_login')
def Faculty_login():
    return render_template('Faculty_login.html')

# Public route
@app.route('/public')
def public():
    return 'For Public'

# Authenticated route
@app.route('/auth')
def auth():
    return jsonify({'message': f'JWT is verified. Welcome to your dashboard!'})

#Dhinesh123#
# Student Login route with POST method
@app.route('/Student_login', methods=['POST'])
def studentlogin():
    if request.method == 'POST':
        client = get_mongo_client()           
        db = client["SAP"]
        collection = db["StudentLogin"]
        user = collection.find_one({"email":request.form['email'],"password":request.form['password']})
        if user:
            name = user.get("name")
            rollno = user.get("rollno")
            semester = user.get("semester")
            print(user)
            session['logged_in'] = True
            token = jwt.encode({
                'user': request.form['email'],
                'expiration': str(datetime.now(timezone.utc) + timedelta(seconds=120))
            },
            app.config['SECRET_KEY'])
            return jsonify({'token': token, 'name': name, 'rollno': rollno, 'semester': semester})
        else:
            return make_response('Unable to verify', 403, {'WWW-Authenticate' : 'Basic realm:Authentication Failed!'})
        
# Faculty Login route with POST method
@app.route('/Faculty_login', methods=['POST'])
def facultylogin():
    if request.method == 'POST':
        client = get_mongo_client()           
        db = client["SAP"]
        collection = db["FacultyLogin"]
        user = collection.find_one({"email":request.form['email'],"password":request.form['password']})
        if user:
            session['logged_in'] = True
            token = jwt.encode({
                'user': request.form['email'],
                'expiration': str(datetime.now(timezone.utc) + timedelta(seconds=120))
            },
            app.config['SECRET_KEY'])
            return jsonify({'token': token, 'name': user.get("name")})
        else:
            return make_response('Unable to verify', 403, {'WWW-Authenticate' : 'Basic realm:Authentication Failed!'})
# Claim route
@app.route('/Claim')
def Claim():
    if not session.get('logged_in'):
        return redirect('/')
    return render_template('SAP.html')

# Student Home route
@app.route('/Student_home')
def Student_home():
    if not session.get('logged_in'):
        return redirect('/')
    return render_template('Student_home.html')

# Student Profile route
@app.route('/studentprofile')
def Student_profile():
    if not session.get('logged_in'):
        return redirect('/')
    return render_template('student_profile.html')

# Faculty Home route
@app.route('/Faculty_home')
def Faculty_home():
    if not session.get('logged_in'):
        return redirect('/')
    return render_template('Faculty_home.html')

# Faculty Profile route
@app.route('/facultyprofile')
def Faculty_profile():
    if not session.get('logged_in'):
        return redirect('/')
    return render_template('Faculty_profile.html')

# SAP Home route
@app.route('/sap_home')
def sap_home():
    if not session.get('logged_in'):
        return redirect('/')
    return render_template('sapindex.html')

# Techno route
@app.route('/Techno')
def Techno():
    if not session.get('logged_in'):
        return redirect('/')
    return render_template('Techno.html')

# Sports route
@app.route('/Sports')
def Sports():
    if not session.get('logged_in'):
        return redirect('/')
    return render_template('Sports.html')

# Membership route
@app.route('/Membership')
def Membership():
    if not session.get('logged_in'):
        return redirect('/')
    return render_template('Membership.html')

# Leadership route
@app.route('/Leadership')
def Leadership():
    if not session.get('logged_in'):
        return redirect('/')
    return render_template('Leadership.html')

# OnlineCourses route
@app.route('/OnlineCourses')
def OnlineCourses():
    if not session.get('logged_in'):
        return redirect('/')
    return render_template('OnlineCourses.html')

# Copyright route
@app.route('/Copyright')
def Copyright():
    if not session.get('logged_in'):
        return redirect('/')
    return render_template('Copyright.html')

# Govt route
@app.route('/Govt')
def Govt():
    if not session.get('logged_in'):
        return redirect('/')
    return render_template('Govt.html')

# Internships route
@app.route('/Internships')
def Internships():
    if not session.get('logged_in'):
        return redirect('/')
    return render_template('Internships.html')

@app.route('/approvesaps')
def Approvesaps():
    if not session.get('logged_in'):
        return redirect('/')
    return render_template('ApproveSaps.html')

# Entrepreneurships route
@app.route('/Entrepreneurships')
def Entrepreneurships():
    if not session.get('logged_in'):
        return redirect('/')
    return render_template('Entrepreneurships.html')

# Social route
@app.route('/Social')
def Social():
    if not session.get('logged_in'):
        return redirect('/')
    return render_template('Social.html')

# Retrive route
@app.route('/Retrive')
def Retrive():
    if not session.get('logged_in'):
        return redirect('/')
    return render_template('Retrive.html')

#Logout
@app.route('/logout')
def Logout():
    session['logged_in'] = False
    return redirect('/')

@app.route('/showsap')
def Showsap():
    rollno = request.args.get('rollno')
    try:
        client = get_mongo_client()
        print("Connected successfully!")            
        db = client["SAP"]
        collection = db["POINTS"]
        print(rollno)
        result = collection.find_one({"roll_no":rollno}) 
        print(result)  
        if result:
            # Convert ObjectId to string before returning the JSON response
            result['_id'] = str(result['_id'])
            return jsonify(result)  # Return the result as JSON
        else:
            return jsonify({"error": "Roll number not found"})  # Return JSON indicating the error     
    except pymongo.errors.ServerSelectionTimeoutError as e:
        print("Error connecting to the MongoDB cluster:", e)
        return jsonify({"error": "Error connecting to the database"})  # Return JSON indicating the error
    except Exception as e:
        print("An unexpected error occurred:", e)
        return jsonify({"error": "An unexpected error occurred"})  # Return JSON indicating the error
    
@app.route('/getclass')
def Getclass():
    section = request.args.get('section')
    try:
        client = get_mongo_client()
        print("Connected successfully!")            
        db = client["SAP"]
        collection = db["POINTS"]
        result = collection.find({"section": section})
        print(result)
        
        # Convert the cursor to a list of dictionaries
        data = list(result)
        
        if data:
            # Convert ObjectId to string in each dictionary
            for item in data:
                item['_id'] = str(item['_id'])
                
            return jsonify(data)  # Return the result as JSON
        else:
            return jsonify({"error": "Data not found"})  # Return JSON indicating the error
    except pymongo.errors.ServerSelectionTimeoutError as e:
        print("Error connecting to the MongoDB cluster:", e)
        return jsonify({"error": "Error connecting to the database"})  # Return JSON indicating the error
    except Exception as e:
        print("An unexpected error occurred:", e)
        return jsonify({"error": "An unexpected error occurred"})  # Return JSON indicating the error

# Getcsv route
@app.route('/download')
def Getcsv():
    client = get_mongo_client()
    db = client['SAP']
    collection = db['POINTS']
    option = request.args.get('option')
    cursor = collection.find({"section":option}) 
    data = list(cursor)
    df = pd.DataFrame(data)
    df.to_csv('sap_data.csv', index=False)
    print("Data exported to CSV successfully.")
    return send_file('sap_data.csv', as_attachment=True)

# Getrequest route
@app.route('/getrequests')
def Getrequests():
    try:
        client = get_mongo_client()
        db = client['SAP']
        collection = db['REQUESTS']
        cursor = collection.find({}) 
        data = list(cursor)

        # Convert ObjectId to string in each dictionary
        for item in data:
            item['_id'] = str(item['_id'])

        return jsonify(data)  # Convert data to JSON response
    except pymongo.errors.ServerSelectionTimeoutError as e:
        print("Error connecting to the MongoDB cluster:", e)
        return jsonify({"error": "Error connecting to the database"})
    except Exception as e:
        print("An unexpected error occurred:", e)
        return jsonify({"error": "An unexpected error occurred"})


# Process image route
@app.route('/Process_image', methods=['POST'])
def process():
    if request.method == 'POST':
        # Check if the request contains a file
        if 'file' not in request.files:
            return 'No file part'

        file = request.files['file']
        roll_no = request.form['roll_no']
        event = request.form['eventname']
        print(request.form)

        # If the user does not select a file, the browser submits an empty file without a filename
        if file.filename == '':
            return 'No selected file'

        # If the file is selected, save it
        if file:
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Process the uploaded file with EasyOCR
            result = reader.readtext(filepath)

            # Extract text from the result
            text_list = [item[1] for item in result]
            text = ' '.join(text_list)
            points = display_points(text.lower())

            try:
                # Get the MongoDB client object
                client = get_mongo_client()
                print("Connected successfully!")
                    
                db = client["SAP"]
                collection = db["REQUESTS"]

                collection.insert_one({"roll_no":roll_no,"points": points,"event":event,"date":datetime.now(),"filepath":filepath})
                
            except pymongo.errors.ServerSelectionTimeoutError as e:
                    print("Error connecting to the MongoDB cluster:", e)
                    return None

            except Exception as e:
                    print("An unexpected error occurred:", e)
                    return None

            except pymongo.errors.ServerSelectionTimeoutError as e:
                    print("Error connecting to the MongoDB cluster:", e)

            except Exception as e:
                    print("An unexpected error occurred:", e) 

            # return render_template('student_profile.html')
            return render_template('student_profile.html')
        
@app.route('/deleterequest', methods=['POST'])
def Deleterequest():
    if request.method == 'POST':
        data = request.json
        # print(data)
        try:
            client = get_mongo_client()
            print("Connected successfully!")            
            db = client["SAP"]
            collection = db["REQUESTS"]
            #{"roll_no":data['roll_no'],"points":data['points'],"event":data['event']}
            collection.delete_one({"_id": ObjectId(data['_id'])})
                
        except pymongo.errors.ServerSelectionTimeoutError as e:
            print("Error connecting to the MongoDB cluster:", e)
            return None

        except Exception as e:
            print("An unexpected error occurred:", e)
            return None

        return make_response("Data has been deleted!")
        
@app.route('/acceptrequest', methods=['POST'])
def Acceptrequest():
    if request.method == 'POST':
        data = request.json
        print(data)
        try:
            client = get_mongo_client()
            print("Connected successfully!")            
            db = client["SAP"]
            collection = db["POINTS"]
            collection.update_one({"roll_no":data['roll_no']},{"$inc":{"points":int(data['points'])}})
            db = client["SAP"]
            collection = db["REQUESTS"]
            collection.delete_one({"_id": ObjectId(data['_id'])})
            # print(data['_id'])
                
        except pymongo.errors.ServerSelectionTimeoutError as e:
            print("Error connecting to the MongoDB cluster:", e)
            return None

        except Exception as e:
            print("An unexpected error occurred:", e)
            return None

        return make_response("Data has been saved!")
    
@app.route('/viewrequest')
def Viewrequest():
    id = request.args.get('id')
    try:
        client = get_mongo_client()
        db = client["SAP"]
        collection = db["REQUESTS"]
        data = collection.find_one(ObjectId(id))
        data['_id'] = str(data['_id'])

    except pymongo.errors.ServerSelectionTimeoutError as e:
        print("Error connecting to the MongoDB cluster:", e)
        return None

    except Exception as e:
        print("An unexpected error occurred:", e)
        return None
    
    return jsonify(data)
#Student_home.html

@app.route('/submitParticipationForm', methods=['POST'])
def submitParticipationForm():
    if request.method == 'POST':
        try:
            dict_common = {}
            print(request.files)
            for key, value in request.form.items():
                dict_common[key] = value

            file = request.files['certificate']
            if file:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                dict_common['filepath'] = filepath
                dict_common['date'] = datetime.now()

            client = get_mongo_client()
            db = client["SAP"]
            collection = db["REQUESTS"]
            collection.insert_one(dict_common)

            return redirect('/studentprofile')

        except pymongo.errors.ServerSelectionTimeoutError as e:
            print("Error connecting to the MongoDB cluster:", e)
            return "Error connecting to the database", 500

        except Exception as e:
            print("An unexpected error occurred:", e)
            return "An unexpected error occurred", 500
    
#SAP.html
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))