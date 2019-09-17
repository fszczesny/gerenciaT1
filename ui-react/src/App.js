import React from "react";
import logo from "./logo.svg";
import "./App.css";
import axios from "axios";

function App() {
  const getDate = async () => {
    try {
      const response = await axios.get("http://127.0.0.1:5002/trafego", {
        method: "GET",
        mode: "no-cors",
        headers: {
          "Access-Control-Allow-Origin": "127.0.0.1",
          "Content-Type": "application/json",
          "Access-Control-Allow-Headers": "Content-Type"
        }
      });
      console.log("response", response.data);
    } catch (err) {
      console.warn("ERROR:", err);
    }
  };

  return (
    <div onClick={getDate} className="App">
      CLIQUE EM MIM PARA FAZER O DOWNLOAD
    </div>
  );
}

export default App;
