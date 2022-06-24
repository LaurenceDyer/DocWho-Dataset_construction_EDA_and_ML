import nltk
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag, pos_tag_sents
from nltk.probability import FreqDist
from nltk.sentiment.vader import SentimentIntensityAnalyzer


from pprintpp import pprint
import pandas as pd

pd.set_option('display.max_rows', 1000)
pd.set_option('max_colwidth',80)
pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)

regexp = RegexpTokenizer(r'\w+')
stop = nltk.corpus.stopwords.words("english")

scripts = pd.read_csv("sentimentScript.csv", index_col = 2)

#Limit for testing
#scripts = scripts.loc[1:10000]

#Need to coerce column to a column of lower case strings
scripts["Script"] = scripts["Script"].astype(str).str.lower().str.strip()

#Tokenize script column
scripts['Script'] = scripts['Script'].apply(regexp.tokenize)

#Remove stopwords from scripts
scripts['Script'] = scripts['Script'].apply(lambda words: [word for word in words if word not in stop])

#Remove very short words with 2 or fewer characters
scripts['Script'] = scripts['Script'].apply(lambda x: ' '.join([item for item in x if len(item)>2]))

#We now wish to remove all words which are very infrequent and appear less than two times over the entire corpus
#We create a list of all words and tokenize it
all_words = ' '.join([word for word in scripts['Script']])
all_words = nltk.tokenize.word_tokenize(all_words)

#We check the frequency of each word across the entire text... and remove those with a frequnecy lower than three
freqdist = FreqDist(all_words)
scripts['Script'] = scripts['Script'].apply(lambda x: ''.join([item for item in x if freqdist[x] <= 3]))

#We now lemmatize words to generate their stems
lemmatizer = nltk.stem.WordNetLemmatizer()

def nltk_tag_to_wordnet_tag(nltk_tag):
    if nltk_tag.startswith('J'):
        return wordnet.ADJ
    elif nltk_tag.startswith('V'):
        return wordnet.VERB
    elif nltk_tag.startswith('N'):
        return wordnet.NOUN
    elif nltk_tag.startswith('R'):
        return wordnet.ADV
    else:
        return None

def lemmatize_sentence(line):
    #First we need to POS tag each word as a noun, verb, etc.
    posTags = pos_tag(regexp.tokenize(line))

    #We then need to convert our tags to wordnet format
    wordnet_pos = map(lambda x: (x[0], nltk_tag_to_wordnet_tag(x[1])), posTags)
    lemma_lines = []
    for word, tag in wordnet_pos:
        if tag is None:
            #if there is no available tag, append the token as is
            lemma_lines.append(word)
        else:
            #else use the tag to lemmatize the token
            lemma_lines.append(lemmatizer.lemmatize(word, tag))
    return " ".join(lemma_lines)

scripts['Script_lemm'] = scripts['Script'].apply(lambda x: lemmatize_sentence(x))


#Now we can begin our sentiment analysis
analyzer = SentimentIntensityAnalyzer()
scripts['Polarity'] = scripts['Script_lemm'].apply(lambda x: analyzer.polarity_scores(x))

scripts = pd.concat(
    [scripts.drop(['Unnamed: 0','Polarity'], axis=1), 
     scripts['Polarity'].apply(pd.Series)], axis=1)


print("Writing all sentiments to file.")
scripts.to_csv("scripts_with_Sentiment.csv", sep='\t')
