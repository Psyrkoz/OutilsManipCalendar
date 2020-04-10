from connexion import GoogleConnexion
import logging


if(__name__ == "__main__"):
    logging.basicConfig(filename = "log", filemode = 'a', format= "%(asctime)s - %(levelname)s - %(message)s", level = logging.DEBUG)
    logging.info("Demarrage de l'application")
    gc = GoogleConnexion()