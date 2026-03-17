import google.generativeai as genai
from duckduckgo_search import DDGS

def search_market_data(sector: str):
    """Searches for news."""
    try:
        with DDGS() as ddgs:
            query = f"Indian {sector} sector market trends 2024"
            results = list(ddgs.text(query, max_results=5))
            if not results:
                return "Analyze using general market knowledge for India 2024-25."
            return "\n".join([r['body'] for r in results])
    except:
        return "Analyze using general market knowledge for India 2024-25."

def get_ai_analysis(sector: str, news_data: str, api_key: str):
    """Finds an available model and generates the report."""
    genai.configure(api_key=api_key)
    
    # --- SMART MODEL SELECTION ---
    # This part looks at your account and finds a model that actually exists
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    
    # We try to find 'gemini-1.5-flash', if not, we take the first available one
    selected_model = 'models/gemini-1.5-flash' 
    if selected_model not in available_models:
        if available_models:
            selected_model = available_models[0]
        else:
            raise Exception("No Gemini models found in this account.")
    
    print(f"Using model: {selected_model}")
    model = genai.GenerativeModel(selected_model)
    
    prompt = f"""
    Write a professional Markdown report on the Indian {sector} sector.
    Context: {news_data}
    
    Include:
    # {sector.upper()} MARKET ANALYSIS
    ## 1. Summary
    ## 2. Trade Opportunities
    ## 3. Risks
    """
    
    response = model.generate_content(prompt)
    return response.text