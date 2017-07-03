from flask import Flask, render_template,request,redirect, url_for,send_file, send_from_directory, jsonify
from flask_wtf import FlaskForm
from wtforms.validators import InputRequired
from wtforms import *
from sqlparser import *
import socket
import re
import requests
from pymongo import MongoClient
from bson.json_util import dumps
import time
import os
from flask_socketio import SocketIO, emit


app = Flask(__name__)
app.config['SECRET_KEY'] = 'Thisisasecret!'
socketio = SocketIO(app)

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class QueryForm(FlaskForm):
   ip = TextField("IP", validators=[InputRequired()])
   port = TextField("Port", validators=[InputRequired()])
   selectlist = MultiCheckboxField('', choices= [('temperature', 'Temperature'), ('humidity', 'Humidity'),('brightness','Brightness')])
   attribute = SelectField('', choices = [('temperature', 'Temperature'), ('humidity', 'Humidity'), ('brightness', 'Brightness')])  
   operator = SelectField('', choices = [('<', '<'), ('>', '>'), ('=', '='), ('<=', '<='), ('>=','>=')])
   nombre = IntegerField("")
   number = IntegerField("Number:")
   periode = IntegerField("Periode:")
   text = TextAreaField("")
 

##################Added Code#####################
# Database configuration
client = MongoClient('localhost:27017')
db = client.capteurs # the database name is capteurs

@app.after_request
def add_header(res):
    res.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    res.headers["Pragma"] = "no-cache"
    res.headers["Expires"] = "0"
    res.headers['Cache-Control'] = 'public, max-age=0'
    return res

@app.route('/index')
def index():
    return send_file('public/index.html')

# charts page
@app.route('/charts')
def charts():
    return send_file('public/charts.html')

@app.route('/public/<path:filename>')
def serve_static(filename):
    #root_dir = os.path.dirname(os.getcwd())
    #print(os.path.join('.','public/'),filename)
    return send_from_directory(os.path.join('.','public/'),filename)


  # Call this to save your data
@app.route('/save/<int:node_id>/<int:temperature>/<int:humidity>/<int:seq>')
def saveData(node_id, temperature, humidity, seq):
    try:
        db.data.insert_one({'date':time.strftime("%Y-%m-%d %H:%M:%S") ,'node':node_id, 'temperature': temperature, 'humidity':humidity, 'seq':seq})
        socketio.emit('newData', {'data': 'New Data'})
        return jsonify(status='OK',message='inserted successfully')
    except e:
        return jsonify(status='ERROR', message=str(e))
  # Call this to retreive your data
@app.route('/getData')
def getData():
    try:
        data = db.data.find({}).sort('$natural',-1).limit(11)
        return dumps(data)
    except e:
        return jsonify(status='ERROR', message=str(e))

# Call this to get all Nodes
@app.route('/getNodes')
def getNodes():
    #print(db.data.find().distinct('node'))
    return jsonify(db.data.find().distinct('node'))

# Call this to get a specific node data
@app.route('/getNodeData/<int:id>')
def getNodeData(id):
    #print(db.data.find({'node':id}))
    return dumps(db.data.find({'node':id}).sort('$natural',-1).limit(10))

##################End Added Code###################
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            return redirect(url_for('form'))
    return render_template('login.html', error=error)
  

        

@app.route('/form', methods=['GET', 'POST'])
def form():
    form = QueryForm()
   
    check=""
  
    if form.validate_on_submit():
       
       for i in form.selectlist.data:
          check+= str(i)+" "
   
       form.text.data+='select {}for {} by {} where {} {} {}'.format(check, form.number.data, form.periode.data,form.attribute.data, form.operator.data , form.nombre.data)
       msg=yacc.parse(str(form.text.data))
       UDP_IP= format(form.ip.data)
       UDP_PORT= int(form.port.data)
       print "UDP target IP:", UDP_IP
       print "UDP target port:", UDP_PORT
       print "message:", msg 
      
       sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
       sock.bind(('aaaa::1', 3001,0,0)) 
       sock.sendto(msg, (UDP_IP, UDP_PORT))
       sock = socket.socket(socket.AF_INET6,socket.SOCK_DGRAM) # UDP
       sock.bind(('aaaa::1', 3001,0,0))
       # buffer size is 1024 bytes
       while True:
         w, addr = sock.recvfrom(1024)
         matchObj = re.match( 'node: (.*) t: (.*) l: (.*) seq: (.*) ', w)
         node_id     = matchObj.group(1)
         temperature = matchObj.group(2)
         humidity    = matchObj.group(3)
         seq         = matchObj.group(4)
         saveData(int(node_id), int(temperature), int(humidity), int(seq))
       
         print ("Data sent successfully")
     
       return render_template('index.html',form=form)
       
    return render_template('index.html',form=form)
    

if __name__ == '__main__':
    app.debug = True
    socketio.run(app)
    #app.run(debug=True)
