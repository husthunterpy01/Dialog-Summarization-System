from sentence_transformers import SentenceTransformer

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def get_embedding(text_list):
    return model.encode(text_list)
