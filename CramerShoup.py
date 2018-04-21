import sys
import random
from random import randrange
import numpy
import binascii
import math
import codecs
#import gmpy
import Hash
import base64
from math import ceil


###################################  CONSTANTES ########################################################################

taille_cle_bits = 50


###################################  Fonctions #########################################################################

#Génération d'un nombre premier
def generer_nombre_premier(taille):

    taille_int= 1 << int(taille-2)  #on fait correspondre la taille en int à la taille en bit
                                    # -2 car par la suite avec le tirage la taille est réaugmentée
    #nombre = 0
    #resultat = False
    #demande = input("Voulez vous un entier non-Friable ? (o/n)")
    friabilite = False


    while friabilite is not True:  #tant que fraibilite = False(c'est a dire que n n'est pas un entier premier non-friable)

        random.seed()  # initialisation du module random pour ne pas obtenir la meme valeur
        nombre = random.randrange(taille_int,taille_int*2)

        resultat =  Miller_rabin_test(nombre, 70)

        if resultat == True:
            nombre_premier_non_friable = nombre*2+1
            friabilite = Miller_rabin_test(nombre_premier_non_friable, 70)  # on regarde si 2*p+1 est premier => il sera donc non-friable

            #if demande == "n":
             #   return nombre

    #print("Entier premier p: ", nombre_premier_non_friable)
    #print("(p-1)/2: ", (nombre_premier_non_friable - 1) / 2)

    return nombre_premier_non_friable



#test de Miller Rabin
def Miller_rabin_test(n, k):

    if n & 1 == 0:  #si n est paire
        return False
    s = 0
    d = n - 1
    while d & 1 == 0:   #tant que d est paire
        d >>= 1 #on divise d par 2
        s += 1  #on incrémente s (nombre de fois que d est composé du multiple 2)
    for i in range(k):  #précision du test de rabin miller
        alea = randrange(2, n - 1)  #nombre aléatoire
        if not test_composition(alea, s, d, n):
            return False
    return True



#vérifie si un nombre est composé ou non
def test_composition(alea, s, d, n):

    x = pow(alea, d, n)  #a^d mod n
    if x == 1:  # peut etre premier
        return True
    for i in range(s-1): # i de 0 à s-1
        if x == n-1:  # peut etre premier
            return True
        d = d*2   #on multiplie d par 2
        x = pow(alea, d, n)     #a^(d*2*r) mod n
    if x == n-1:
        return True
    return False



#fonction pour trouver les générateurs &1 et &2
def recherche_generateurs(n):
    # n correspond ici à p-1
    #on sait que p est non friable, donc p-1 = 2*(p-1)/2 avec (p-1)/2 premier

    #on a donc deux diviseurs premiers possibles
    liste_diviseurs = [2,int(n/2)]
    liste_gen = [0]

    while 1:
        test = 0
        a = randrange(2,n)  # on choisit a aléatoirement

        if False in [a != i for i in liste_gen]:    # ici on vérifie que le a n'a pas déjà été sélectionné (car on veut deux générateurs distincts)
            pass
        else:
            for i in liste_diviseurs:

                # pour que a soit générateur : a^i mod (n+1) != 1
                if pow(a, i, n + 1) != 1:
                    test += 1

            if test == len(liste_diviseurs) and len(liste_gen) < 3:
                liste_gen.append(a)
            elif len(liste_gen) >= 3:
                break

    # Ci dessous en commentaire, on peut générer tous les éléments de l'ensemble Zp pour vérifier
    # que alpha 1 et alpha2 sont bien des générateurs

    #liste_test = [pow(liste_gen[1], i, n + 1) for i in range(1, n + 1)]
    #print("Generat 1:", sorted(liste_test))

    #liste_test = [pow(liste_gen[2], i, n + 1) for i in range(1, n + 1)]
    #print("Generat 2:", sorted(liste_test))

    return liste_gen[1],liste_gen[2]




#fonction pour tirer aléatoirement x éléments différents sur Zp
def tirage_aleatoire(x,p):
    liste_nbr = []

    while 1:

        a = randrange(2, p-1)  # on choisit a aléatoirement
        #a = randrange(100,1000) # on choisit dans cet intervalle juste pour simplifier et diminuer le tps de calcul, sinon trop long !!

        if False in [a != i for i in liste_nbr]:  # ici on vérifie que le a n'a pas déjà été sélectionné (car on veut x valeurs distincts)
            pass
        elif len(liste_nbr) >= x:
            break
        else :
            liste_nbr.append(a)

    return liste_nbr



#fonction qui génère les clés
def generation_des_cles(t):

    print("Taille de la clé:",t,"bits")
    print("Recherche d'un entier premier non-friable ...")
    nombre_premier = generer_nombre_premier(t)
    print("Recherche de deux générateurs ...")
    list_gen = recherche_generateurs(numpy.long(nombre_premier - 1))
    print("Tirage de 5 valeurs aléatoires ...")
    list_alea = tirage_aleatoire(5, nombre_premier)

    #Calcul de X, Y et W
    print("Calcul de X, Y et W ...")
    x = numpy.long(((pow(list_gen[0],list_alea[0],nombre_premier)) *  (pow(list_gen[1],list_alea[1],nombre_premier))) % nombre_premier)
    y = numpy.long(((pow(list_gen[0], list_alea[2], nombre_premier)) * (pow(list_gen[1], list_alea[3], nombre_premier))) % nombre_premier)
    w = numpy.long(pow(list_gen[0],list_alea[4],nombre_premier))

    # écriture de la clé publique dans un fichier
    fichier_cle_publique = open("Clé_Publique.txt", "w", encoding='utf-8')
    enc = str(nombre_premier)+'\n'+str(list_gen[0])+'\n'+str(list_gen[1])+'\n'+str(x)+'\n'+str(y)+'\n'+str(w)+'\n'+str(t)   #on écrit la taille en bit dans la clé publique
    fichier_cle_publique.write(enc)
    fichier_cle_publique.close()

    # écriture de la clé privée dans un fichier
    fichier_cle_publique = open("Clé_Privée.txt", "w", encoding='utf-8')
    fichier_cle_publique.write(str(list_alea[0])+'\n'+str(list_alea[1])+'\n'+str(list_alea[2])+'\n'+str(list_alea[3])+'\n'+str(list_alea[4]))
    fichier_cle_publique.close()

    # retourne (Cle publique, Cle privée)
    return (nombre_premier,list_gen[0],list_gen[1],x,y,w),(list_alea[0],list_alea[1],list_alea[2],list_alea[3],list_alea[4])



#fonction de cryptage
def chiffrement(message,ClePub):

    print("Chiffrement en cours ...")
    taille = int(ClePub[6])  #on récupère la taille en bits de la clé (cette taille est publique et contenue dans la clé publique)
    #on découpe le message en blocs de taille égale à la clé
    blocs = decoupage_message(message,taille)

    list_crypt = ""

    for int_msg in blocs:
        b = tirage_aleatoire(1,int(ClePub[0]))[0]

        # Calcul de B1, B2, c, Beta, v
        B1 = pow(int(ClePub[1]),b,int(ClePub[0]))
        B2 = pow(int(ClePub[2]),b,int(ClePub[0]))

        c = (pow(int(ClePub[5]), b, int(ClePub[0])) * int_msg) % int(ClePub[0])


        Beta = Hash.hashage(str(B1)+str(B2)+str(c)) # Hash qui prend la concaténation de B1, B2, c
        #print("Beta:",Beta)

        v = ((pow(int(ClePub[3]),b,int(ClePub[0]))) * (pow(int(ClePub[4]),(b*int(Beta)),int(ClePub[0])))) % int(ClePub[0])

        #print("emis:",B1,B2,c,v)       # affiche les valeurs mathématiques émises

        list_crypt += str(hex(B1)[2:])+'\n'+ str(hex(B2)[2:])+'\n'+ str(hex(c)[2:])+'\n'+ str(hex(v)[2:])+'\n'  # contient le chiffré de tous les blocs


    # écriture du message chiffré dans un fichier
    fichier_cle_publique = open("Message_chiffré.txt", "w", encoding='utf-8')
    fichier_cle_publique.write(list_crypt)
    fichier_cle_publique.close()

    return list_crypt



#calcul du pgcd et coef bezout
def pgcd(a, b):

    if a == 0:
        return (b, 0, 1)    # pgcd=b (donc 1 car a et b copremiers normalement), u=0, v=1
    var_pgcd, u, v = pgcd(b % a, a)    # a <- b-a*q+r et b <- a

    return (var_pgcd, v - (b//a) * u, u)  # renvoie les coef de bezout correspondants pgcd = a*u+b*v



#fonction qui permet de découper le message en bloc pour le ramener dans l'espace Zp
def decoupage_message(m,t):

    message_bits = to_bits(m)
    compteur = 0    # pour savoir combien de 0 sont ajoutés à la fin
    while len(message_bits)% (t-1) != 0:
        message_bits += '0'                # on rajoute t-1 bits à 0 à la fin
        compteur += 1

    taille_en_bits = len(message_bits)

    blocs = [compteur]      # en transmet le compteur dans le message crypté, il servira pour le décryptage

    for decalage in range(0,taille_en_bits,t-1):    # par sécurité on découpe en bloc légèrement inférieurs à la taille de la clé
                                                    # pour être sûr que le Integer du bloc du message ne soit pas plus grand que P

         # on convertit les bits en Integer
        blocs.append(int(message_bits[decalage:decalage + (t - 1)], 2))

    #print("Liste clair avant chiffrement",blocs)   #affiche la valeur mathématique des éléments avant le chiffrement
    return blocs



#fonction qui réassemble le message après déchiffrement de chaque bloc
def assembler_message(list_clair,taille_cle):

    text = ""
    compteur = list_clair[0]

    for int_clair in list_clair[1:-1]:

        text += bin(int_clair)[2:].zfill(taille_cle-1)

    # pour le dernier élément on retire le nombre de 0, indiqués par le compteur dans la fonction decoupage_message()
    last = bin(list_clair[-1])[2:].zfill(taille_cle-1)

    if compteur != 0:       # si il n'y a pas eu de 0 ajouté alors le compteur est nul
        last = last [:-compteur]

    text += last

    return  from_bits(text)



#calcul de l'inverse
def inverse(a, m):
    var_pgcd, u, v = pgcd(a, m)
    if var_pgcd != 1:  #si le pgcd est différent de 1 pas d'inverse (ça ne peut pas arriver car m est premier)
        return 0
    return u % m



#fonction de décryptage
def dechiffrement(list_crypt,paire_de_cles):

    print("Déchiffrement en cours ...")
    ClePublique = paire_de_cles[0]
    ClePrivee = paire_de_cles[1]
    taille_cle = int(ClePublique[6])    # on récupère la taille en bits de la clé
    list_clair = []
    i = 0

    for j in range(0,int(len(list_crypt)/4)):

        B1_recu = int(list_crypt[i],16)
        B2_recu = int(list_crypt[i+1],16)
        c_recu = int(list_crypt[i+2],16)
        v_recu = int(list_crypt[i+3],16)
        i += 4
        #print("recu",B1_recu,B2_recu,c_recu,v_recu)    #valeurs mathématiques reçues
        #v_recu = 9

        #Vérification
        Beta_2 = Hash.hashage(str(B1_recu)+str(B2_recu)+str(c_recu))

        test = (pow(B1_recu,int(ClePrivee[0]),int(ClePublique[0]))*pow(B2_recu,int(ClePrivee[1]),int(ClePublique[0]))
                *(pow(pow(B1_recu,int(ClePrivee[2]),int(ClePublique[0]))*pow(B2_recu,int(ClePrivee[3]),int(ClePublique[0])),Beta_2,int(ClePublique[0])))) % int(ClePublique[0])

        #print("v:",v_recu,"test:",test)
        if test != v_recu:
            return "Message non valide car hashs différents !"


        inverser = inverse(pow(B1_recu,int(ClePrivee[4]),int(ClePublique[0])),int(ClePublique[0]))
        m = (inverser * c_recu) % int(ClePublique[0])
        list_clair.append(m)

    #print("Liste clair",list_clair)  # affiche la valeur mathématique des éléments décryptés
    clair = assembler_message(list_clair,taille_cle)
    return clair



#convertir en bits
to_bits = lambda str: bin(int.from_bytes(str.encode('utf-8'), 'big'))[2:]



#convertir en String
from_bits = lambda bin: int(bin, 2).to_bytes(ceil(len(bin) / 8), 'big').decode('utf-8')




###################################  MAIN ##############################################################################

#if __name__ == '__main__':

def main_CramerShoup():
    print("********* --> Cramer-Shoup <-- *************")

    while 1:

        print("--------------------------------------------------------------------------------------------")
        print("Souhaitez vous:","Générer une nouvelle clé ? (Press 1) ","Chiffrer un message ? (Press 2)",
              "Déchiffrer un message ? (Press 3)","Exit ? (Press 4)", sep='\n')
        choix = input()

        if choix == "1":

            taille_cle_utilisateur = input("Entrer la taille de la clé:")
            paire_de_cles = generation_des_cles(int(taille_cle_utilisateur)) # indiquer la taille en bits
            print("******************************* Clé Publique ********************************************","-> P:", paire_de_cles[0][0], "-> Generateur 1:", paire_de_cles[0][1], "-> Generateur 2:",
               paire_de_cles[0][2], "-> X:", paire_de_cles[0][3],"-> Y:", paire_de_cles[0][4], "-> W:", paire_de_cles[0][5], sep='\n')

            print("******************************* Cle Privée ********************************************","-> x1:",paire_de_cles[1][0],"-> x2:",paire_de_cles[1][1],"-> y1:",paire_de_cles[1][2],"-> y2:",paire_de_cles[1][3]
                , "-> w:", paire_de_cles[1][4], sep='\n')

        elif choix == "2":
            print("La clé de chiffrement est: Clé_Publique.txt","Le message est chiffré dans: Message_chiffré.txt", sep='\n')
            #message = input("Entrer le message à chiffrer: ")
            while 2:
                filename = input("Nom du fichier à chiffrer: ")
                try:
                    file = codecs.open(filename, 'r',encoding='utf-8')
                    message = ""
                    for line in file:
                        message += line
                    break
                except Exception:
                    print("Mauvais fichier")
                    sys.exit(0)

            with codecs.open("Clé_Publique.txt", encoding='utf-8') as doc:
                contenu = doc.readlines()

            chiffrer = chiffrement(message,contenu) # paire de clé [0] = clé publique

           # print("******************************* Chiffrement ********************************************","-> Message chiffré: ",chiffrer ,sep='\n')

        elif choix == "3":
            print("Pour déchiffrer on utilise la paire de clé: Clé_Privée.txt et Clé_Publique.txt. On déchiffre le fichier: Message_chiffré.txt", sep='\n')
            doc = codecs.open("Clé_Publique.txt", encoding='utf-8')
            contenu_1 = doc.readlines()
            doc = codecs.open("Clé_Privée.txt", encoding='utf-8')
            contenu_2 = doc.readlines()
            doc = codecs.open("Message_chiffré.txt", encoding='utf-8')
            chiffrer = doc.readlines()

            paire_de_cles = (contenu_1,contenu_2)
            clair  = dechiffrement(chiffrer, paire_de_cles)   # paire de clé [1] = clé privée

            print("******************************* Déchiffrement ********************************************","-> Message clair: ",clair,sep='\n')

        elif choix == "4":
            break

    print("********* --> Authors: Frédérik BKOUCHE, Victor BOUILLOT, GS15 <-- *************")

########################################################################################################################

# GS15: Frédérik BKOUCHE - Victor BOUILLOT
