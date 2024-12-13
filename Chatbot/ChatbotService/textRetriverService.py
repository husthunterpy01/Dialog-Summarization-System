import os
import fitz
import pdfplumber
from Chatbot.ChatbotService.vectordbHandlingService import save_embeddings_to_db
from Chatbot.utils.embedding_utils import get_embedding, validate_and_truncate_text
def get_file_name(file_path) -> str:
    file_name_with_extension = os.path.basename(file_path)
    file_name, _ = os.path.splitext(file_name_with_extension)
    return file_name


def extract_text_from_pdf(file_path) -> str:
    if os.path.exists(file_path):
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text


def extract_table_from_pdf(file_path) -> list:
    if os.path.exists(file_path):
        with pdfplumber.open(file_path) as pdf:
            tables = []
            for page in pdf.pages:
                table = page.extract_tables()
                if table:
                    tables.append(table)
    return tables


def convert_text_to_chunk(text, chunk_size: int = 500, chunk_overlap: int = 200):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if len(chunk.strip()) > 0:
            chunks.append(chunk)
        start = end - chunk_overlap
    return chunks

def chunk_table_data(tables, chunk_size: int = 500, chunk_overlap: int = 200):
    table_chunks = []
    for table in tables:
        table_text = "\n".join([" ".join(map(str, row)) for row in table])
        table_chunks.extend(convert_text_to_chunk(table_text, chunk_size, chunk_overlap))
    return table_chunks


def process_pdf(file_path):
    text_extracted = extract_text_from_pdf(file_path)
    text_chunks = convert_text_to_chunk(text_extracted, chunk_size=500, chunk_overlap=50)

    text_chunks = [validate_and_truncate_text(chunk) for chunk in text_chunks]

    tables = extract_table_from_pdf(file_path)
    table_chunks = chunk_table_data(tables)

    documents = []
    text_embedding = get_embedding(text_chunks)
    for i, (chunk, embedding) in enumerate(zip(text_chunks, text_embedding)):
        doc = {
            'chunk_id': i,
            'content': chunk,
            'embedding': embedding.tolist(),
            'file_name': get_file_name(file_path),
            'source': 'document'
        }
        documents.append(doc)

    table_embedding = get_embedding(table_chunks)
    for i, (chunk, embedding) in enumerate(zip(table_chunks, table_embedding)):
        doc = {
            'chunk_id': i,
            'content': chunk,
            'embedding': embedding.tolist(),
            'file_name': get_file_name(file_path),
            'source': 'table'
        }
        documents.append(doc)

    save_embeddings_to_db(documents)
    return documents
