import os
import requests
from flask import Flask, request

app = Flask(__name__)

# Zenserp API Credentials
ZENSERP_API_KEY = "8d38a4d0-f099-11ef-a5fc-b1de60a7a21d"
ZENSERP_ENDPOINT = "https://app.zenserp.com/api/v2/search"

# Zenserp Search Function
def zenserp_search(query):
    params = {
        "q": query,
        "apikey": ZENSERP_API_KEY,
    }
    response = requests.get(ZENSERP_ENDPOINT, params=params)
    return response.json() if response.status_code == 200 else {"error": "Failed to fetch results"}

# Flask Route to Handle Search Queries
@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("q")
    if not query:
        return {"error": "Missing search query"}, 400

    search_results = zenserp_search(query)
    return {"results": search_results}

# New Route for Twilio SMS Handling
@app.route("/sms", methods=["POST"])
def sms_reply():
    from twilio.twiml.messaging_response import MessagingResponse

    # Get the SMS content
    incoming_msg = request.form.get("Body", "").strip()

    # Perform a search if a query is given
    if incoming_msg:
        search_results = zenserp_search(incoming_msg)
        first_result = search_results.get("organic", [{}])[0]  # Extract first result

        title = first_result.get("title", "No title found")
        link = first_result.get("url", "No link found")

        reply_text = f"🔎 {title}\n🔗 {link}" if title and link else "No results found."
    else:
        reply_text = "Please send a search query."

    # Twilio Response
    response = MessagingResponse()
    response.message(reply_text)
    return str(response)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
    
