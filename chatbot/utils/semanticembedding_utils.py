import numpy as np
import re
from .embedding_utils import get_embedding
from sklearn.metrics.pairwise import cosine_similarity

def _split_sentences(text):
    sentences = re.split(r'(?<=[.?!])\s+', text)
    return sentences


def _combine_sentences(sentences):
    combined_sentences = []
    for i in range(len(sentences)):
        combined_sentence = sentences[i]
        if i > 0:
            combined_sentence = sentences[i - 1] + ' ' + combined_sentence
        if i < len(sentences) - 1:
            combined_sentence += ' ' + sentences[i + 1]
        combined_sentences.append(combined_sentence)
    return combined_sentences


def convert_to_vector(texts):
    try:
        # Replace with your embedding model or API call
        embeddings = get_embedding(texts)
        return np.array(embeddings)
    except Exception as e:
        print("An error occurred:", e)
        return np.array([])


def _calculate_cosine_distances(embeddings):
    distances = []
    for i in range(len(embeddings) - 1):
        similarity = cosine_similarity([embeddings[i]], [embeddings[i + 1]])[0][0]
        distance = 1 - similarity
        distances.append(distance)
    return distances
