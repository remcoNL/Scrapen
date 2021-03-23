import pickle
import SQL_Fabriek as sqlf
standaard_zoektermen = ["iphone", "nintendo","xbox", "goud", "met label er nog aan", "partij || partijen", "fiets", "scooter" , "rolex","goud"]
# aantal_zoektermen = len(standaard_zoektermen)

def set_to_default():
	f = open("zoektermen.pickle","wb")
	pickle.dump(standaard_zoektermen, f)
	f.close
	
def lijst():
	f = open("zoektermen.pickle","rb")
	zoektermen = pickle.load(f)
	f.close
	data=[]
	for zoekterm in zoektermen:
		A = zoekterm
	
		B = sqlf.laatste_keer_zoeken(zoekterm)
		C = sqlf.status_zoekterm(zoekterm)
		data.append ([A ,B,C])
	
	return data
	
def toevoegen(zoekterm):
	f = open("zoektermen.pickle","rb")
	zoektermen = pickle.load(f)
	f.close
	if not (zoekterm in zoektermen):
		#zoektermen.append(zoekterm)
		zoektermen.insert(0,zoekterm)
	f = open("zoektermen.pickle","wb")
	pickle.dump(zoektermen, f)
	f.close

def verwijder(zoekterm):
	f = open("zoektermen.pickle","rb")
	zoektermen = pickle.load(f)
	f.close
	
	print('we zijn in zoektermen')
	print(zoekterm)
	
	if (zoekterm in zoektermen):
		zoektermen.remove(zoekterm)
	f = open("zoektermen.pickle","wb")
	pickle.dump(zoektermen, f)
	f.close
	print('end')
	

#set_to_default()



	
