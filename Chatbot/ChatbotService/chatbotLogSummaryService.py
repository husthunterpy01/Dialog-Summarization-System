from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from dotenv import load_dotenv
import os

load_dotenv()
# Load the fine-tuned model
FINE_TUNE_MODEL = os.getenv("FINE_TUNE_MODEL")
tokenizer = AutoTokenizer.from_pretrained(FINE_TUNE_MODEL)
model = AutoModelForSeq2SeqLM.from_pretrained(FINE_TUNE_MODEL)

def generate_summary(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True)
    summary_ids = model.generate(
        inputs["input_ids"], max_length=100, min_length=25, num_beams=4, early_stopping=True
    )
    return tokenizer.decode(summary_ids[0], skip_special_tokens=True)