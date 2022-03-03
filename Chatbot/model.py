# Natural Language Toolkit
import sys
import pickle
import random
import json
import tensorflow
import tflearn
import numpy
import nltk
# Transformar palabras, quita letras de mas
from nltk.stem.lancaster import LancasterStemmer
stemmer = LancasterStemmer()

# Paquete necesario que en ocasiones no se instala
nltk.download('punkt')

# Se abre el contenido de los patrones reconocibles por el chat
with open('utils/contenido.json', encoding='utf-8') as archivo:
    datos = json.load(archivo)

palabras = []  # Todas las palabras del contenido separadas
tags = []  # Los tags sin repetir
auxX = []  # Lista de listas de palabras que son relevantes agrupadas
auxY = []  # Los Tags repetidos

# Accedemos a cada tag del archivo
for contenido in datos['contenido']:
    # Recorremos todos los patrones dentro de cada tag
    for patrones in contenido['patrones']:
        # Separa la frase de cada patron en palabras significativas y reconoce signos significativos
        auxPalabra = nltk.word_tokenize(patrones)
        # Ponemos solamente todas las palabras separadas
        palabras.extend(auxPalabra)
        # Agregamos la lista al final de nuestra variable como un elemento,
        # aqui van todas las palabras separadas del tag
        auxX.append(auxPalabra)
        # Aqui va el nombre del tag al cual pertenece la frase
        auxY.append(contenido['tag'])

        # Sacamos los tags del archivo sin que se repitan
        if contenido['tag'] not in tags:
            tags.append(contenido['tag'])

# Recupera la parte significativa de todas las palabras en el modelo, eliminando signos
palabras = [stemmer.stem(w.lower()) for w in palabras if w != "?"]
# Ordenamos las palabras y eliminamos las repetirdas con set()
palabras = sorted(list(set(palabras)))
# Ordenamos los tags
tags = sorted(tags)

entrenamiento = []  # Lista con cubetas que no indica la posición de las listas de frases dentro
                    # del arreglo de palabras totales sin repetir
salida = []  # Lista de cubetas que indica a qué tag pertenece la frase que traemos en aunxX

# Creamos un arreglo de solo ceros del tamaño de la cantidad de tags
salidaVacia = [0 for _ in range(len(tags))]

# Recorremos todas las frases del contenido
for x, documento in enumerate(auxX):
    cubeta = []
    # Volvemos a eliminar partes de la oración que no nos sirve
    auxPalabra = [stemmer.stem(w.lower()) for w in documento]
    # Llenamos la cubeta para marcar que palabras han aparecido y cuales no han aparecido
    for w in palabras:
        if w in auxPalabra:
            cubeta.append(1)
        else:
            cubeta.append(0)
    filaSalida = salidaVacia[:]
    filaSalida[tags.index(auxY[x])] = 1
    # Agregamos cada cubeta de cada frase en el entrenamiento
    entrenamiento.append(cubeta)
    # Le asigna a que tag le pertenece cada frase
    salida.append(filaSalida)

# Convertimos las listas en un arreglo de numpy
entrenamiento = numpy.array(entrenamiento)
salida = numpy.array(salida)

# Limpiar datos basura de la red neuronal
tensorflow.compat.v1.reset_default_graph()

# Configuramos el tamaño de la entrada de los datos (Todas las cubetas de entrenamiento )
red = tflearn.input_data(shape=[None, len(entrenamiento[0])])
# Creamos una capa de 10 neuronas totalmente conectadas a los datos
red = tflearn.fully_connected(red, 10)
# Creamos una segunda capa de 10 neuronas totalemente conectadas a la primera capa
red = tflearn.fully_connected(red, 10)
# Por ultimo conectamos las salidas (count tags) de la red
red = tflearn.fully_connected(red, len(salida[0]), activation="softmax")
red = tflearn.regression(red)

# Creamos el modelo pasandole la red neuronal que creamos
modelo = tflearn.DNN(red)
# Entrenamos el modelo con los datos
#   - n_epoch: La cantidades de veces que analizará los datos (mientras mas mejor)
#   - batch_size: El tamaño de lotes que agarrará para aprende el modelo
modelo.fit(entrenamiento, salida, n_epoch=1000, batch_size=10, show_metric=True)
# Se guarda el modelo en un archivo fisico
modelo.save("utils/modelo.tflearn")

# Se guardan todos los datos de entrenamiento en un archivol pickle
with open('utils/modelo.pickle', 'wb') as archivo_pickle_escritura:
    pickle.dump((palabras, tags, entrenamiento, salida, datos), archivo_pickle_escritura)

print("Modelo Actualizado correctamente")
