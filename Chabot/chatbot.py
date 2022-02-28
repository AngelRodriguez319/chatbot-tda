import pickle
import os
import tensorflow
import tflearn
import random
import numpy
import nltk
nltk.download('punkt')
from nltk.stem.lancaster import LancasterStemmer

class ChatBot():

    def __init__(self):
        self.stemmer = LancasterStemmer()
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)).replace("""\\""", "/") + "/utils/modelo.pickle"), 'rb') as archivo_pickle:
            self.palabras, self.tags, self.entrenamiento, self.salida, self.datos = pickle.load(archivo_pickle)

        tensorflow.compat.v1.reset_default_graph()
        red = tflearn.input_data(shape=[None, len(self.entrenamiento[0])])
        red = tflearn.fully_connected(red, 10)
        red = tflearn.fully_connected(red, 10)
        red = tflearn.fully_connected(red, len(self.salida[0]), activation="softmax")
        red = tflearn.regression(red)
        self.modelo = tflearn.DNN(red)
        self.modelo.load(os.path.join(os.path.dirname(os.path.abspath(__file__)).replace("""\\""", "/") + "/utils/modelo.tflearn"))

    def getResponse(self, entrada):
        cubeta = [0 for _ in range(len(self.palabras))]     
        entradaProcesada = nltk.word_tokenize(entrada)     
        entradaProcesada = [self.stemmer.stem(palabra.lower()) for palabra in entradaProcesada]
        for palabraIndividual in entradaProcesada:
            for i, palabra in enumerate(self.palabras):
                if palabra == palabraIndividual:
                    cubeta[i] = 1
        resultados = self.modelo.predict([numpy.array(cubeta)])
        resultadosIndices = numpy.argmax(resultados)
        tag = self.tags[resultadosIndices]
        for tagAux in self.datos['contenido']:
            if tagAux['tag'] == tag:
                respuesta = tagAux["respuestas"]
        
        response = random.choice(respuesta) 
        return response
