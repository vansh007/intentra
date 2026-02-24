import google.generativeai as genai

genai.configure(api_key="AIzaSyAWxcPAZg2vnEc5sP_2Ezz1yy5H7JsaN6I")
model = genai.GenerativeModel("models/gemini-2.5-flash")


response = model.generate_content("Say hello in one sentence.")
print(response.text)