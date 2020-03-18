import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-a", "--add", type=str, help="Indiquer le nom calendrier a modifier suivi de la commande --file")
parser.add_argument("-e", "--export", type=str, help="Indiquer le nom du calendrier a exporter suivi de la commande --file")
parser.add_argument("-ds", "--dateStart", type=str, help="Jours de depart pour l'exportation (jj/mm/aaaa)")
parser.add_argument("-de", "--dateEnd", type=str, help="Jours de fin pour l'exportation (jj/mm/aaaa)")
parser.add_argument("-f", "--file", type=str, help="Indiquer le nom du fichier a ajouter / exporter")

args = parser.parse_args()

# Dans le cas ou on veut ajouter un fichier .ics
if(args.add):
    # Le prototype de la fonction sera sûrement quelque chose comme: add(nomCalendrier, nomFichierICS)
    if(args.file):
        print("Ajout de " + args.file + " dans le calendrier " + args.add)
    else:
        print("Mauvaise utilisation de la commande... Utiliser --help pour plus d'informations")
elif(args.export):
    if(args.file):
        # Le prototype de la fonction sera sûrement quelque chose comme: export(nomCalendrier, fichierExportation, dateDebut, dateFin)
        if(args.dateStart and args.dateEnd):
            print("Exportation du calendrier " + args.export + " dans le fichier " + args.file + " a partir du " + args.dateStart + " jusqu'au " + args.dateEnd)
        elif(args.dateStart):
            print("Exportation du calendrier " + args.export + " dans le fichier " + args.file + " a partir du " + args.dateStart + " jusqu'a la fin des temps")
        elif(args.dateEnd):
            print("Exportation du calendrier " + args.export + " dans le fichier " + args.file + " a partir du 01/01/1970 jusqu'au " + args.dateEnd)
        else:
            print("Exportation de tout le calendrier " + args.export + " dans le fichier" + args.file)