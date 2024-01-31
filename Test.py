# -*- coding: utf-8 -*-
"""
Created on Wed May 13 23:18:27 2020

@author: manoj
"""
import subprocess,os
import sqlite3
from geopy.geocoders import Nominatim
import folium 
from IPython.core.display import HTML

#database='C:\Users\manoj\potholes.db'
con=sqlite3.connect("Potholes.db")
print("Database opened successfully")

#con.execute("create table Potholes (SlNo INTEGER PRIMARY KEY AUTOINCREMENT, Area TEXT, Data BLOB)")
print("Table created")  
con.close()
UPLOAD_FOLDER='static/images'
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
app=Flask(__name__,template_folder='template')
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


@app.route('/')
def home():
    return render_template('index1.html')

@app.route('/success', methods = ['POST'])  
def success():
    global text
    if request.method == 'POST':  
        file = request.files['file']  
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        text=request.form['text']
    print(text)

    from imageai.Detection.Custom import CustomObjectDetection

    detector = CustomObjectDetection()
    detector.setModelTypeAsYOLOv3()
    detector.setModelPath("Pothole Project/potts/models/detection_model-ex-012--loss-0004.504.h5")
    detector.setJsonPath("Pothole Project/potts/json/detection_config.json")
    detector.loadModel()
    detections = detector.detectObjectsFromImage(input_image='static/images/'+filename, output_image_path="static/images/po-detected.jpg")
    for detection in detections:        
        print(detection["name"], " : ", detection["percentage_probability"], " : ", detection["box_points"])
    with open(r'static/images/po-detected.jpg','rb') as f:
        data=f.read()
        #print(data)
    con=sqlite3.connect("Potholes.db")    
    cur = con.cursor()  
    cur.execute("""INSERT INTO Potholes ( Area, Data) VALUES (?,?)""",(text,data))  
    con.commit()  
    con.close()
    return render_template('success.html')



@app.route('/video', methods=['POST'])
def video():
        if request.method == 'POST':  
            file = request.files['file']  
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))  
@app.route('/list', methods=['POST'])
def listofpot():
    #return render_template('list1.html')

##@app.route('/display', methods=['POST'])
#def display():
    if request.method == 'POST':
        area=request.form['text']
        
    
    con=sqlite3.connect("Potholes.db")    
    cur = con.cursor()  
    img=cur.execute("""SELECT DATA FROM Potholes where Area=?""",(area,))
    for x in img:
        im=x[0]
    
    
    with open("static/images/db.png","wb") as f:
        f.write(im)
    con.commit()  
    con.close()
    return render_template("final.html", area=area)

@app.route('/viewmaps', methods = ['GET','POST'])
def maps():
    nom = Nominatim(user_agent = "test.py")
    n=nom.geocode(text)
    print(n.latitude,n.longitude)
    m = folium.Map(location = [n.latitude,n.longitude], zoom_start=20)
    folium.Marker(location=[n.latitude,n.longitude]).add_to(m)
    m.save('E:/Downloads/Project HTML CSS/template/myhtml.html')
    return render_template('myhtml.html')
    
        
    


    

app.run(debug = True, use_reloader=False)