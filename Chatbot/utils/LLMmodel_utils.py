from llama_cpp import Llama
class LLM:
    def __init__(self, model_path):
        # Load the model using llama_cpp
        self.model = Llama(model_path, n_ctx = 10000)
        # self.model = Llama.from_pretrained(
        #     repo_id="unsloth/Llama-3.2-3B-Instruct-GGUF",
        #     filename="Llama-3.2-3B-Instruct-Q4_K_M.gguf",
        #     n_ctx=10000
        # )

    def generate_response(self, prompt: str) -> str:
        try:
            # Generate a response based on the given prompt
            response = self.model(
                prompt,
                echo=False,
                max_tokens=256,
                temperature=0
            )
            # Get the raw output text
            raw_output = response.get('choices', [{}])[0].get('text', "").strip()
            if not raw_output:
                raw_output = "I'm sorry this knowledge hasn't been updated to me ? Can you ask another question ?"
            # Clean up any performance or additional logs from the raw output
            clean_output = self.clean_output(raw_output)

            return clean_output
        except Exception as e:
            return f"Error: {str(e)}"

    def clean_output(self, text: str) -> str:
        # Remove performance logging details
        lines = text.split("\n")
        cleaned_lines = [line for line in lines if not line.startswith("llama_perf_context_print")]

        # Further clean: Strip extra empty lines if there are any
        return "\n".join(cleaned_lines).strip()