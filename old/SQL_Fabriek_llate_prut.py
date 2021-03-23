
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options 
import sqlite3
import re
import webbrowser
import time
from datetime import date
import os
from pathlib import Path

# advertentie tabel
	# status:		geen
					# STAR		
	
	# status_item: 	VIEW
					# HIDE		afhankelijk van zoekterm, maar kan misschien ook met SQL opgelost

# verkoper tabel
	# status: 		schermafdruk
					


# items zoekterm wel niet meenemen
# item verkopers wel niet meenemen
# schermafdruk + datum

#verkopertabel toevoegen: STAR, HIDE, niet

# nieuwe items: zonder screenshot
# verdwenen items: scrape datum is ouder dan de laatste scrape datum
# totaal = laatste scrape + oude scrapes




wijk = 'Rotterdam-Zuid'
DRIVER_PATH ='/home/remco/OneDrive/Klanten/Rotterdam Feijenoord/sublime/chromedriver'
minimum_prijs_verkoper = '35'  # in de inventaris van de verkoper
minimum_prijs = '5000' #bij het zoeken door advertenties heen (blijkbaar in centen...)

postcodes= ('3071','3072','3073','3074','3075','3076','3077','3078','3079','3081','3082','3083','3084','3085')
#postcodes= ('3071','3072')


def nummer_uit_MP_string(mpstring):
	print(mpstring)
	mpstring = mpstring.replace('https://www.marktplaats.nl/u/','')
	mpstring = mpstring[:-1]
	mpstring = mpstring.split("/")
	return mpstring[1]

def naam_uit_MP_string(mpstring):
	print(mpstring)
	mpstring = mpstring.replace('https://www.marktplaats.nl/u/','')
	mpstring = mpstring[:-1]
	mpstring = mpstring.split("/")
	return mpstring[0]

	
	




def create_SQL_tables():
	connection = sqlite3.connect('MP_'+wijk)   
	c = connection.cursor()
	sql=("""CREATE TABLE IF NOT EXISTS verkoper(
														id 				INTEGER PRIMARY KEY, 
														verkoper_url 	TEXT, 
														titel	 		TEXT, 
														prijs 			REAL, 
														beschrijving 	TEXT,
														status			TEXT,
														status_item		TEXT,
														reserve			TEXT,
														timestamp 		DATETIME DEFAULT CURRENT_TIMESTAMP,
														
														CONSTRAINT unieke_goederen UNIQUE (verkoper_url, titel,  beschrijving)  
														
														); """)
																#prijs kan veranderen, maar advertentie is dan hetzelfde
	c.execute((sql))
	connection.commit()
	
	sql = ("""CREATE TABLE IF NOT EXISTS advertentielijst (
														id 				INTEGER PRIMARY KEY, 
														verkoper_url 	TEXT, 
														postcode,		INT,
														titel	 		TEXT, 
														prijs 			REAL, 
														beschrijving 	TEXT,
														zoekterm		TEXT,
														status			TEXT,
														status_item		TEXT,
														reserve2		TEXT,
														timestamp 		DATETIME DEFAULT CURRENT_TIMESTAMP,
														
														CONSTRAINT unieke_goederen UNIQUE (verkoper_url, titel, prijs, beschrijving)
														
														); """)
	c.execute(sql)
	connection.commit()
	
	
	
	c.close()
	connection.close()

def een_van_wat(aantal_paginas): # MP zegt pagina 1 van 13, dit geeft dan 13 terug
	print('een van wat??')
	print(aantal_paginas)
	
	nummer=''
	if aantal_paginas[-3].isdigit():
		nummer = aantal_paginas[-3]
	if aantal_paginas[-2].isdigit():
		nummer += aantal_paginas[-2]
	if aantal_paginas[-1].isdigit():
		nummer += aantal_paginas[-1]
	return int(nummer)
	#print (int(nummer))

def scrape_aanbod_verkoper(URL,status):  #verkoper van MP
	#create_SQL_table_verkoper()	
	verkoper_nummer = nummer_uit_MP_string(URL)
	verkoper_naam = naam_uit_MP_string(URL)
	
 	# options = webdriver.ChromeOptions()
	# options.headless = True
 	# driver = webdriver.Chrome(executable_path=DRIVER_PATH,options=options)
		
	driver = webdriver.Chrome(executable_path=DRIVER_PATH)
	driver.get(URL)	
	WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME,'mp-Listing')))

	inventaris = driver.find_elements_by_class_name('mp-Listing')
	print (len(inventaris))
	aantal_paginas = driver.find_element_by_class_name('mp-PaginationControls').find_element_by_class_name('mp-PaginationControls-pagination-amountOfPages').get_attribute("textContent")
	aantal_paginas = een_van_wat(aantal_paginas)
	print (aantal_paginas)
	for pagina in range(1,aantal_paginas+1):
				print('i: '+str(pagina))
				URL = f"https://www.marktplaats.nl/u/{verkoper_naam}/{verkoper_nummer}/p/{pagina}/"
				driver.get(URL)
				WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME,'mp-Listing')))
				advertenties = driver.find_elements_by_class_name('mp-Listing')
				print (len(advertenties))
		
				for advertentie in advertenties:
					try:
						verkoper_url = advertentie.find_element_by_class_name('mp-Listing--sellerInfo').find_element_by_class_name('mp-TextLink').get_attribute('href')
						titel = advertentie.find_element_by_class_name('mp-Listing-group').find_element_by_class_name('mp-Listing-title').text
						beschrijving = advertentie.find_element_by_class_name('mp-Listing-group').find_element_by_class_name('mp-Listing-description').text
						prijs = advertentie.find_element_by_class_name('mp-Listing-group--price-date-feature').find_element_by_class_name('mp-Listing-price')
						prijs2 = re.findall("\d+\,\d+",prijs.text)
						prijs = float(prijs2[0].replace(',','.'))
						if prijs < minimum_prijs_verkoper :
							print('te weinig')
							print (prijs)
							continue
						
					except Exception as e:
						print(e)
						print('continue')
						continue
					
					print("in SQL gaan stoppen: ... ......")				
					print(verkoper_url) 
					print(titel)
					print(beschrijving)
					print(prijs)
					#just to see someting working
					connection = sqlite3.connect('MP_'+wijk)   
					c = connection.cursor()
					
					c.execute("""INSERT OR IGNORE INTO verkoper (
														verkoper_url, 
														
														titel, 
														prijs, 
														beschrijving,
														
														status) 
																				 values (?,?,?,?,? )""",    (verkoper_url, titel, prijs, beschrijving, status))
					connection.commit()
					
	c.close()
	connection.close()		
	driver.close()

	print('driver closed')


	





def bepaal_MP_aantal_paginaas(URL):
	driver = webdriver.Chrome(executable_path=DRIVER_PATH)
	driver.get(URL)

	#WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'gdpr-consent-banner-accept-button'))).click()
	#WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/div[2]/div/article/div[1]/span[1]/i'))).click()
	
	
		
	aantal_paginas = driver.find_element_by_class_name('mp-PaginationControls').find_element_by_class_name('mp-PaginationControls-pagination-amountOfPages').get_attribute("textContent")
	nummer = ''
	print ('aantal paginaas '+ str(aantal_paginas))
	if aantal_paginas[-3].isdigit():
		nummer = aantal_paginas[-3]
	if aantal_paginas[-2].isdigit():
		nummer += aantal_paginas[-2]
	if aantal_paginas[-1].isdigit():
		nummer += aantal_paginas[-1]
	print('dus')
	print(nummer)
	driver.close()
	return int(nummer)
	
	

#find_number_of_pages('https://www.marktplaats.nl/u/janina/13766918/')



def maak_screenshot(URL):
	print('maak screenshot bezig')
	verkoper_naam = naam_uit_MP_string(URL)
	verkoper_nummer = nummer_uit_MP_string(URL)
	datum = date.today()
	datum = datum.strftime("%d-%b-%Y")
	aantal_paginaas = bepaal_MP_aantal_paginaas(URL)
	
		
	path = os.getcwd()
	path += '/verkopers/'
	path += f'{verkoper_nummer}/'

	options = webdriver.ChromeOptions()
	options.headless = True
	driver = webdriver.Chrome(executable_path=DRIVER_PATH,options=options)
	
	#range!
	for pagina in range(1,aantal_paginaas+1):
		URL = f"https://www.marktplaats.nl/u/{verkoper_naam}/{verkoper_nummer}/p/{pagina}/"
		print(URL)
		driver.get(URL)
		try:
			WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'gdpr-consent-banner-accept-button'))).click()
			WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/div[2]/div/article/div[1]/span[1]/i'))).click()
		except:
			print('niks te klikken')
		
		
		WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME,'mp-Listing')))
		S = lambda X: driver .execute_script('return document.body.parentNode.scroll'+X)
		driver.set_window_size(S('Width'), S('Height'))
		driver.find_element_by_tag_name('body').screenshot(F'{path}/{datum}_{verkoper_naam}_{verkoper_nummer}_p_{pagina}.png')
		scrape_voorraad_wat_is_verwijderd(URL)
		print('maak screenshot klaar')
	driver.close()
	  
	 
def maak_directory_verkoper(nummer):
	try:
		path = os.getcwd()
		path += '/verkopers/'
		path += f'{nummer}/'
		os.makedirs(path)
		
	except:
		print('pad bestaat wrs al')	

 
def archiveer_directory_verkoper(nummer):
	path_old = os.getcwd()
	path_old += '/verkopers/'
	path_old += f'{nummer}/'
		
	path_new = os.getcwd()
	path_new += '/verkopers/'
	path_new += f'ARCHIEF_VAN_{nummer}/'
	try:
		os.rename(path_old, path_new)
	except:
		print('pad bestond wrs al niet meer. Geen archief gemaakt')
	

 	
def scrape_MP_regio(zoekterm):	
	
	afstand = '1000'
	status = 'geen'
	status_item = 'VIEW'
	connection = sqlite3.connect('MP_'+wijk)   
	c = connection.cursor()
	
	
	for postcode in postcodes:
		print('* * nieuwe postcode * *')
		print(postcode, zoekterm)

		URL = f"https://www.marktplaats.nl/q/{zoekterm}/#PriceCentsFrom:{minimum_prijs}|distanceMeters:{afstand}|postcode:{postcode}|searchInTitleAndDescription:true"
						
		driver = webdriver.Chrome(executable_path=DRIVER_PATH)
		driver.get(URL)
		
		print('* * * *')
		print(URL)
		WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'gdpr-consent-banner-accept-button'))).click()
		WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/div[2]/div/article/div[1]/span[1]/i'))).click()

		try:
			WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'mp-PaginationControls')))
			print('De mp Pagination Controls zijn er wel!')
			time.sleep(1)
		except:
			print("empty")
			print('continue')
			continue
		driver = webdriver.Chrome(executable_path=DRIVER_PATH)
	driver.get(URL)	
	WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME,'mp-Listing')))
	inventaris = driver.find_elements_by_class_name('mp-Listing')
	print (len(inventaris))


	try:

		l= driver.find_element_by_xpath('//*[@id="content"]/div[2]/div[4]/nav/a')
		s= l.text
		print("Element exist -" + s)
	
	except NoSuchElementException:
		print("Element does not exist")



		# for pagina in range(1,aantal_paginas+1):
			# print('i: '+str(pagina))
			# URL = f"https://www.marktplaats.nl/q/{zoekterm}/p/{pagina}/#PriceCentsFrom:{minimum_prijs}|distanceMeters:{afstand}|postcode:{postcode}|searchInTitleAndDescription:true"
			# driver.get(URL)
			# try:
				# WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME,'mp-Listing')))
				# advertenties = driver.find_elements_by_class_name('mp-Listing')
				# print('MP LISTING DETECTED')
				# print (len(advertenties))
			# except:
				# print('lege pagina? no MP listings')
				# continue
			
			
			# for advertentie in advertenties:
				
				# try:
					# verkoper_url = advertentie.find_element_by_class_name('mp-Listing--sellerInfo').find_element_by_class_name('mp-TextLink').get_attribute('href')
					# titel = advertentie.find_element_by_class_name('mp-Listing-group').find_element_by_class_name('mp-Listing-title').text
					# beschrijving = advertentie.find_element_by_class_name('mp-Listing-group').find_element_by_class_name('mp-Listing-description').text
					# prijs = advertentie.find_element_by_class_name('mp-Listing-group--price-date-feature').find_element_by_class_name('mp-Listing-price')
					# prijs2 = re.findall("\d+\,\d+",prijs.text)
					# prijs = float(prijs2[0].replace(',','.'))
				# except:
					# print('Geen verkoper/prijs beschrijving in advertentie? -> continue')
					# continue
				
								
				# print(verkoper_url) #just to see someting working
				# c.execute("""INSERT OR IGNORE INTO advertentielijst (
													# verkoper_url, 
													# postcode,
													# titel, 
													# prijs, 
													# beschrijving,
													# zoekterm,
													# status,
													# status_item) 
																			# values (?,?,?,?,?,?,?,? )""",    (verkoper_url, postcode, titel, prijs, beschrijving, zoekterm, status, status_item))
				# connection.commit()
				
		
		# driver.close()
		# print('driver closed')
				
		
	# c.close()
	# connection.close()
	# driver.quit()
	print()
	print('** *** * *** * * *** * * **** * * *** *')
	print()

	print ('end')

#scrape_MP_regio()



def scrape_voorraad_wat_is_verwijderd(verkoper_url):
		print('wat is verwijderd')
		print(verkoper_url)
		connection = sqlite3.connect('MP_'+wijk)   
		c = connection.cursor()
		
		#test if verkoper is 'unstarred'
		sql = f"""	UPDATE verkoper SET status = 'verwijderd'
					WHERE    DATE (timestamp) < DATE('now', '-1 day')
					AND
					verkoper_url = '{verkoper_url}'"""
		c.execute(sql)
		connection.commit()
		c.close()
		connection.close()
	
def verander_status(URL, nieuwe_status):  #verander status van verkoper in 'advertentielijst' STAR /HIDE(misschien beter in verkoper lijst later)
		print('verander status')
		print(URL)
		print(nieuwe_status)
		connection = sqlite3.connect('MP_'+wijk)   
		c = connection.cursor()
		
		#test if verkoper is 'unstarred'
		sql = f"""	SELECT status 
					FROM 'advertentielijst' 
					WHERE verkoper_url = "{URL}" 
					LIMIT 1"""
		huidige_status = c.execute(sql)
		connection.commit()
		if huidige_status == "STAR":
			nieuwe_status = "geen"
		
		sql = f"""	UPDATE advertentielijst 
					SET status = '{nieuwe_status}' 
					WHERE verkoper_url = '{URL}'"""
		c.execute(sql)
		connection.commit()
		c.close()
		connection.close()

def lijst_hits():     # resultaat van alle zoektermen in tabel in aantal hits per verkoper 
	connection = sqlite3.connect('MP_Rotterdam-Zuid')   
	c = connection.cursor()
	sql = """
			SELECT verkoper_url, count(verkoper_url), status 
			FROM 'advertentielijst' 
			WHERE  status <> 'HIDE'
			AND status_item <> 'HIDE'
		
			GROUP BY verkoper_url 
			HAVING count(verkoper_url) > 1
			ORDER BY  count(verkoper_url) 
		
			DESC"""
	
	c.execute(sql)	
	data = c.fetchall()
	connection.commit()
	c.close()
	connection.close()
	return (data)
#HAVING count(verkoper_url) > 1  

def zoekterm_wel_meetellen(zoekterm):
	connection = sqlite3.connect('MP_Rotterdam-Zuid')   
	c = connection.cursor()
	sql = F"""
			
			UPDATE 'advertentielijst'
			SET status_item = 'VIEW' 
			WHERE zoekterm = '{zoekterm}'
			"""
	c.execute(sql)	
	connection.commit()
	c.close()
	connection.close()


def zoekterm_niet_meetellen(zoekterm):
	connection = sqlite3.connect('MP_Rotterdam-Zuid')   
	c = connection.cursor()
	sql = F"""
			
			UPDATE 'advertentielijst'
			SET status_item = 'HIDE' 
			WHERE zoekterm = '{zoekterm}'
			"""
	c.execute(sql)	
	connection.commit()
	c.close()
	connection.close()



def verkoper_lijst(): # verkopers uit de tabel 'verkoper' (dus met ster)
	connection = sqlite3.connect('MP_Rotterdam-Zuid')   
	c = connection.cursor()
	sql = """
			SELECT verkoper_url
			FROM 'verkoper' 
			GROUP BY verkoper_url
			ORDER BY verkoper_url 
	
	"""
	c.execute(sql)	
	data = c.fetchall()
	connection.commit()
	c.close()
	connection.close()
	print('verkoperlijst uit DB')
	return (data)

def verwijder_van_verkoperlijst(URL):
	connection = sqlite3.connect('MP_Rotterdam-Zuid')   
	c = connection.cursor()
	sql = F"""
			DELETE FROM 'verkoper' 
			WHERE verkoper_url = '{URL}'
			
	
	"""
	c.execute(sql)	
	connection.commit()
	c.close()
	connection.close()
	print(URL)
	print('deleted')


def verwijder_van_advertentielijst(zoekterm):
	connection = sqlite3.connect('MP_Rotterdam-Zuid')   
	c = connection.cursor()
	sql = F"""
			DELETE FROM 'advertentielijst' 
			WHERE zoekterm = '{zoekterm}'
			
	
	"""
	c.execute(sql)	
	connection.commit()
	c.close()
	connection.close()
	print('!deleted')



def bestaat_ie():
	connection = sqlite3.connect('MP_Rotterdam-Zuid')   
	c = connection.cursor()
	sql = """
	SELECT verkoper_url
	FROM advertentielijst
	WHERE verkoper_url = 'https://www.marktplaats.nl/u/benjamin/15207666/'
    """
	c.execute(sql)	
	row = c.fetchone()
	if row is None:
		print('nai')
	
	print()
	
def waarde_aanbod_huidig(URL):
	res=0
	connection = sqlite3.connect('MP_Rotterdam-Zuid')   
	c = connection.cursor()
	sql = f"""
			SELECT printf("%.2f",SUM(prijs))
			FROM 'verkoper' 
			WHERE verkoper_url = '{URL}'  
			AND status NOT IN ('verwijderd')
	
			"""
	c.execute(sql)	
	connection.commit()
	data = c.fetchone()
	data=data[0]
	# data =''.join(data)
	# data2 = re.findall("\d+\,\d+",data.text)
	#data = float(data.replace(',','.'))
	#data = format(data[0], '.2f')
	print(data)
	print('waarde huidig aanbod bepaald')
	print(type(data))
	
	c.close()
	connection.close()	
	return (data)

	#SELECT count(prijs) FROM 'verkoper' WHERE verkoper_url = 'https://www.marktplaats.nl/u/olena/27699755/'
	#SELECT SUM(prijs) FROM 'verkoper' WHERE verkoper_url = 'https://www.marktplaats.nl/u/olena/27699755/'
	
	#select * from advertentielijst where   date(timestamp) >= date('now', '-1 day')
	#SELECT  titel, verkoper_url, max(Timestamp) FROM verkoper GROUP BY date(Timestamp);   #meest recente

#waarde_aanbod_huidig('https://www.marktplaats.nl/u/olena/27699755/')

def lees_verkoper_voorraad(URL):
	connection = sqlite3.connect('MP_Rotterdam-Zuid')   
	c = connection.cursor()
	sql = f"""
			SELECT PRINTF("%.2f", prijs), titel  FROM 'verkoper' 
			WHERE verkoper_url = '{URL}'  
			AND status NOT IN ('verwijderd')
			ORDER BY prijs DESC
	
			"""
	c.execute(sql)	
	data = c.fetchall()
	connection.commit()
	
	print('waarde huidig aanbod bepaald')
	
	c.close()
	connection.close()	
	return (data)
	

#def waarde_voorraad_actueel(verkoper_url)
#SELECT SUM (prijs) FROM 'verkoper' WHERE verkoper_url = 'https://www.marktplaats.nl/u/benjamin/15207666/'

#def waarde_voorraad_tot_nu_toe(verkoper_url)

#def markeer_items_screenshot (verkoper_url)

def laatste_keer_zoeken(zoekterm):
	connection = sqlite3.connect('MP_Rotterdam-Zuid')   
	c = connection.cursor()
	sql = f"""
			SELECT date(timestamp) FROM advertentielijst 
			WHERE zoekterm = '{zoekterm}' 
			ORDER BY timestamp DESC LIMIT 1;
	
			"""
	c.execute(sql)	
	data = c.fetchone()
	connection.commit()
	c.close()
	connection.close()	
	return (data)	

def status_zoekterm(zoekterm):
	connection = sqlite3.connect('MP_Rotterdam-Zuid')   
	c = connection.cursor()
	sql = f"""
			SELECT status_item  FROM 'advertentielijst' 
			WHERE zoekterm = '{zoekterm}' 
			LIMIT 1;
	
			"""
	c.execute(sql)	
	data = c.fetchone()
	connection.commit()
	c.close()
	connection.close()	
	return (data)	




def laatste_scrape(URL):
	connection = sqlite3.connect('MP_Rotterdam-Zuid')   
	c = connection.cursor()
	sql = f"""
			SELECT date(timestamp) FROM verkoper 
			WHERE verkoper_url = '{URL}' 
			ORDER BY timestamp DESC LIMIT 1;
	
			"""
	c.execute(sql)	
	data = c.fetchone()
	connection.commit()
	
	print('laatste SCRAPE')
	print(data)
	print(type(data))
	
	c.close()
	connection.close()	
	return (data)	


#def update_verkoper(URL):
	# lees huidige waarde SQL
	# lees verwijderde waarde SQL
	# scrape 
	# bepaal verwijderd
	# lees huidige waarde SQL
	# lees verwijderder waarde SQL
	# als verschil -> foto
	
	




def timestampen():  # testje om te werken met timestamps
	connection = sqlite3.connect('MP_Rotterdam-Zuid')   
	c = connection.cursor()
	sql = """
	SELECT * 
	FROM 'advertentielijst' 
	WHERE DATETIME(timestamp) < '2021-03-11'
    """
	data=c.execute(sql)	
	connection.commit()

	for row in data:
		print(row)
		print()
		
#timestampen()

# verkopers = verkoper_lijst()
# data =()
# for URL in verkopers:
	# print(URL)
	# #data += URL
	# data_plus = lees_verkoper_voorraad(str(URL))
	#data += data_plus


#URL ="https://www.marktplaats.nl/u/benjamin/15207666/"
#a = verkoper_lijst()
#lees_verkoper_voorraad(URL)
