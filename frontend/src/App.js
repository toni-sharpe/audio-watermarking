import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './Home';
import Artists from './Artists';
import Llm from './Llm';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/artists" element={<Artists />} />
          <Route path="/llm" element={<Llm />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
