from flask import Flask, render_template      
import sqlite3
import re


postcode= 1052
zoek_op = 'iphone'
afstand = 1000
minimum_prijs = 50 *100



app = Flask(__name__)

@app.route("/beoordelen" )
def beoordelen():
	db = 'Postcode '+str(postcode)
	connection = sqlite3.connect(db)  
	connection.commit() 
	c = connection.cursor()

	sql = "SELECT verkoper_url, count(verkoper_url) FROM 'advertentielijst' GROUP BY verkoper_url  ORDER BY count(verkoper_url) DESC"

	data=c.execute(sql)
	connection.commit()
	return render_template("beoordelen.html", data=data)
    #c.close() 
    
if __name__ == "__main__":
    app.run(debug=True)
#SQL TABLE
#
c.close
connection.close
