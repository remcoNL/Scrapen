from flask import Flask, render_template, request, url_for, redirect     
import sqlite3
import re
import Zoektermen as zt
import SQL_Fabriek as sqlf

app = Flask(__name__)

@app.route("/zoek", methods=["POST", "GET"])
def zoek():
	if request.method == "POST":
		terug = request.form.get('submit')
		
		if terug == 'backtonormaltimesplease':
			zt.set_to_default()
		
		if terug == 'addthistothat':
			term = request.form.get('nieuwe_zoekterm')
			if term is not None:
				zt.toevoegen(term)
		
		if terug[0] == 'X':
			term = terug[1:]
			zt.verwijder(term)
		

	data = zt.lijst()	
	return render_template('zoek.html',data=data)


	#return render_template('zoek.html', data = data)


@app.route("/beoordelen", methods=["POST", "GET"])
def beoordelen():
	if request.method == "POST":	
		terug = str(request.form.get('handelaar'))
		status, handelaar = terug[:4], terug [4:]
		sqlf.verander_status(handelaar,status)
		print(terug)
		print(status)
		print(handelaar)
		
	
	connection = sqlite3.connect('MP_Rotterdam-Zuid')   
	c = connection.cursor()
	sql = "SELECT verkoper_url, count(verkoper_url), zoekterm, status FROM 'advertentielijst' GROUP BY verkoper_url  ORDER BY zoekterm, count(verkoper_url) DESC"
	data=c.execute(sql)	
	connection.commit()
		
			
	
	
	return render_template("beoordelen.html", data=data)
	c.close()
	
@app.route('/archief')
def archief():
    return render_template('archief.html')


@app.route('/logout')
def logout():
    return render_template('logout.html')



  
if __name__ == "__main__":
    app.run(debug=True)
#SQL TABLE
#
c.close
connection.close
