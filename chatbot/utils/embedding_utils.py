from sentence_transformers import SentenceTransformer

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def get_embedding(text_list):
    return model.encode(text_list)

def validate_and_truncate_text(text, max_tokens=512):
    encoded_input = model.tokenizer(text, truncation=False, return_tensors="pt")
    input_tokens = len(encoded_input['input_ids'][0])
    if input_tokens > max_tokens:
        truncated_text = model.tokenizer.decode(encoded_input['input_ids'][0][:max_tokens])
        return truncated_text
    return text
