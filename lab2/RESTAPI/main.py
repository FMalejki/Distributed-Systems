from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional
import httpx
import asyncio
from datetime import datetime
import os
from dotenv import load_dotenv
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import random

load_dotenv()

ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY", "demo")
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="Financial Markets Analysis API", version="1.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CommodityType(str):
    OIL = "oil"
    GAS = "gas"

class DefenseStock(str):
    LOCKHEED = "LMT"
    BOEING = "BA"
    RAYTHEON = "RTX"
    NORTHROP = "NOC"
    GENERAL_DYNAMICS = "GD"

class MarketAnalysisRequest(BaseModel):
    commodity: str = Field(..., description="Type of commodity")
    defense_stocks: List[str] = Field(..., description="List of defense stock symbols (1-5)")
    days_back: int = Field(default=7, ge=1, le=30)

    @validator('defense_stocks')
    def validate_stocks(cls, v):
        if not v or len(v) < 1:
            raise ValueError('At least one stock must be selected')
        if len(v) > 5:
            raise ValueError('Maximum 5 stocks allowed')
        if len(v) != len(set(v)):
            raise ValueError('Duplicate stocks not allowed')
        return v

class NewsArticle(BaseModel):
    title: str
    description: Optional[str]
    url: str
    source: str
    publishedAt: str

class PriceData(BaseModel):
    symbol: str
    price: float
    change: float
    change_percent: float
    timestamp: str

class CommodityData(BaseModel):
    commodity: str
    price: float
    unit: str
    change_24h: float
    timestamp: str

class AnalysisResult(BaseModel):
    commodity_data: CommodityData
    defense_stocks_data: List[PriceData]
    correlation_analysis: Dict[str, float]
    market_sentiment: str
    recommendation: str
    iran_news: List[NewsArticle]
    generated_at: str

async def fetch_with_retry(client: httpx.AsyncClient, url: str, max_retries: int = 3) -> Dict:
    """Fetch data with exponential backoff retry"""
    for attempt in range(max_retries):
        try:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            
            if isinstance(data, dict) and ("Note" in data or "Information" in data):
                error_msg = data.get('Note') or data.get('Information', 'Rate limit exceeded')
                print(f"[API Rate Limit] {error_msg}")
                raise ValueError(f"API Rate Limit: {error_msg}")
            
            if isinstance(data, dict) and "Error Message" in data:
                raise ValueError(f"API Error: {data.get('Error Message')}")
            
            return data
            
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"[Failed] {url} after {max_retries} attempts: {str(e)}")
                raise
            
            delay = (2 ** attempt) + random.uniform(0, 1)
            print(f"[Retry {attempt + 1}/{max_retries}] {url} - waiting {delay:.1f}s")
            await asyncio.sleep(delay)
    
    raise Exception("Max retries exceeded")

class FinancialDataClient:
    def __init__(self):
        self.timeout = httpx.Timeout(15.0)

    async def get_commodity_price(self, commodity: str) -> Dict:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                if commodity.lower() == "oil":
                    url = f"https://www.alphavantage.co/query?function=WTI&interval=daily&apikey={ALPHA_VANTAGE_KEY}"
                    try:
                        data = await fetch_with_retry(client, url)
                        if "data" in data and len(data["data"]) > 0:
                            latest = data["data"][0]
                            prev_price = float(data["data"][1]["value"]) if len(data["data"]) > 1 else float(latest["value"])
                            change = float(latest["value"]) - prev_price
                            price = float(latest["value"])
                        else:
                            raise ValueError("No data in response")
                    except Exception as e:
                        print(f"[Warning] Using mock oil data: {str(e)}")
                        price = 78.50
                        change = 2.15
                    return {
                        "commodity": "OIL",
                        "price": price,
                        "unit": "USD/barrel",
                        "change_24h": change,
                        "timestamp": datetime.now().isoformat()
                    }
                elif commodity.lower() == "gas":
                    url = f"https://www.alphavantage.co/query?function=NATURAL_GAS&interval=daily&apikey={ALPHA_VANTAGE_KEY}"
                    try:
                        data = await fetch_with_retry(client, url)
                        if "data" in data and len(data["data"]) > 0:
                            latest = data["data"][0]
                            prev_price = float(data["data"][1]["value"]) if len(data["data"]) > 1 else float(latest["value"])
                            change = float(latest["value"]) - prev_price
                            price = float(latest["value"])
                        else:
                            raise ValueError("No data in response")
                    except Exception as e:
                        print(f"[Warning] Using mock gas data: {str(e)}")
                        price = 3.24
                        change = -0.08
                    return {
                        "commodity": "GAS",
                        "price": price,
                        "unit": "USD/MMBtu",
                        "change_24h": change,
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    raise ValueError(f"Unknown commodity: {commodity}")
            except HTTPException:
                raise
            except Exception as e:
                print(f"[Error] Commodity API failed, using mock data: {str(e)}")
                return {
                    "commodity": "OIL" if commodity.lower() == "oil" else "GAS",
                    "price": 78.50 if commodity.lower() == "oil" else 3.24,
                    "unit": "USD/barrel" if commodity.lower() == "oil" else "USD/MMBtu",
                    "change_24h": 2.15 if commodity.lower() == "oil" else -0.08,
                    "timestamp": datetime.now().isoformat()
                }

    async def get_stock_price(self, symbol: str) -> Dict:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={ALPHA_VANTAGE_KEY}"
                try:
                    data = await fetch_with_retry(client, url)
                    if "Global Quote" in data and data["Global Quote"]:
                        quote = data["Global Quote"]
                        price = float(quote.get("05. price", 0))
                        change = float(quote.get("09. change", 0))
                        change_percent = float(quote.get("10. change percent", "0").replace("%", ""))
                    else:
                        raise ValueError("No Global Quote in response")
                except Exception as e:
                    print(f"[Warning] Using mock data for {symbol}: {str(e)}")
                    stock_prices = {
                        "LMT": {"price": 445.30, "change": 5.20},
                        "BA": {"price": 185.75, "change": -2.40},
                        "RTX": {"price": 95.60, "change": 1.80},
                        "NOC": {"price": 475.20, "change": 3.50},
                        "GD": {"price": 245.80, "change": 2.10}
                    }
                    if symbol not in stock_prices:
                        raise ValueError(f"Unknown stock: {symbol}")
                    stock_data = stock_prices[symbol]
                    price = stock_data["price"]
                    change = stock_data["change"]
                    change_percent = round((change / price) * 100, 2)
                return {
                    "symbol": symbol,
                    "price": price,
                    "change": change,
                    "change_percent": change_percent,
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                raise HTTPException(status_code=503, detail=f"Failed to fetch stock data: {str(e)}")

    async def get_iran_defense_news(self, stock_symbols: List[str]) -> List[Dict]:
        """Fetch news about Iran conflict and defense stocks from NewsAPI"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                if not NEWS_API_KEY:
                    print("[Warning] NEWS_API_KEY not set, returning mock data")
                    return self._get_mock_news()
                
                stock_names = {
                    "LMT": "Lockheed Martin",
                    "BA": "Boeing",
                    "RTX": "Raytheon",
                    "NOC": "Northrop Grumman",
                    "GD": "General Dynamics"
                }
                
                query_parts = ["Iran conflict", "defense"]
                for symbol in stock_symbols[:2]:
                    if symbol in stock_names:
                        query_parts.append(stock_names[symbol])
                
                query = " OR ".join(query_parts)
                url = f"https://newsapi.org/v2/everything?q={query}&sortBy=publishedAt&language=en&pageSize=5&apiKey={NEWS_API_KEY}"
                
                data = await fetch_with_retry(client, url, max_retries=2)
                
                if "articles" not in data:
                    print(f"[Warning] No articles in NewsAPI response: {data}")
                    return self._get_mock_news()
                
                articles = []
                for article in data["articles"][:5]:
                    articles.append({
                        "title": article.get("title", "No title"),
                        "description": article.get("description", ""),
                        "url": article.get("url", "#"),
                        "source": article.get("source", {}).get("name", "Unknown"),
                        "publishedAt": article.get("publishedAt", "")
                    })
                
                return articles if articles else self._get_mock_news()
                
            except Exception as e:
                print(f"[Error] Failed to fetch news: {str(e)}")
                return self._get_mock_news()
    
    def _get_mock_news(self) -> List[Dict]:
        """Return mock news data when API is unavailable"""
        return [
            {
                "title": "Iran-Israel Tensions Rise: Defense Stocks React",
                "description": "Defense contractors see increased activity amid Middle East tensions",
                "url": "#",
                "source": "Mock News",
                "publishedAt": datetime.now().isoformat()
            },
            {
                "title": "US Defense Budget Increases Amid Regional Conflicts",
                "description": "Pentagon announces increased spending on defense systems",
                "url": "#",
                "source": "Mock News",
                "publishedAt": datetime.now().isoformat()
            }
        ]

class MarketAnalyzer:
    def __init__(self):
        self.client = FinancialDataClient()

    async def analyze_markets(self, request: MarketAnalysisRequest) -> AnalysisResult:
        try:
            commodity_data = await self.client.get_commodity_price(request.commodity)
            
            stocks_data = []
            for i, stock in enumerate(request.defense_stocks):
                if i > 0:
                    await asyncio.sleep(1.5)
                try:
                    stock_data = await self.client.get_stock_price(stock)
                    stocks_data.append(stock_data)
                except Exception as e:
                    print(f"[Warning] Failed to fetch {stock}: {str(e)}")
            
            iran_news = await self.client.get_iran_defense_news(request.defense_stocks)

            if not stocks_data:
                raise HTTPException(status_code=503, detail="No stock data available")

            correlations = self._calculate_correlations(commodity_data, stocks_data)
            sentiment = self._determine_sentiment(commodity_data, stocks_data, iran_news)
            recommendation = self._generate_recommendation(commodity_data, stocks_data, correlations, sentiment)

            return AnalysisResult(
                commodity_data=CommodityData(**commodity_data),
                defense_stocks_data=[PriceData(**stock) for stock in stocks_data],
                correlation_analysis=correlations,
                market_sentiment=sentiment,
                recommendation=recommendation,
                iran_news=[NewsArticle(**article) for article in iran_news],
                generated_at=datetime.now().isoformat()
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

    def _calculate_correlations(self, commodity_data: Dict, stocks_data: List[Dict]) -> Dict[str, float]:
        correlations = {}
        commodity_change = commodity_data["change_24h"]
        for stock in stocks_data:
            stock_change = stock["change"]
            correlation = 0.5 if (commodity_change > 0 and stock_change > 0) or \
                                  (commodity_change < 0 and stock_change < 0) else -0.3
            correlations[stock["symbol"]] = round(correlation, 2)
        return correlations

    def _determine_sentiment(self, commodity_data: Dict, stocks_data: List[Dict], iran_news: List[Dict]) -> str:
        """Determine market sentiment based on commodity, stocks, and Iran news"""
        commodity_positive = commodity_data["change_24h"] > 0
        stocks_positive = sum(1 for s in stocks_data if s["change"] > 0) > len(stocks_data)/2
        
        news_score = 0
        for article in iran_news:
            title = (article.get("title") or "").lower()
            desc = (article.get("description") or "").lower()
            text = title + " " + desc
            
            if any(word in text for word in ["conflict", "tension", "war", "attack", "strike"]):
                news_score += 1  # Conflict news = bullish for defense
            if any(word in text for word in ["peace", "deal", "agreement", "ceasefire"]):
                news_score -= 1  # Peace news = bearish for defense

        if news_score > 0 and commodity_positive and stocks_positive:
            return "Strongly Bullish"
        elif (news_score > 0 or commodity_positive) and stocks_positive:
            return "Bullish"
        elif news_score < 0 and not commodity_positive and not stocks_positive:
            return "Strongly Bearish"
        elif news_score < 0 or (not commodity_positive and not stocks_positive):
            return "Bearish"
        else:
            return "Neutral"

    def _generate_recommendation(self, commodity_data: Dict, stocks_data: List[Dict], correlations: Dict, sentiment: str) -> str:
        avg_correlation = sum(correlations.values()) / len(correlations)
        avg_stock_change = sum(s["change_percent"] for s in stocks_data) / len(stocks_data)
        if sentiment in ["Strongly Bullish", "Bullish"] and avg_correlation > 0.3:
            return f"BUY: Strong positive correlation ({avg_correlation:.2f}) between {commodity_data['commodity']} and defense stocks. Average stock change: {avg_stock_change:.2f}%"
        elif sentiment in ["Strongly Bearish", "Bearish"] and avg_correlation < -0.2:
            return f"SELL: Negative market conditions. Average stock change: {avg_stock_change:.2f}%"
        else:
            return f"HOLD: Mixed signals. Correlation: {avg_correlation:.2f}, Average change: {avg_stock_change:.2f}%"

analyzer = MarketAnalyzer()

@app.get("/", response_class=HTMLResponse)
async def root():
    html_content = """<!DOCTYPE html>
<html>
<head>
<title>Financial Markets Analysis</title>
<style>
body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
h1 { color: #2c3e50; }
form { background: #f4f4f4; padding: 20px; border-radius: 5px; }
label { display: block; margin: 10px 0 5px; font-weight: bold; }
input, select { width: 100%; padding: 8px; margin-bottom: 10px; border: 1px solid #ddd; border-radius: 3px; }
button { background: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 3px; cursor: pointer; }
button:hover { background: #2980b9; }
.result { background: #fff; padding: 20px; margin-top: 20px; border: 1px solid #ddd; border-radius: 5px; }
.error { color: #e74c3c; }
.success { color: #27ae60; }
.checkbox-group { margin: 10px 0; }
.checkbox-group label { display: inline; margin-right: 15px; font-weight: normal; }
</style>
</head>
<body>
<h1>Financial Markets Analysis API</h1>
<p>Analyze commodity prices (Oil/Gas) and defense stocks correlations</p>
<form id="analysisForm">
<label>Commodity Type:</label>
<select id="commodity" required>
<option value="oil">Oil (WTI Crude)</option>
<option value="gas">Natural Gas</option>
</select>
<label>Defense Stocks (select 1-5):</label>
<div class="checkbox-group">
<label><input type="checkbox" name="stocks" value="LMT" checked> Lockheed Martin (LMT)</label><br>
<label><input type="checkbox" name="stocks" value="BA"> Boeing (BA)</label><br>
<label><input type="checkbox" name="stocks" value="RTX"> Raytheon (RTX)</label><br>
<label><input type="checkbox" name="stocks" value="NOC"> Northrop Grumman (NOC)</label><br>
<label><input type="checkbox" name="stocks" value="GD"> General Dynamics (GD)</label>
</div>
<label>Analysis Period (days):</label>
<input type="number" id="daysBack" min="1" max="30" value="7" required>
<button type="submit">Analyze Markets</button>
</form>
<div id="result" class="result" style="display:none;"></div>
<script>
document.getElementById('analysisForm').addEventListener('submit', async (e) => {
e.preventDefault();
const commodity = document.getElementById('commodity').value;
const daysBack = parseInt(document.getElementById('daysBack').value);
const stockCheckboxes = document.querySelectorAll('input[name="stocks"]:checked');
const stocks = Array.from(stockCheckboxes).map(cb => cb.value);
if (stocks.length === 0) { alert('Please select at least one defense stock'); return; }
const resultDiv = document.getElementById('result');
resultDiv.innerHTML = '<p>Loading analysis...</p>';
resultDiv.style.display = 'block';
try {
const response = await fetch('/api/analyze', {
method: 'POST',
headers: { 'Content-Type': 'application/json' },
body: JSON.stringify({ commodity: commodity, defense_stocks: stocks, days_back: daysBack })
});
if (!response.ok) {
const error = await response.json();
throw new Error(error.detail || 'Analysis failed');
}
const data = await response.json();
displayResults(data);
} catch (error) {
resultDiv.innerHTML = `<p class="error">Error: ${error.message}</p>`;
}
});
function displayResults(data) {
const resultDiv = document.getElementById('result');
let stocksHtml = data.defense_stocks_data.map(stock => `<tr>
<td>${stock.symbol}</td>
<td>$${stock.price.toFixed(2)}</td>
<td style="color: ${stock.change >= 0 ? 'green' : 'red'}">
${stock.change >= 0 ? '+' : ''}${stock.change.toFixed(2)} (${stock.change_percent}%)</td>
<td>${data.correlation_analysis[stock.symbol]}</td>
</tr>`).join('');

let newsHtml = '';
if (data.iran_news && data.iran_news.length > 0) {
newsHtml = `<h3>📰 Iran Conflict & Defense News</h3>
<div style="background: #f9f9f9; padding: 15px; border-radius: 5px; margin: 15px 0;">`;
data.iran_news.forEach(article => {
newsHtml += `<div style="margin-bottom: 15px; padding-bottom: 15px; border-bottom: 1px solid #ddd;">
<h4 style="margin: 0 0 5px 0;"><a href="${article.url}" target="_blank" style="color: #2c3e50; text-decoration: none;">${article.title}</a></h4>
<p style="margin: 5px 0; color: #666; font-size: 0.9em;">${article.description || 'No description available'}</p>
<p style="margin: 5px 0; font-size: 0.85em; color: #999;">
<strong>${article.source}</strong> • ${new Date(article.publishedAt).toLocaleDateString()}
</p>
</div>`;
});
newsHtml += `</div>`;
}

resultDiv.innerHTML = `<h2>Analysis Results</h2>
<h3>Commodity Data</h3>
<p><strong>${data.commodity_data.commodity}:</strong> $${data.commodity_data.price.toFixed(2)} ${data.commodity_data.unit}</p>
<p style="color: ${data.commodity_data.change_24h >= 0 ? 'green' : 'red'}">
24h Change: ${data.commodity_data.change_24h >= 0 ? '+' : ''}${data.commodity_data.change_24h.toFixed(2)}</p>
<h3>Defense Stocks</h3>
<table border="1" cellpadding="5" style="width:100%; border-collapse: collapse;">
<tr><th>Symbol</th><th>Price</th><th>Change</th><th>Correlation</th></tr>
${stocksHtml}</table>
${newsHtml}
<h3>Market Analysis</h3>
<p><strong>Market Sentiment:</strong> <span class="success">${data.market_sentiment}</span></p>
<p><strong>Recommendation:</strong> ${data.recommendation}</p>
<p><em>Generated at: ${new Date(data.generated_at).toLocaleString()}</em></p>`;
}
</script>
</body>
</html>"""
    return HTMLResponse(content=html_content)

@app.post("/api/analyze", response_model=AnalysisResult)
@limiter.limit("10/minute")
async def analyze_markets(request: Request, analysis_request: MarketAnalysisRequest):
    return await analyzer.analyze_markets(analysis_request)

@app.get("/api/commodity/{commodity_type}")
@limiter.limit("20/minute")
async def get_commodity_price(request: Request, commodity_type: str):
    client = FinancialDataClient()
    return await client.get_commodity_price(commodity_type)

@app.get("/api/stock/{symbol}")
@limiter.limit(limit_value="20/minute")
async def get_stock_price(request: Request, symbol: str):
    client = FinancialDataClient()
    return await client.get_stock_price(symbol)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)