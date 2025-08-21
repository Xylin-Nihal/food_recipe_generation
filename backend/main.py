from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import pandas as pd
import ast
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow frontend (React) to talk to backend (FastAPI)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # you can restrict later to ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Load CSV
df = pd.read_csv("recipe_final.csv", on_bad_lines="skip", engine="python")

# Clean NER column
def safe_literal_eval(x):
    try:
        return ast.literal_eval(x)
    except (ValueError, SyntaxError):
        return []

df["NER"] = df["NER"].apply(safe_literal_eval)
df["NER"] = df["NER"].apply(lambda x: [i for i in x if isinstance(i, str)])
df["NER_string"] = df["NER"].apply(lambda x: " ".join(x))

# TF-IDF model
tfidf_vectorizer = TfidfVectorizer()
tfidf_matrix = tfidf_vectorizer.fit_transform(df["NER_string"])

class IngredientsRequest(BaseModel):
    ingredients: List[str]

@app.post("/search")
def search_recipes(request: IngredientsRequest):
    input_string = " ".join(request.ingredients)
    input_tfidf = tfidf_vectorizer.transform([input_string])
    cosine_similarities = cosine_similarity(input_tfidf, tfidf_matrix).flatten()
    top_indices = cosine_similarities.argsort()[-5:][::-1]

    results = []
    for idx in top_indices:
        recipe = df.iloc[idx]
        results.append({
            "title": recipe["title"],
            "ingredients": recipe["ingredients"],
            "directions": recipe["directions"],
            "NER": recipe["NER"]
        })
    return results
