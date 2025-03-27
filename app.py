from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import json
import os
import google.generativeai as genai
from dotenv import load_dotenv  # Load .env file

# ✅ Load API key from .env
load_dotenv("key.env")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Check if API key is loaded
if not GEMINI_API_KEY:
    raise ValueError("⚠️ Error: GEMINI_API_KEY is missing. Please check your .env file.")

# Initialize Gemini AI
genai.configure(api_key=GEMINI_API_KEY)

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle multiple requests in separate threads."""
    pass

def run_gemini(query):
    """Sends the query to Gemini AI and returns the response."""
    try:
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        response = model.generate_content(query)
        return response.text.strip() if response else "No response from Gemini AI."
    except Exception as e:
        return f"Error: {str(e)}"

def run_server():
    server = ThreadedHTTPServer(("0.0.0.0", 8000), RequestHandler)
    print("🚀 Server running on http://localhost:8000")
    server.serve_forever()

class RequestHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write("<h1>🚀 Server is running. Use POST request to analyze code.</h1>".encode("utf-8"))

    def do_POST(self):
        if self.path == "/":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                post_data = self.rfile.read(content_length)

                if not post_data:
                    raise ValueError("No data received")

                request_data = json.loads(post_data.decode("utf-8"))
                code_snippet = request_data.get("code", "").strip()

                if not code_snippet:
                    raise ValueError("No code snippet provided")

                # Query Gemini AI for analysis
                query = f"""
                You are an AI Code Analyzer. Analyze the following code snippet and generate a report covering:
                - Readability Test
                - Complexity
                - Naming Conventions
                - Error Handling
                - Duplication
                - Formatting
                - Private Key Detection
                Provide detailed suggestions for improvement.

                Code snippet:
                {code_snippet}
                """
                response = run_gemini(query)

                # Send response
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"report": response}).encode())

            except ValueError as ve:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(ve)}).encode())

            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())

if __name__ == "__main__":
    run_server()
