#!/usr/bin/env python3

"""Ce script réalise une extraction des données à partir de la base de données MongoDB
    
    Il se décompose en ... étpaes :
    
    2. Extraction des mots-clés de la base de données
    
    3. Récupération des phrases à partir de regex
    
    4. Extraction des chunk par classe

"""
import json
import yaml
import argparse
import sys
import pymongo
from pymongo  import MongoClient
from collections import defaultdict
import re
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns
from uuid import uuid4
from datetime import datetime

## Arguments
## words_diffamation text_diffamation 3

#sys.argv = ['c:\\Users\\Kaisensdata\\Explore_database\\explore_database.py', 'words_diffamation', 'text_diffamation', '3']

## Ouverture de la base de données ##

db_uri = "mongodb://localhost:27017/"
client = MongoClient(db_uri)

# affichage un objet
#print(client)
#print(type(client))

db_name = "CSVimports"
db = client[db_name]

#print(db)
#print(type(db))

#coll_name = "Mots_cles"
#coll = db[coll_name]

#print(coll)
#print(type(coll))

db.list_collection_names()

file_object = open("./utils/data.json", "r")
data = json.load(file_object)

#for elelment in data :
    #nom_classe_kw = data["keywords_class"] #.json import class --> argument = nom de la classe dans fichier
    

file_regex = open("./utils/regex.yml", "r")
data_regex = yaml.safe_load(file_regex)

## regex

def get_regex_data(list_key):
    return data_regex.get(list_key)

## Récupération des mots-clés par classe ##
def liste_mots_cles(nom_classe):
    words_classe = db.Mots_cles.find({"classe": nom_classe})

    liste = []
    
    for words in words_classe:
        nkww_liste = words["Insulte"]
        liste.append(nkww_liste)
        
    nkww_liste = "|".join(liste)
    return nkww_liste


##########mettre résultats dans un dico############

##Parcours des phrases pour trouver celles qui correspondent aux regex##
def parser_regex_old(text, kw_liste, list_regex):
    liste = []
    
    liste_adj = data_regex.get("liste_adj")
    liste_mot = data_regex.get("liste_mot")
    liste_intj = data_regex.get("liste_intj") 
    liste_post_kw = data_regex.get("liste_post_kw")
    liste_pron = data_regex.get("liste_pron")
    no_toxic = data_regex.get("no_toxic") 
    
    print(liste_adj)
    
    #for m in re.finditer("({adj}) ({keywords})".format(adj=liste_adj,keywords=kw_liste), text): #fichier yaml en argument
        #liste.append(m.group(0))
        #print(m.group(0))
    #return liste

def parser_regex(text, kw_liste, list_regex):
    liste = []
    
    ####Liste regex
    liste_adj = r"(esp(è|e)ce de|sales?|bande d(e|\')|putains? de|vieux|merdeux|gros(ses?)?|pe?tite?s?|(une?|de) vraie?s?|sombres?|pauvres?|quel|sacré(e)?)+" if "liste_adj" in list_regex else r''
    liste_mot = r"(vtf|va te faire|ta race|va chier|fuck|je t\'emmerde)" if "liste_mot" in list_regex else r''
    #suivi de : vtf, ntgrm, nique ta/ton/tes ..., ntm
    liste_intj = r"(vsy|va(z|s)(-)?y|alle(z|r)|donc|bon|va|te|ptn|putain)" if "liste_intj" in list_regex else r''

    #à mettre après les mots-clés :
    liste_post_kw = r"(sal(e)?|ptn|comme (lui|elle))" if "liste_post_kw" in list_regex else r''
    liste_pron = r"(toi|vos|ton|tes|aussi)?" if "liste_pron" in list_regex else r''
    no_toxic = r"^((j\'|tu|il) (as?|aurai(s|t)?) dit)" if "no_toxic" in list_regex else r''

    for m in re.finditer("({adj}) ({liste_mot}) ({liste_intj}) ({liste_post_kw}) ({liste_pron}) ({liste_pron}) ({no_toxic}) ({keywords})".format(
        adj=liste_adj,
        liste_mot=liste_mot,
        liste_intj=liste_intj,
        no_toxic=no_toxic,
        liste_pron=liste_pron,
        liste_post_kw=liste_post_kw,
        keywords=kw_liste), 
                         text):
        liste.append(m.group(0))
        #print(m.group(0))
    return liste

    #regex = re.compile((liste_adj) (liste_mot) (liste_pron) (no_toxic) (kw_liste) (liste_post_kw) (liste_intj))
    #for m in re.finditer(regex, text):
        #print() #faire un print en fonction de la sélection des utilisateurs
    #return

##application de la définition précédente pour avoir en sortie, la phrase parsée, la regex, la classe##
def explore_regex(keyw_list, list_regex):
    cursor = db.Toxicite.find({})

    res = []
    for item in cursor:
        res.append({
            "text":item['text'],
            "text_regex":parser_regex(item['text'], keyw_list, list_regex),
            "annotation": item['annotation-humaine']
        })
    
    res = list(filter(lambda item:len(item['text_regex']),res))
    return res

###CHUNK###

##Récupération des chunk par classe##

def ngrammes(text_class, n):
    mots = []
    stop_words = []
    file = open("./utils/stopwords.txt", "r")
    content = file.read()
    stop_words.append(content)
    file.close()
    
    #ouverture du fichier
    cursr = db.Toxicite.find({"annotation-humaine": text_class})

    texte = []
    for wds in cursr:
        texte.append(wds["text"])
        texte_str = ' '.join(texte)
        liste_words = texte_str.split()
        #print(texte)

    #suppression des stopwords    
    for e in liste_words:
        if e in stop_words:
            liste_words.remove(e)
    #print(liste_words)
            
    #récupération des ngram pour les mettre dans une liste
    mots.append(liste_words) #création d'une liste de mots
    #print(mots)
    l_ngram = []
    for i in range(len(liste_words)-(n-1)): #on calcule les n-grammes à partir de la liste créée
        word_list = []
        for a in range(n):
            word_list.append(liste_words[i+a])
        l_ngram.append(word_list)
        
    return l_ngram

def plot_schema(l_ngram):
    a = [' '.join(x) for x in l_ngram]
    liste =[]
    for i in a:
        b = i, a.count(i)
        liste.append(b)

    #création d'un dictionne : la clé est le n-gram, la valeur est le nombre d'occurrences

        #print(type(b))
    dico = dict(liste)
    # # print(dico)

    # for cle, valeur in dico.items():
    #     if valeur >= 3:
    #         print("chunks composés de", valeur, "mots :", cle)

            #Création d'un graphique pour afficher les n-gram les plus fréquents au moins fréquents

    x = []
    y = []
    top_ngram = dico.items()
    myList = sorted(top_ngram, key=lambda t: t[1], reverse = True)
    for key, value in myList:
        x.append(value)
        y.append(key)
        
    ## Visualisation des chunk les plus fréquents dans un graphique
    plt.figure(figsize=(10,7))
    swarm_plot = sns.barplot(x=x[:30],y=y[:30])
    fig = swarm_plot.get_figure()
    uuid = uuid4()
    date = datetime.now().strftime('%d-%m-%Y')
    plot_name = f"plot {uuid}-{date}.png"
    fig.savefig(f'static/uploads/{plot_name}')
    return plot_name