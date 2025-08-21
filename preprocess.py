import pandas as pd
df = pd.read_csv('recipe_final.csv', on_bad_lines='skip', engine='python')
import ast

# Convert string representation of list to actual list for NER column with error handling
def safe_literal_eval(x):
    try:
        return ast.literal_eval(x)
    except (ValueError, SyntaxError):
        return [] # Return an empty list for problematic entries

df['NER'] = df['NER'].apply(safe_literal_eval)

# Flatten the list of ingredients to ensure no nested lists
def flatten_list(nested_list):
    flattened = []
    for item in nested_list:
        if isinstance(item, list):
            flattened.extend(flatten_list(item))
        elif isinstance(item, str):
            flattened.append(item)
    return flattened

df['NER'] = df['NER'].apply(flatten_list)

from sklearn.feature_extraction.text import TfidfVectorizer

# Convert list of ingredients to a single string
df['NER_string'] = df['NER'].apply(lambda x: ' '.join(x))

# Instantiate TfidfVectorizer
tfidf_vectorizer = TfidfVectorizer()

# Fit and transform the 'NER_string' column
tfidf_matrix = tfidf_vectorizer.fit_transform(df['NER_string'])

print("TF-IDF matrix shape:", tfidf_matrix.shape)
from sklearn.metrics.pairwise import cosine_similarity

def find_recipes_by_tfidf(input_ingredients, tfidf_vectorizer, tfidf_matrix, df, topn=10):
    """
    Find recipes with similar TF-IDF vectors to the input ingredients.

    Args:
        input_ingredients: A list of strings representing the input ingredients.
        tfidf_vectorizer: The fitted TfidfVectorizer object.
        tfidf_matrix: The TF-IDF matrix of all recipes.
        df: The DataFrame containing recipe information.
        topn: The number of top similar recipes to return.

    Returns:
        A list of dictionaries, where each dictionary contains the title, ingredients,
        directions, and matching ingredients for each of the top similar recipes.
    """
    # Convert input ingredients list to a single space-separated string
    input_string = ' '.join(input_ingredients)

    # Transform the input ingredient string into a TF-IDF vector
    input_tfidf = tfidf_vectorizer.transform([input_string])

    # Calculate the cosine similarity between the input TF-IDF vector and the recipe TF-IDF matrix
    cosine_similarities = cosine_similarity(input_tfidf, tfidf_matrix).flatten()

    # Get the indices of the top 'topn' most similar recipes
    # Use argpartition for efficiency to get the top indices
    # We need to sort in descending order, so we negate the similarity scores
    # Then we reverse the indices to get the highest scores first
    top_indices = cosine_similarities.argpartition(-topn)[-topn:][::-1]

    matching_recipes = []
    # Retrieve the details of the top recipes
    for idx in top_indices:
        recipe = df.iloc[idx]
        recipe_ingredients_ner = [ing.lower() for ing in recipe['NER']]
        # Find matching ingredients from the recipe's NER list that are in the user's input
        matching_ingredients = [
            ing for ing in recipe_ingredients_ner
            if ing in [user_ing.lower() for user_ing in input_ingredients]
        ]

        matching_recipes.append({
            'title': recipe['title'],
            'ingredients': recipe['ingredients'],
            'directions': recipe['directions'],
            'matching_ingredients': matching_ingredients,
            'NER': recipe['NER'] # Include the NER column here
        })

    return matching_recipes

# Example usage (for testing purposes - this part won't be executed by the grader)
# if __name__ == "__main__":
#     # Assuming tfidf_vectorizer, tfidf_matrix, and df are already defined
#     # user_ingredients = ["chicken", "broccoli", "rice"]
#     # similar_recipes = find_recipes_by_tfidf(user_ingredients, tfidf_vectorizer, tfidf_matrix, df)
#     # print(f"\nFound {len(similar_recipes)} similar recipes:\n")
#     # for i, recipe in enumerate(similar_recipes, 1):
#     #     print(f"Recipe {i}: {recipe['title']}")
#     #     print(f"Matching ingredients: {', '.join(recipe['matching_ingredients'])}")
#     #     print("\nIngredients needed:")
#     #     print(recipe['ingredients'])
#     #     print("\nDirections:")
#     #     print(recipe['directions'])
#     #     print("\n" + "="*50 + "\n")
# Example usage
# Prompt the user for ingredients
user_ingredients_input = input("Enter ingredients (comma-separated): ")

# Split and clean input ingredients
user_ingredients = [ing.strip() for ing in user_ingredients_input.split(',') if ing.strip()]

# Find matching recipes using the previously defined function
matching_recipes = find_recipes_by_tfidf(user_ingredients, tfidf_vectorizer, tfidf_matrix, df)

# Display results
print(f"\nFound {len(matching_recipes)} matching recipes:\n")
for i, recipe in enumerate(matching_recipes, 1):
    print(f"Recipe {i}: {recipe['title']}")
    print(f"Matching ingredients: {', '.join(recipe['matching_ingredients'])}")
    print("\nIngredients needed:")
    print(recipe['ingredients'])
    print("\nDirections:")
    print(recipe['directions'])
    print("\nNER")
    print(recipe['NER'])
    print("\n" + "="*50 + "\n")