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

        # Cargamos las variables de los archivos
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)).replace("""\\""", "/") + "/utils/modelo.pickle"), 'rb') as archivo_pickle:
            self.palabras, self.tags, self.entrenamiento, self.salida, self.datos = pickle.load(archivo_pickle)

        # Se vuelve a crear la red neuronal exactamente igual al entrenamiento
        tensorflow.compat.v1.reset_default_graph()
        red = tflearn.input_data(shape=[None, len(self.entrenamiento[0])])
        red = tflearn.fully_connected(red, 10)
        red = tflearn.fully_connected(red, 10)
        red = tflearn.fully_connected(red, len(self.salida[0]), activation="softmax")
        red = tflearn.regression(red)
        self.modelo = tflearn.DNN(red)
        
        # En vez de entrenar el modelo, solo se carga del archivo
        self.modelo.load(os.path.join(os.path.dirname(os.path.abspath(__file__)).replace("""\\""", "/") + "/utils/modelo.tflearn"))

    def getResponse(self, entrada):
        # Se crea una cubeta con solo ceros del tamaño del total de palabras
        cubeta = [0 for _ in range(len(self.palabras))]     
        # Permite separar la entrada del usuario en frases significativas y con signos de interrogación
        entradaProcesada = nltk.word_tokenize(entrada)     
        # Eliminamos letras que no son relevantes para el modelo
        entradaProcesada = [self.stemmer.stem(palabra.lower()) for palabra in entradaProcesada]
       
        # Recorremos todas las palabras de la oración procesada de entrada
        for palabraIndividual in entradaProcesada:
            # Recorremos todas las palabras de nuestro conjunto de palabras totales
            for i, palabra in enumerate(self.palabras):
                # Actualizamos en la cubeta las palabras de entrada que coinciden con la palabras totales
                if palabra == palabraIndividual:
                    cubeta[i] = 1

        # Mediante el modelo obtenemos la probabilidad de que la frase pertenezca al i-esimo tag 
        resultados = self.modelo.predict([numpy.array(cubeta)])
        # Obtenemos el indice con el tag de mayor probabilidad
        resultadosIndices = numpy.argmax(resultados)
        # Obtenemos la probabilidad del tag con la mayor
        probabilidad = resultados[0][resultadosIndices] * 100
        # Si dicha probabilidad es menos de 50% entonces decimos que no entendimos el mensaje 
        if probabilidad < 50:
            return [probabilidad, "Lo siento no pude entender lo que dijiste, podrias escribirlo de otra manera por favor :)"]
        
        # Obtenemos el nombre del tag con mas probabilidad de ser
        tag = self.tags[resultadosIndices]
        # Recorremos todos los tags para buscar el correspondiente y guardamos las posibles respuestas 
        for tagAux in self.datos['contenido']:
            if tagAux['tag'] == tag:
                respuesta = tagAux["respuestas"]

        # El bot contesta una respuesta aleatoria de todas las posibles respuestas
        response = random.choice(respuesta) 
        return [probabilidad, response]
