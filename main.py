from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import HTMLResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
import logic 
from datetime import datetime
import json

# --- CONFIGURATION ---
MY_API_KEY = "YOUR_GEMINI_API_KEY_HERE"

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="AppScrip AI Trade Engineer")
app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)

# --- THE STABLE PREMIUM TEMPLATE ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Market Analysis: {sector}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Inter', sans-serif; }}
        .report-content h1 {{ font-size: 2rem; font-weight: 800; color: #1e293b; margin-top: 1.5rem; margin-bottom: 1rem; border-bottom: 3px solid #3b82f6; display: inline-block; }}
        .report-content h2 {{ font-size: 1.5rem; font-weight: 700; color: #334155; margin-top: 2rem; margin-bottom: 0.75rem; display: flex; align-items: center; }}
        .report-content h2::before {{ content: ''; width: 6px; height: 24px; background: #3b82f6; margin-right: 12px; border-radius: 2px; }}
        .report-content p {{ color: #475569; line-height: 1.8; margin-bottom: 1.25rem; font-size: 1.05rem; }}
        .report-content ul {{ margin-bottom: 1.5rem; list-style-type: none; }}
        .report-content li {{ position: relative; padding-left: 1.5rem; margin-bottom: 0.5rem; color: #475569; }}
        .report-content li::before {{ content: '•'; position: absolute; left: 0; color: #3b82f6; font-weight: bold; font-size: 1.2rem; }}
        .report-content strong {{ color: #1e293b; font-weight: 600; }}
    </style>
</head>
<body class="bg-slate-50 min-h-screen">

    <nav class="bg-slate-900 text-white py-5 px-10 shadow-xl flex justify-between items-center">
        <div class="flex items-center space-x-3">
            <div class="w-9 h-9 bg-blue-500 rounded flex items-center justify-center font-bold text-xl text-white">A</div>
            <span class="text-xl font-bold tracking-tight">AppScrip <span class="text-blue-400 font-medium">Market Intelligence</span></span>
        </div>
        <div class="text-sm text-slate-400 font-medium tracking-wide uppercase">AI Engine v1.0</div>
    </nav>

    <main class="max-w-5xl mx-auto py-12 px-6">
        <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-8 mb-8 flex items-center justify-between">
            <div>
                <h3 class="text-slate-400 uppercase tracking-widest text-[10px] font-bold mb-1">Target Sector</h3>
                <h1 class="text-3xl font-black text-slate-900 capitalize tracking-tight">{sector}</h1>
                <p class="text-slate-400 text-sm mt-1">Full Strategic Analysis • {date}</p>
            </div>
            <div class="flex space-x-2">
                <span class="px-4 py-1.5 bg-green-50 text-green-600 border border-green-100 rounded-full text-xs font-bold italic">● Live Search Active</span>
            </div>
        </div>

        <div class="bg-white rounded-xl shadow-2xl border border-slate-200 overflow-hidden">
            <div class="h-1.5 bg-blue-500 w-full"></div>
            <div class="p-10 lg:p-16">
                <div id="formatted-report" class="report-content">
                    Generating analysis...
                </div>
            </div>
        </div>

        <footer class="mt-16 text-center text-slate-400 text-xs pb-12 uppercase tracking-widest">
            &copy; 2026 AppScrip AI Engineer Task | Solution by Sirapu Sravya
        </footer>
    </main>

    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <script>
        // Safely parse the JSON data from Python
        const rawMarkdown = {raw_data_json};
        document.getElementById('formatted-report').innerHTML = marked.parse(rawMarkdown);
    </script>
</body>
</html>
"""

@app.get("/")
def home():
    return {"message": "System Active"}

# FIXED: Removed the double curly braces here
@app.get("/analyze/{sector}")
@limiter.limit("5/minute")
async def analyze_sector(sector: str, request: Request):
    try:
        market_news = logic.search_market_data(sector)
        report_markdown = logic.get_ai_analysis(sector, market_news, MY_API_KEY)
        current_date = datetime.now().strftime("%B %d, %Y")
        
        # Convert to JSON string so it doesn't break the HTML/JS
        safe_json_string = json.dumps(report_markdown)
        
        # Inject values into template
        html_output = HTML_TEMPLATE.format(
            sector=sector, 
            date=current_date,
            raw_data_json=safe_json_string
        )
        
        return HTMLResponse(content=html_output)
    except Exception as e:
        return {"error": "Internal Error", "details": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)