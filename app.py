#!/usr/bin/python3

from flask import Flask, render_template, request, url_for, redirect
from werkzeug import secure_filename
import csv, os
import re
import unidecode

app = Flask(__name__)

##############################################################################
#la page root
@app.route('/')
def landing():
    return render_template('index.html')

##############################################################################
# Lecture du CSV
@app.route('/', methods = ['POST'])
def read_csv():
    if request.method == 'POST':
        csv_file = request.files['csv_file']
        if csv_file == '':
            return redirect(url_for('landing'))
        csv_file.save(secure_filename(unidecode.unidecode(csv_file.filename.replace(" ","_")) ))
        
    return render_template('index.html', upload_done=True, file_name=(unidecode.unidecode(csv_file.filename.replace(" ","_")) ))

##############################################################################
#Verification de la syntaxe du partition dans la page /verification   
@app.route('/verification/<csv_filename>')
def verification(csv_filename):
    content = read_file(csv_filename)
    is_correct = is_partition(content)
    return render_template('verification.html', is_correct=is_correct, file_name=csv_filename)

##############################################################################
# Redirection vers la page /Details pour afficher le contenu du ficher csv
@app.route('/details/<csv_filename>')
def details(csv_filename):
    content = read_file(csv_filename)
    status = getStatus(content)
    erreurs = is_harmonieuse(content)
    stats = getStat(content)
    return render_template('details.html', content=enumerate(content), status=status, erreurs=erreurs, stats = stats)

##############################################################################
#Récupération du contenu du fichier .csv et le retourner sous forme de liste
def read_file(csv_filename):
    file_path = os.path.join(os.path.dirname(__file__), csv_filename)
    with open(file_path) as temp_csv_file:
        reader = csv.reader(temp_csv_file)
        content = []
        for row in reader:
            content.append(row[0])
    return content

#########################################################################
#is_partition retourne True si la partition est correcte syntaxiquement. Faalse sinon   
def is_partition(partition):
    
    regex = ";\s?|[A-G](;[A-G])*\s?"
    
    for mesure in partition:
        if not re.fullmatch(regex, mesure): 
            return False
      
    return True 

##########################################################################
#is_accord retourne True si accord. Faalse sinon
def is_accord(mesure):
     
     mesure = mesure.split(";")   
     return (len(mesure) == 3) and ((ord(mesure[1]) - ord(mesure[0]) == 1) 
                        or (ord(mesure[2]) - ord(mesure[1]) == 2))
    
##########################################################################
#Retourner tous les accords de la partition     
def getAccords(partition):
    
    return [mesure for mesure in partition if is_accord(mesure)]    

##########################################################################
#Retourner tous les non-accords de la partition        
def getNonAccords(partition):
    
    return [mesure for mesure in partition if not is_accord(mesure) and mesure != ";"]   

##########################################################################
#Sauvegarder pour chaque mesure son status    
def getStatus(partition):
    
    status = {}
    for mesure in partition:
        
        if is_accord(mesure): status[mesure] = "Accord"
        elif mesure == ';' : status[mesure] = "Silence"
        else : status[mesure] = "Sans Accord" 
        
    return status   


#########################################################################
#Recuperer le nombre de silences, accords et sans accord dans la partition    
def getStat(partition):
    
    stats = {}
    stats["Accord"] = len(getAccords(partition))
    stats["SansAccord"] = len(getNonAccords(partition))
    stats["Silence"] = len(partition) - (len(getAccords(partition)) + len(getNonAccords(partition)))
    
    return stats

##########################################################################
#Lister les différentes erreurs d'harmonies détectées    
def is_harmonieuse(partition):
        
        notes = ["A","B","C","D","E","F","G"]
        erreurs = {}
        
        for indice, mesure in enumerate(partition[:-1]):
            
            suivante = partition[indice+1]
            
            if is_accord(mesure) and suivante == ";":
                erreurs[indice+1] = "Un accord ne peut être suivi d'un silence" 
            
            #not in [0,1,6] pour traiter le cas circulaire G-A
            if (is_accord(mesure) and is_accord(suivante)
              and abs(notes.index(mesure[0]) - notes.index(suivante[0]) ) not in [0,1,6]):
                  erreurs[indice+1] = "Si deux accords se suivent, ils doivent être au maximum espacés d'une note en hauteur"
                
            if mesure == ";" and not is_accord(suivante):
                erreurs[indice+1] = "Un silence doit être suivi d'un accord"
      
        if partition[-1] == ";" or is_accord(partition[-1]):
            erreurs[indice+1] = "La dernière mesure de la partition doit comporter une ou plusieurs mesures, sans accord"
        
        return erreurs
               
###################################################################################           


if __name__ == '__main__':
    app.run(debug=True, host= '0.0.0.0')
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    