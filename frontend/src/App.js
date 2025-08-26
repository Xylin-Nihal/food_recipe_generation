import React, { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [input, setInput] = useState("");
  const [results, setResults] = useState([]);

  const searchRecipes = async () => {
    try {
      const response = await axios.post("http://localhost:8000/search", {
        ingredients: input.split(",").map((i) => i.trim()),
      });
      setResults(response.data);
    } catch (error) {
      console.error(error);
    }
  };

  const parseField = (field) => {
    try {
      return JSON.parse(field);
    } catch {
      return [field];
    }
  };

  return (
    <div className="App">
      {/* Navbar */}
      <nav className="navbar">
        <div className="logo">🍳 Recipe Finder</div>
        <ul className="nav-links">
          <li>Home</li>
          <li>Recipes</li>
          <li>About Us</li>
          <li>Contact</li>
          <li><button className="signup-btn">Sign Up</button></li>
        </ul>
      </nav>

      {/* Hero Section */}
      <header className="hero">
        <h1>Discover Delicious Recipes</h1>
        <p>Enter your ingredients and find recipes that match your pantry</p>
        <div className="search-box">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Enter ingredients (e.g., chicken, rice, etc.)"
          />
          <button onClick={searchRecipes}>Find Recipes</button>
        </div>
      </header>

      {/* Results */}
      <section className="recipes">
        <h2>Popular Recipes</h2>
        <div className="recipe-list">
          {results.map((r, index) => (
            <div key={index} className="recipe-card">
              {/* Recipe Image */}
              <div className="recipe-content">
                <h3>{r.title}</h3>
                <p><strong>Ingredients:</strong></p>
                <ul>
                  {parseField(r.ingredients).map((ing, i) => (
                    <li key={i}>{ing}</li>
                  ))}
                </ul>
                <p><strong>Directions:</strong></p>
                <ol>
                  {parseField(r.directions).map((step, i) => (
                    <li key={i}>{step}</li>
                  ))}
                </ol>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

export default App;