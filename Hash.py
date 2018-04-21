import sys
import random
import numpy
import binascii
import math
import codecs

################################### -- CONSTANTES ######################################################################

fonctions = 16*[lambda x, y, z: (x & y)]+ \
            16*[lambda x,y, z: (x & z)]+ \
            16*[lambda x,y,z : (x^y^z)]+ \
            16*[lambda x,y,z : (~x)^(~y)^(~z)]

index = 16*[lambda i:i]+\
        16*[lambda i: (5+i*3)%16]+\
        16*[lambda i: (3*i+4)%16]+\
        16*[lambda i: (2*i+1)%16]

valeurs_initiales=[0x54ef68a1, 0x11eb8c99, 0x21e901db, 0xa9b756ce]


################################### -- FONCTIONS #######################################################################

#Convertir texte en binaire
def text_to_binary (text):
     #return bin(int(binascii.hexlify(text), 16))
     #return str(bin(int(binascii.hexlify(bytes(text,"utf8")), 16))[2:])
     return bin(int(binascii.hexlify(bytes(text, "utf8")), 16))[2:]



#Convertir le hash calculé en hexadécimal
def hash_to_hexa(digest):
    hexabytes = digest.to_bytes(16, byteorder='little')
    return '{:032x}'.format(int.from_bytes(hexabytes, byteorder='big'))

#rotation à gauche
def gauche_rotat (x, nombre):
    x &= 0xffffffff #32 bits
    return ((x<<nombre)|(x>>(32-nombre))) &0xffffffff


#rotation fonction
def rotation(var,w,x,y,z):

    nombre=[1, 3, 7, 8, 10, 2, 9, 20,
            14, 15, 3, 17, 9, 5, 15, 10,
            12, 7, 5, 3, 4, 9, 2, 1,
            13, 5, 3, 10, 18, 7, 13, 11,
            1, 3, 7, 8, 19, 2, 9, 10,
            20, 15, 3, 11, 9, 5, 8, 10,
            12, 7, 5, 18, 4, 9, 2, 1,
            13, 16, 3, 10, 9, 7, 8, 14
            ]

    for i in range(64):
        f = fonctions[i](x, y, z)
        ind = index[i](i)
        variable= int(abs(math.sin(i+1))*5**11)
        rotat= w + f + ind + int.from_bytes(var[4*ind:4*ind+4], byteorder='little')+variable
        nouveau_x= (x+gauche_rotat(rotat,nombre[i])) & 0xffffffff
        w,x,y,z = z,nouveau_x, x, y
    return w,x,y,z


#fonction de hashage
def hashage(contenu):
    message_byte = bytearray(contenu.encode())

    #taille en bits que l'on garde: 56 bits
    taille_en_bits= (len(message_byte)*8)&0xffffffffffffff

    #vecteur d'interruption pour marquer la fin du message
    message_byte.append(0x80)

    #On remplit de 0, pour avoir un message de 56 octets modulo 64
    while len(message_byte)%64 != 56:
        message_byte.append(0)

    #On ajoute 8 octets à la fin (en utilisant la taille du message)
    message_byte+= taille_en_bits.to_bytes(8, byteorder='little')

    valeurs=valeurs_initiales[:]

    for decalage in range(0,len(message_byte),64):
        w,x,y,z=valeurs

        #decoupage tous les 64 octets
        var = message_byte[decalage:decalage+64]

        #on effectue une rotation 64 fois
        w,x,y,z = rotation(var,w,x,y,z)

        for i,val in enumerate([w,x,y,z]):
            valeurs[i] += val
            valeurs[i] &= 0xffffffff


    somme=sum(val<<(32*i) for i,val in enumerate(valeurs))

    return somme



################################## -- MAIN -- ##########################################################################



#if __name__ == '__main__':

def main_hash():
   # message = codecs.open("message.txt", encoding='utf-8')
   # contenu = message.read()

    while 2:
        filename = input("Nom du fichier à chiffrer: ")
        try:
            file = codecs.open(filename, 'r',encoding='utf-8')
            contenu = ""
            for line in file:
                contenu += line
            break
        except Exception:
            print("Mauvais fichier")
            sys.exit(0)

    hash_hexa = hash_to_hexa(hashage(contenu))
    print(contenu,'=',hash_hexa , sep=' ')

########################################################################################################################

# GS15: Frédérik BKOUCHE - Victor BOUILLOT


