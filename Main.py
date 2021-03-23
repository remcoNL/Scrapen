from flask import Flask, render_template, request, url_for, redirect     
import sqlite3
import re
#import Zoektermen as zt
import SQL_Fabriek as sqlf

app = Flask(__name__)

@app.route("/zoek", methods=["POST", "GET"])
def zoek():
	sqlf.create_SQL_tables()
	if request.method == "POST":
		terug = request.form.get('zoeken')
		print('TERUG')
		print(terug)
		
		print(type(terug))
		
			
		if terug == 'addthistothat':
			zoekterm = request.form.get('nieuwe_zoekterm')
			if zoekterm is not None:
				sqlf.scrape_MP_regio(zoekterm)

# zoeken (scrape)		
		if terug[0] == 'Z':
			print('Z:zoek')
			print(zoekterm)
			zoekterm = str(terug[1:])
			sqlf.scrape_MP_regio(zoekterm)

# verwijderen		
		if terug[0] == 'X':
			zoekterm = terug[1:]
			print('X: verwijder')
			print(zoekterm)
			sqlf.verwijder_van_advertentielijst(zoekterm)


# meetellen	: VIEW	 	
		if terug[0] == 'V':
			zoekterm = str(terug[1:])
			sqlf.zoekterm_wel_meetellen(zoekterm)	
			print('V: view')

#niet meetellen : HIDE			
		if terug[0] == 'H':
			zoekterm = str(terug[1:])
			sqlf.zoekterm_niet_meetellen(zoekterm)	
			print('H: hide')
			

	data = sqlf.zoekterm_lijst_bepalen()	
	return render_template('zoek.html',data=data)


	#return render_template('zoek.html', data = data)


@app.route("/beoordelen", methods=["POST", "GET"])
def beoordelen():
	if request.method == "POST":	
		terug = str(request.form.get('handelaar'))
		status, verkoper_url = terug[:4], terug [4:] # eerste vier letters zijn HIDE of STAR
		verkoper_nummer  = sqlf.nummer_uit_MP_string(verkoper_url)
		sqlf.verander_status(verkoper_url,status) # HIDE of STAR in tabel
		
		if status == 'STAR':
				print('STAR *** *** **** **** verkoper volgen')
				print(verkoper_nummer)
				sqlf.maak_directory_verkoper(verkoper_nummer)
				status = 'schermafdruk'
				sqlf.scrape_aanbod_verkoper(verkoper_url,status)
				sqlf.maak_directory_verkoper(verkoper_nummer)
				sqlf.maak_screenshot(verkoper_url)
				
				
				
		if status == 'HIDE':	 #ook uit VOLG lijst verwijderen
				sqlf.verwijder_van_verkoperlijst(verkoper_url)
			
				
	data = sqlf.lijst_hits()
	return render_template("beoordelen.html", data=data)
	c.close()
	
@app.route('/archief', methods=["POST", "GET"])
def archief():
	if request.method == "POST":	
		terug = str(request.form.get('verkoper'))
		status, verkoper_url = terug[:4], terug [4:] # eerste vier letters zijn VIEW
		verkoper_nummer  = sqlf.nummer_uit_MP_string(verkoper_url)
	
		
		if status == 'HIDE':	 #ook uit VOLG lijst verwijderen
			sqlf.verwijder_van_verkoperlijst(verkoper_url)
			sqlf.verander_status(verkoper_url,"geen")
			sqlf.archiveer_directory_verkoper(verkoper_nummer)
		
	
	#verkoper_url = ("https://www.marktplaats.nl/u/benjamin/15207666/")
	verkopers = sqlf.verkoper_lijst()
	data =[]
	
	m=[]
	for URL in verkopers:
	
		URL =''.join(URL) #tuple to string
		verkoper_nummer = sqlf.nummer_uit_MP_string(URL)
		
		datum_laatste_scrape = sqlf.laatste_scrape(URL)
		datum_laatste_scrape = ''.join((datum_laatste_scrape))
		waarde_alles = '21'
		
		voorraad = sqlf.lees_verkoper_voorraad(URL)
			
		waarde = sqlf.waarde_aanbod_huidig(URL) 
		header =[URL, verkoper_nummer,waarde,datum_laatste_scrape,voorraad]
		data.append(header)
	
	
	
	
	return render_template('archief.html', data=data)


@app.route('/logout')
def logout():
    return render_template('logout.html')



  
if __name__ == "__main__":
    app.run(debug=True)
#SQL TABLE
#
c.close
connection.close
