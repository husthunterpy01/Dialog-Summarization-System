import os
import fitz
import pdfplumber
import shutil
import numpy as np
from chatbot.chatbotService.vectordbHandlingService import save_embeddings_to_db
from chatbot.utils.embedding_utils import get_embedding, validate_and_truncate_text
from chatbot.utils.semanticEmbedding_utils import _split_sentences, _combine_sentences, convert_to_vector, _calculate_cosine_distances

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


def remove_footer_box_from_pdf(file_path, footer_height=80, box_padding=10):
    temp_file = file_path + "_temp.pdf"  # Temporary file path

    # Open the input PDF
    pdf_document = fitz.open(file_path)

    # Check if the PDF is encrypted
    if pdf_document.is_encrypted:
        try:
            pdf_document.authenticate("")  # Try with an empty password
        except:
            print("Error: PDF is encrypted and cannot be processed without a password.")
            return

    for page_num in range(len(pdf_document)):
        page = pdf_document[page_num]

        # Get page dimensions
        rect = page.rect  # Full page rectangle
        footer_rect = fitz.Rect(
            rect.x0 + box_padding,  # Left edge
            rect.height - footer_height,  # Top edge of footer
            rect.width - box_padding,  # Right edge
            rect.height  # Bottom edge of page
        )

        # Redact (remove) text in the footer rectangle
        page.add_redact_annot(footer_rect, fill=(1, 1, 1))  # White rectangle
        page.apply_redactions()

    # Save changes to a temporary file
    pdf_document.save(temp_file, encryption=0)  # Remove encryption
    pdf_document.close()

    # Replace the original file with the modified temporary file
    shutil.move(temp_file, file_path)


def chunk_text(text):
    # Step 1: Split text into sentences
    single_sentences_list = _split_sentences(text)
    if not single_sentences_list:  # Handle empty input text
        print("Error: No sentences found in the input text.")
        return []

    # Step 2: Combine sentences for context
    combined_sentences = _combine_sentences(single_sentences_list)

    # Step 3: Generate embeddings
    embeddings = convert_to_vector(combined_sentences)
    if embeddings.size == 0:  # Handle empty embeddings
        print("Error: Failed to generate embeddings.")
        return []

    # Step 4: Calculate cosine distances
    distances = _calculate_cosine_distances(embeddings)
    if not distances:  # Handle empty distances
        print("Error: No distances calculated.")
        return []

    # Step 5: Determine breakpoints
    breakpoint_percentile_threshold = 80
    breakpoint_distance_threshold = np.percentile(distances, breakpoint_percentile_threshold)

    indices_above_thresh = [i for i, distance in enumerate(distances) if distance > breakpoint_distance_threshold]

    # Step 6: Create chunks based on breakpoints
    chunks = []
    start_index = 0

    for index in indices_above_thresh:
        chunk = ' '.join(single_sentences_list[start_index:index + 1])
        chunks.append(chunk)
        start_index = index + 1

    # Add the last chunk if any sentences remain
    if start_index < len(single_sentences_list):
        chunk = ' '.join(single_sentences_list[start_index:])
        chunks.append(chunk)

    return chunks

def process_pdf(file):
    remove_footer_box_from_pdf(file)

    # Extract text from PDF
    text_extracted = extract_text_from_pdf(file)

    # Perform advanced semantic chunking on the extracted text
    text_chunks = chunk_text(text_extracted)

    # Validate and truncate each chunk
    text_chunks = [validate_and_truncate_text(chunk) for chunk in text_chunks]

    # Extract and chunk tables
    tables = extract_table_from_pdf(file)
    table_chunks = chunk_text("\n".join([" ".join(map(str, row)) for table in tables for row in table]))

    documents = []
    text_embedding = get_embedding(text_chunks)
    for i, (chunk, embedding) in enumerate(zip(text_chunks, text_embedding)):
        doc = {
            'chunk_id': i,
            'content': chunk,
            'embedding': embedding.tolist(),
            'file_name': get_file_name(file),
            'source': 'document'
        }
        documents.append(doc)

    table_embedding = get_embedding(table_chunks)
    for i, (chunk, embedding) in enumerate(zip(table_chunks, table_embedding)):
        doc = {
            'chunk_id': i,
            'content': chunk,
            'embedding': embedding.tolist(),
            'file_name': get_file_name(file),
            'source': 'table'
        }
        documents.append(doc)

    save_embeddings_to_db(documents)
    return documents
