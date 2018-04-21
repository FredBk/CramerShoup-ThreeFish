import ThreeFish as threefish
import sys
import CramerShoup
import Hash
import codecs



Init_V="100110001010100001101010110101010101011110111011001110111011110000010101010111010110101111101100010101110101010100011100011011101110100101010101110100011110110010101010001110101110101"

def encryptThreeFish():
    print("\n---------------------------------------------------------------------\nChiffrement Three Fish")
    print("Veuillez choisir la taille des blocs pour le chiffrement:")
    print("256 / 512 / 1024 bits")

    blocksize = input()
    while (blocksize not in ['256', '512', '1024']):
        print("Mauvaise entrée")
        print("Veuillez entrer la taille des blocs (256 / 512 / 1024 bits)")
        blocksize = input()

    # N est le nombre de mots utilisés
    N = int(int(blocksize) / 64)
    print("\nTaille des blocs:", blocksize, " Nombre de mots:", N)
    print("\n---------------------------------------------------------------------")

    # *************************************************************************************************************************
    # Clé ThreeFish

    print("Voulez-vous générer une nouvelle clé? (y/n)")
    boolKey = input()
    while (boolKey not in ['n', 'o', 'y']):
        print("Mauvaise entrée")
        print("Voulez-vous générer une clé? (y/n)")
        boolKey = input()

    if (boolKey == 'n'):

        print("1) clé par défaut: key.txt")
        print("2) choisir le fichier de la clé")
        chooseKey = input()
        while (chooseKey not in ['1', '2']):
            print("Mauvaise entrée")
            print("1) clé par défaut: key.txt")
            print("2) choisir le fichier de la clé")
            boolKey = input()

        if chooseKey == '1':
            key = threefish.readKey("key.txt")
        else:
            print('ok')
            sys.exit(0)

        if (len(key) != N):
            print("mauvaise taille de clé:", len(key))
            sys.exit(0)
    else:
        print("Génération de la clé pour Three Fish")
        key = threefish.generateKey(int(blocksize))
        print("Clé généré dans le fichier key.txt")

    # *************************************************************************************************************************
    # Choix du message

    print("\n---------------------------------------------------------------------")
    print("Choix du message")

    print("1) Taper le message")
    print("2) choisir le fichier par défaut: message.txt")
    print("3) choisir le fichier")
    chooseMsg = input()
    while (chooseMsg not in ['1', '2', '3', '4']):
        print("1) Taper le message")
        print("2) choisir le fichier par défaut: message.txt")
        print("3) choisir le fichier")
        chooseMsg = input()

    if chooseMsg == '1':
        message = input("Message:")

    if chooseMsg == '2':
        file = codecs.open("message.txt", 'r',encoding='utf-8')
        message = ""
        for line in file:
            message += line

    if chooseMsg == '3':
        filename = input("Path fichier: ")
        try:
            file = codecs.open(filename, 'r',encoding='utf-8')
            message = ""
            for line in file:
                message += line
        except Exception:
            print("Mauvais fichier")
            sys.exit(0)

    if chooseMsg == '4':
        message = "Rémi Cogranne Maitre de l'Univers"

    # *************************************************************************************************************************
    # Choix du chiffrement

    print("Type de chiffrement:")
    print("1) ECB")
    print("2) CBC")
    chooseEnc=input()
    while (chooseEnc not in ['1', '2']):
        print("1) ECB")
        print("2) CBC")
        chooseEnc = input()

    if chooseEnc == '1':
        print("\n\nChiffrement ECB")
        file_cipher = open("cipher.txt", "w")
        cipher = threefish.encrypt(key, message, N)

        file_cipher.write(cipher)
        file_cipher.close()
        key = key[:-1]
        binary = threefish.decrypt(key, cipher, N)
        print(threefish.binary_to_text(binary))


    if chooseEnc == '2':
        print("\n\nChiffrement CCB")
        cipher=Init_V
        file_cipher = open("cipher.txt", "w")
        while len(message) > (N*8):


            text_to_encrypt = message[:N*8]
            text_to_encrypt= threefish.text_to_binary(text_to_encrypt)
            threefish.xor(text_to_encrypt,cipher[:len(text_to_encrypt)])
            cipher = threefish.encrypt(key, text_to_encrypt, N)
            file_cipher.write(cipher + "\n")
            key = threefish.readKey("key.txt")
            message = message[N*8:]

        cipher = threefish.encrypt(key, message, N)
        file_cipher.write(cipher)
        file_cipher.close()


def decryptThreeFish():
    print("\n---------------------------------------------------------------------\nDéchiffrement Three Fish")
    print("1) clé par défaut: key.txt")
    print("2) choisir le fichier de la clé")
    chooseKey = input()
    while (chooseKey not in ['1', '2']):
        print("Mauvaise entrée")
        print("1) clé par défaut: key.txt")
        print("2) choisir le fichier de la clé")
        boolKey = input()

    if chooseKey == '1':
        key = threefish.readKey("key.txt")
    else:
        print('ok')
        sys.exit(0)
    N=len(key)
    print ("\n Taille des blocs: "+  str(N*64) + " bits")

    # *************************************************************************************************************************
    # Choix du message

    print("\n---------------------------------------------------------------------")
    print("Choix du fichier chiffré")

    print("1) choisir le fichier par défaut: cipher.txt")
    print("2) choisir le fichier")
    chooseMsg = input()
    while (chooseMsg not in ['1', '2']):
        print("1) choisir le fichier par défaut: cipher.txt")
        print("2) choisir le fichier")
        chooseMsg = input()

    filename=""
    if chooseMsg == '1':
        filename="cipher.txt"
        file = open(filename, 'r')
        message = ""
        for line in file:
            message += line

    if chooseMsg == '2':
        filename = input("Path fichier: ")
        try:
            file = open(filename, 'r')
            message = ""
            for line in file:
                message += line
        except Exception:
            print("Mauvais fichier")
            sys.exit(0)


            # *************************************************************************************************************************
            # Choix du chiffrement

    print("Type de déchiffrement:")
    print("1) ECB")
    print("2) CBC")
    chooseEnc = input()
    while (chooseEnc not in ['1', '2']):
        print("1) ECB")
        print("2) CBC")
        chooseEnc = input()

    if chooseEnc == '1':
        print("\n\nDéchiffrement ECB")

        binary = threefish.decrypt(key, message, N)
        print(threefish.binary_to_text(binary))
        plain_file = codecs.open("plain_message.txt", "w", encoding='utf-8')
        plain_file.write(threefish.binary_to_text(binary))
        plain_file.close()
    if chooseEnc == '2':
        print("\n\nDéchiffrement CCB")
        cipher = Init_V

        #on lit le fichier ligne par ligne du bas vers le haut pour le CCB (on commence par la fin)
        file_cipher = open(filename, "r")
        line_list = file_cipher.readlines()
        line_list.reverse()

        plain_file = codecs.open("plain_message.txt", "w",encoding='utf-8')
        i = 0
        plain = ""
        for line in line_list:
            i += 1
            xorCBC = line_list[len(line_list) - (1 + i)]
            key = threefish.readKey("key.txt")
            decrypt = threefish.decrypt(key, line, N)
            threefish.xor(xorCBC, decrypt)
            plain = decrypt + plain
            #print("decrypt=", decrypt)
            #plain_file.write(decrypt + "\n")

        print("message: " + threefish.binary_to_text(plain))
        print("Message déchiffré dans plain_message.txt")
        plain_file.write(threefish.binary_to_text(plain))
        plain_file.close()


while 1:
    print('\n')
    print("***************************       MENU PRINCIPAL        ****************************************************************")
    print("Souhaitez vous:", "ThreeFish (Press 1) ", "Cramer-Shoup (Press 2)",
          "Hashage (Press 3)","Exit (press 4)", sep='\n')
    choix = input()

    if choix == "1":
        while 3:
            print("******************* THREE FISH *********************************************************")
            print("Chiffrer ? (press 1)","Déchiffrer ? (press 2)","Quitter ThreeFish ? (press 3)", sep='\n')
            choix_bis = input()
            if choix_bis == "1":
                encryptThreeFish()
            if choix_bis == "2":
                decryptThreeFish()
            if choix_bis == "3":
                break
    if choix == "2":
        CramerShoup.main_CramerShoup()
    if choix == "3":
        print("*****************************    HASHAGE   ******************************************************")
        Hash.main_hash()
    if choix == "4":
        break

print("*****************************************************************************************************************")

