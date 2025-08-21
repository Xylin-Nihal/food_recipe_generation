import React, { useState } from "react";
import axios from "axios";

function App() {
  const [input, setInput] = useState("");
  const [results, setResults] = useState([]);

  const searchRecipes = async () => {
    try {
      const response = await axios.post("http://localhost:8000/search", {
        ingredients: input.split(",").map(i => i.trim())
      });
      console.log("API Response:", response.data);
      setResults(response.data);
    } catch (error) {
      console.error(error);
    }
  };

  // helper to parse stringified arrays safely
  const parseField = (field) => {
    try {
      return JSON.parse(field);
    } catch {
      return [field]; // fallback if it's not a JSON array
    }
  };

  return (
    <div style={{ padding: "20px" }}>
      <h1>Recipe Finder</h1>
      <input
        type="text"
        value={input}
        onChange={e => setInput(e.target.value)}
        placeholder="Enter ingredients (comma separated)"
        style={{ marginRight: "10px" }}
      />
      <button onClick={searchRecipes}>Search</button>

      <div style={{ marginTop: "20px" }}>
        {results.map((r, index) => (
          <div key={index} style={{ marginTop: "20px" }}>
            <h2>{r.title}</h2>
            
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
        ))}
      </div>
    </div>
  );
}

export default App;
