import pandas as pd
import numpy as np
import string, os
import matplotlib.pyplot as plt

import tensorflow
from numpy.random import seed

tensorflow.random.set_seed(1337)
seed(1337)

from tensorflow import keras
from keras_preprocessing.sequence import pad_sequences
from keras.layers import Embedding, LSTM, Dense, Dropout
from keras.preprocessing.text import Tokenizer
from keras.callbacks import EarlyStopping
from keras.models import Sequential
import keras.utils as ku

#Input dalek corpus
dalek_dat = pd.read_csv("Dalek_Speech.csv")
dalek_dat = dalek_dat.loc[:, ~dalek_dat.columns.str.contains('^Unnamed')]
dalek_dat = dalek_dat.loc[:,~dalek_dat.columns.str.contains('^Character$')]

dalek_dat = dalek_dat["Script"].tolist()

#Define cleaning of text, e.g., white space, capital letters, punctuation, etc.
def clean_text(txt):
    txt = "".join(t for t in txt if t not in string.punctuation).lower().strip()
    txt = txt.encode("utf8").decode("ascii",'ignore')
    return txt

#Clean text
dalek_corpus = []
dalek_corpus = [clean_text(line) for line in dalek_dat]

#Generte tokenizer
tokenizer = Tokenizer()
tokenizer.fit_on_texts(dalek_corpus)
word_index = tokenizer.word_index
total_words = len(word_index) + 1

input_sequences =[]

#Crete ngram input sequences for the model
for sentence in dalek_corpus:
    token_list = tokenizer.texts_to_sequences([sentence])[0]
    for i in range(1, len(token_list)):
        n_gram_sequence = token_list[:i+1]
        input_sequences.append(n_gram_sequence)


#Pad sequences to max sequence length
max_sequence_len = max([len(x) for x in input_sequences])
input_sequences = np.array(pad_sequences(input_sequences, 
                                         maxlen=max_sequence_len, 
                                         padding='pre'))

#Generate predictors (The tokens that will be used for prediction) and label (The actual next word in the sequence)
predictors, label = input_sequences[:,:-1],input_sequences[:,-1]
label = tensorflow.keras.utils.to_categorical(label, num_classes=total_words)

#Create model
#We choose one input layer which can take input according to the max sequence length
#We choose to add our LSTM layers (100)
#Our dropout layer is intended to prevent overfitting of the model
def create_model(max_sequence_len, total_words):
    input_len = max_sequence_len - 1
    model = Sequential()
    # ----------Add Input Embedding Layer
    model.add(Embedding(total_words, 10, input_length=input_len))
    # ----------Add Hidden Layer 1 - LSTM Layer
    model.add(LSTM(200))
    model.add(Dropout(0.1))
    # ----------Add Output Layer
    model.add(Dense(total_words, activation='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='adam')
    return model


model = create_model(max_sequence_len, total_words)
model.summary()
history = model.fit(predictors, label, epochs=200, verbose=2)
model.save('./LSTM_Dalek_Model')
#model = keras.models.load_model('./LSTM_Dalek_Model')
#model.summary()

loss = history.history["loss"]

epochs = range(len(loss))

plt.plot(epochs, loss, 'b', label='Training Loss')
plt.title('Training loss')
plt.legend()

plt.show()

def generate(seed_text, next_words):
	for _ in range(next_words):
	    token_list = tokenizer.texts_to_sequences([seed_text])[0]
	    token_list = pad_sequences([token_list], maxlen=max_sequence_len-1, padding='pre')
	    predict_x = model.predict(token_list,verbose=0)
	    predicted = np.argmax(predict_x,axis=1)
	    output_word = ""
	    for word, index in tokenizer.word_index.items():
	        if index == predicted:
	            output_word = word
	            break
	    seed_text += " " + output_word
	return(seed_text)

print(generate("The doctor has", 8).rstrip('\n'))
print(generate("I am a", 8).rstrip('\n'))
print(generate("You are a", 8).rstrip('\n'))
print(generate("I love", 9).rstrip('\n'))
print(generate("I hate", 9).rstrip('\n'))

print(generate("I have come here to", 40).rstrip('\n'))
print(generate("There are more of this", 40).rstrip('\n'))
print(generate("I turned myself into a pickle, Morty", 35).rstrip('\n'))
print(generate("A cow? In the middle of paris?", 35).rstrip('\n'))
print(generate("You would not want to know", 35).rstrip('\n'))


print(generate("Locate the doctor", 90).rstrip('\n'))