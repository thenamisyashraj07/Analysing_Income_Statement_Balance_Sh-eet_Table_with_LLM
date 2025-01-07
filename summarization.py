from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline, BitsAndBytesConfig
import torch

def initialize_llm_pipeline(model_name="mistralai/Mistral-7B-Instruct-v0.2"):
    """
    Initializes the Language Model pipeline for text generation.
    
    Args:
        model_name (str): Name of the pre-trained model.
        
    Returns:
        pipeline: Hugging Face transformers pipeline for text generation.
    """
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    # quant_config = BitsAndBytesConfig(
    #     load_in_8bit=True  # Enable 8-bit quantization
    # )
    
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        # quantization_config=quant_config,
        device_map="auto",
    )
    
    llm_pipeline = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        device_map="auto",
        batch_size=1
    )
    return llm_pipeline

def summarize_table(llm_pipeline, table_text):
    """
    Generates a summary for the given table text using the LLM pipeline.
    
    Args:
        llm_pipeline (pipeline): Initialized transformers pipeline.
        table_text (str): Text representation of the table.
        
    Returns:
        str: Generated summary.
    """
    prompt = (
        "Summarize the following table data:\n\n"
        f"{table_text}\n\n"
        "Provide a concise summary of the key points."
    )
    response = llm_pipeline(prompt, max_new_tokens=100, num_return_sequences=1)
    summary = response[0]['generated_text']
    return summary