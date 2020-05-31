from flask import Flask,render_template,request,redirect,url_for,flash
from mysql.connector import Error
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.stem import WordNetLemmatizer
from flask_socketio import SocketIO, emit
import nltk
import mysql.connector
from flaskext.mysql import MySQL
import io
import random
import string 
import warnings
import numpy as np
import mysql
import warnings
import functools
import operator

warnings.filterwarnings('ignore')

app = Flask(__name__)
app.config[ 'SECRET_KEY' ] = 'jsbcfsdfghjbfjefebw237u3gdbdc'
socketio = SocketIO( app )
#config mysql database
conn = mysql.connector.connect(host='localhost',user='root',password='chatbot8399',database='chatbot')
#opennng textfile 
with open('chatbot.txt','r', encoding='utf8', errors ='ignore') as fin:
    raw = fin.read().lower()
sent_tokens = nltk.sent_tokenize(raw)
word_tokens = nltk.word_tokenize(raw)
lemmer = WordNetLemmatizer()

@app.route("/")
def index():
	return render_template("login.html", title="data")

@app.route("/login")
def login():
	return render_template("login.html",title="data")

@app.route("/checkUser",methods=['GET', 'POST'])
def check():
        check.username = str(request.form["user"])
        password = str(request.form["password"])
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM studentslist WHERE id ='"+check.username+"' && password ='"+password+"'")
        use = cursor.fetchall()
        
        if len(use) is 1:
                cursor.execute("SELECT name FROM studentslist WHERE id ='"+check.username+"'")
                name = cursor.fetchone()
                na = functools.reduce(operator.add, (name)) 
                flash("Hi  "+na)
                return redirect(url_for("home"))
        else:
                flash('Incorrect credentials')
                return redirect(url_for("login"))

#chatbot  code...............
def LemTokens(tokens):
    return [lemmer.lemmatize(token) for token in tokens]

remove_punct_dict = dict((ord(punct), None) for punct in string.punctuation)
def LemNormalize(text):
    return LemTokens(nltk.word_tokenize(text.lower().translate(remove_punct_dict)))


GREETING_INPUTS = ("hello", "hi", "greetings", "sup", "what's up","hey",)
GREETING_RESPONSES = ["hi", "hey", "*nods*", "hi there", "hello", "I am glad! You are talking to me"]

def greeting(sentence):
    """If user's input is a greeting, return a greeting response"""
    for word in sentence.split():
        if word.lower() in GREETING_INPUTS:
            return random.choice(GREETING_RESPONSES)
# Generatingresponse
def response(user_response):
    robo_response=''
    sent_tokens.append(user_response)
    TfidfVec = TfidfVectorizer(tokenizer=LemNormalize, stop_words='english')
    tfidf = TfidfVec.fit_transform(sent_tokens)
    vals = cosine_similarity(tfidf[-1], tfidf)
    idx=vals.argsort()[0][-2]
    flat = vals.flatten()
    flat.sort()
    req_tfidf = flat[-2]
    if(req_tfidf==0):
        robo_response=robo_response+"I am sorry! I don't understand you"
        return robo_response
    else:
        robo_response = robo_response+sent_tokens[idx]
        return robo_response

@app.route("/get",methods=['GET','POST'])
def get_bot_response():
        flag=True
        mycursor = conn.cursor()
        val=check.username
        while(flag==True):
                user_response = request.args.get('msg')
                user_response=user_response.lower()
                w=nltk.word_tokenize(user_response)
                if(user_response!='bye'):
                        if(user_response=='thanks' or user_response=='thank you' ):
                                flag=False
                                return str("You are welcome")
                        else:
                                if(greeting(user_response)!=None):
                                        return str(greeting(user_response))
                                else:
                                        if(w.count("attendance")>0):
                                                mycursor.execute("SELECT Attendence FROM studentslist WHERE Id='"+val+"'")
                                                tup=mycursor.fetchone()
                                                atten = functools.reduce(operator.add, (tup)) 
                                                return str(atten)
                                        else:
                                                if(w.count("percentage")>0):
                                                        mycursor.execute("SELECT percentage FROM studentslist WHERE Id='"+val+"'")
                                                        per=mycursor.fetchone()
                                                        perc = functools.reduce(operator.add, (per)) 
                                                        return str(perc)
                                                else:
                                                        if(w.count("address")>0):
                                                                mycursor.execute("SELECT address FROM studentslist WHERE Id='"+val+"'")
                                                                add=mycursor.fetchone()
                                                                addr = functools.reduce(operator.add, (add)) 
                                                                return str(addr)
                                                        else:
                                                                reply=response(user_response)
                                                                return str(reply)
                                                                sent_tokens.remove(user_response)
                else:
                        return str("you can logout with the help of logout button on top right corner. ")
 
@app.route('/logout')
def logout():
        return render_template('login.html')       
@app.route("/home")
def home():
	return render_template("index.html")
if __name__ == "__main__":
	socketio.run( app, debug = True )
