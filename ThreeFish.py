import sys
import random
import numpy
import binascii


# constante C
C = "0001101111010001000110111101101010101001111111000001101000100010"

file_round = open("round_key.txt", "w")

# fichier de la clé
def generateKey(keyLength):
    file2 = open("key.txt", "w")
    file2.write("Clé pour Three Fish\n")
    for i in range(0, keyLength):
        file2.write(str(random.randint(0, 1)))
    file2.close()
    return readKey("key.txt")


def readKey(filename):
    fichier = open(filename, "r")

    #print(fichier)

    i = 0
    key = []
    nbBlocsKey = 0

    for line in fichier:
        i += 1
        if i == 2:
            if len(line) % 64 == 0:
                nbBlocsKey = len(line) / 64

            if nbBlocsKey in [4, 8, 16]:
                bit = 0
                for nbBloc in range(0, int(nbBlocsKey)):
                    #print("bit=", bit)
                    key.append(line[bit:(bit + 64)])
                    bit += 64
                    #print(key[len(key) - 1])

            else:
                print("La taille de la clé n'est pas bonne.")
                sys.exit(0)
            del bit
        #print(line)
    fichier.close()
    return key


def xor(bloc1, bloc2):
    result = int(bloc1, 2) ^ int(bloc2, 2)
    return (bin(result)[2:]).zfill(len(bloc1))


def appendlastKey(key):
    #print("Calcul Key:", key)
    xored = key[0]
    for i in range(1, len(key) - 2):
        xored = xor(xored, key[i])
    xored = xor(C, xored)
    key.append(xored)
    return key


def text_to_binary(text):
    text = str(bin(int(binascii.hexlify(bytes(text, "utf8")), 16))[2:])
    while len(text) % 8 != 0:
        text = "0" + text
    return text


def binary_to_text(binary):
    return binascii.unhexlify('%x' % int('0b' + binary, 2)).decode("utf-8")


# mélange de deux mots m1 et m2
def mix(m1, m2):
    m1result = addition64b(m1, m2)
    m2result = xor(m1result, perm_circulaire(m2, 49))

    return m1result, m2result


# inverse de mélange de deux mots m1 et m2
def demix(m1result, m2result):
    m2 = xor(m1result, m2result)
    m2 = perm_circulaire(m2, 15)
    m1 = soustraction64b(m1result, m2)
    return m1, m2


# addition modulaire de deux nombres binaires mod 2^64
def addition64b(a, b):
    return (bin(numpy.add(int(a, 2), int(b, 2), dtype=numpy.uint64)))[2:].zfill(64)


# soustraction modulaire de deux nombres binaires mod 2^64
def soustraction64b(a, b):
    return (bin(numpy.subtract(int(a, 2), int(b, 2), dtype=numpy.uint64)))[2:].zfill(64)


# permutation circulaire vers la gauche d'un string ou d'une liste (nbPerm = nombre de permutations)
def perm_circulaire(bloc, nbPerm):
    bloc = bloc[nbPerm:] + bloc[:nbPerm]

    return bloc


# inverse les éléments d'une liste
def permutation(liste_blocs):
    liste_blocs.reverse()
    return liste_blocs


# fonction qui génére toutes les clés pour chaque tournée
def gen_round_key(key):
    tweak0 = key[0]
    tweak1 = key[1]

    N = len(key) - 1
    round_key = [[0 for x in range(N)] for y in range(20)]
    if len(key) in [5, 9, 17]:
        print("la taille de la clé est bonne, N=", N)
    else:
        print("la clé n'a pas la bonne taille: " + str(len(key)))
        sys.exit(0)

    # On crée une liste pour les tweaks et t2= xor(t0 et t1)
    tweaks = [tweak0, tweak1, xor(tweak0, tweak1)]
    # On crée une clé pour chaque tournée de l'algorithme
    for round in range(0, 20):
        for num_bloc in range(0, N):
            # mod est le numéro de clé oiginale pour la tournée: round + num_bloc mod N + 1
            mod = num_bloc + round
            mod = (mod % (N + 1))

            # Pour les blocs [0,N-4]: k(i)=Key[round + num_bloc mod N + 1]
            if (num_bloc <= (N - 4)):
                #print(key[mod])
                round_key[round][num_bloc] = key[mod]

            # Pour les blocs [N-3]: k(i)=Key[round + num_bloc mod N + 1] + t[i mod 3]
            if (num_bloc == (N - 3)):
                mod_tweak = (round % 3)
                round_key[round][num_bloc] = addition64b(key[mod], tweaks[mod_tweak])
                #print("N-3=" + round_key[round][num_bloc])

            # Pour les blocs [N-2]: k(i)=Key[round + num_bloc mod N + 1] + t[ (i+1) mod 3]
            if (num_bloc == (N - 2)):
                mod_tweak = ((round + 1) % 3)
                round_key[round][num_bloc] = addition64b(key[mod], tweaks[mod_tweak])
                #print("N-2=" + round_key[round][num_bloc])

            # Pour les blocs [N-1]: k(i)=Key[round + num_bloc mod N + 1] + i
            if (num_bloc == (N - 1)):
                mod_tweak = (round % 3)
                round_key[round][num_bloc] = addition64b(key[mod], str(bin(round)))
                #print(str(bin(round)))
                #print(key[mod])
                #print("N-1=" + round_key[round][num_bloc])
        file_round.write('\n' + str(round_key[round]))

    return round_key


# prend un string, le convertit en binaire et le sépare en blocs de 64 bits
def message_to_bloc(message):
    if len(message.replace('0', '').replace('1', '')) > 1:
        binary = text_to_binary(message)
    else:
        binary = message
    message = []
    while len(binary) >= 64:
        message.append(binary[0:64])
        binary = binary[64:]
    if len(binary) > 1:
        n = 64 - len(binary)
        n = "".zfill(n)
        message.append(binary + n)
    #print(message)
    return message


# prend une liste de blocs de 64 bits et le convertit en string (message)
def blocs_to_message(blocs, bool):
    message = ""
    for bloc in blocs:
        message += bloc

    # on supprime les derniers 0 si le booléen vaut 1 (déchiffrement)
    if bool == 1:
        while message[-8:] == "00000000":
            message = message[:-8]
    return message


# fonction qui remplit de 0 les blocs vides
def fill_message(message, N):
    while len(message) < N:
        message.append("".zfill(64))
    #print(message)
    return message


def encrypt(key, message, N):
    message = message_to_bloc(message)
    fill_message(message, N)
    key = appendlastKey(key)
    round_key = gen_round_key(key)

    for round in range(0, 19):

        for numbloc in range(0, N):
            # XOR de la subkey et du message
            message[numbloc] = xor(round_key[round][numbloc], message[numbloc])

        # pour chaque round, on applique 4 fois une opération de mixage et une permutation
        for nummix in range(0, 4):
            for numbloc in range(0, N):
                if (numbloc % 2 == 0):
                    message[numbloc], message[numbloc + 1] = mix(message[numbloc], message[numbloc + 1])

            # permutation simple
            permutation(message)


    # A la fin du dernier round, on xor avec le dernier élément de la clé
    for numbloc in range(0, N):
        # XOR de la subkey et du message
        message[numbloc] = xor(round_key[19][numbloc], message[numbloc])
        # print(len(message[numbloc]))
    print("Le chiffrement ThreeFish a été réalisé avec succès")

    #file_cipher = open("cipher.txt", "w")
    #print(blocs_to_message(message, 0))

    #file_cipher.write(blocs_to_message(message, 0))
    return (blocs_to_message(message, 0))


def decrypt(key, message, N):

    message = message_to_bloc(message)
    key = appendlastKey(key)
    round_key = gen_round_key(key)
    for round in range(0, 19):

        for numbloc in range(0, N):
            message[numbloc] = xor(round_key[len(round_key) - 1 - round][numbloc], message[numbloc])

        # pour chaque round, on applique 4 fois une opération de mixage et une permutation
        for nummix in range(0, 4):
            # permutation simple
            permutation(message)

            for numbloc in range(0, N):
                if (numbloc % 2 == 0):
                    message[numbloc], message[numbloc + 1] = demix(message[numbloc], message[numbloc + 1])

    # A la fin du dernier round, on xor avec le dernier élément de la clé
    for numbloc in range(0, N):
        # XOR de la subkey et du message
        message[numbloc] = xor(round_key[0][numbloc], message[numbloc])

    print("Le déchiffrement ThreeFish a été réalisé avec succès")

    file_decipher = open("decipher.txt", "w")
    print(blocs_to_message(message, 1))

    file_decipher.write(blocs_to_message(message, 1))
    return (blocs_to_message(message, 1))

"""
a = xor(key[len(key) - 1], key[len(key) - 2])
print(a)
# key = appendlastKey(key)
print("Kn+1=", key[len(key) - 1])

print(perm_circulaire(key[0], 49))
print("addition: " + key[0])
print("addition: " + key[0])
print("addition: " + addition64b(key[0], key[0]))
print("soustrac: " + soustraction64b(key[0], key[0]))
print("soustrac: " + soustraction64b(addition64b(key[0], key[0]), key[0]))

# print("long: " +str(len(blocs_to_message(message_to_bloc("Bonjour Guillaume"),1))))
# print("long: " +blocs_to_message(message_to_bloc("Bonjour Guillaume"),1))

text_to_binary("a")

a = perm_circulaire(key[0], 49)
perm_circulaire(a, 15)

key1 = key
test = encrypt(key,
               "Bonjour Guillaume, je vais etre en retard demain, je ne viendrais pas à l'école comme tous les matins",
               8)
key = key[:-1]

print(binary_to_text(decrypt(key, test, 8)))
print(text_to_binary(
    "0B1o2n45jour Guillaume, je vais etre en retard demain, je ne viendrais pas à l'école comme tous les matins"))

"""