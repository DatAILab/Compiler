import React, { useState, useEffect, useRef } from 'react';
import { Card } from '@/components/ui/card';

const SQL_KEYWORDS = [
  'SELECT', 'FROM', 'WHERE', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'TABLE',
  'INTO', 'VALUES', 'AND', 'OR', 'NOT', 'NULL', 'AS', 'JOIN', 'LEFT', 'RIGHT', 'INNER',
  'OUTER', 'GROUP BY', 'ORDER BY', 'HAVING', 'LIMIT', 'OFFSET', 'UNION', 'ALL'
];

const SQLEditor = () => {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [cursorPosition, setCursorPosition] = useState(0);
  const textareaRef = useRef(null);

  const highlightSQL = (text) => {
    let highlighted = text;
    SQL_KEYWORDS.forEach(keyword => {
      const regex = new RegExp(`\\b${keyword}\\b`, 'gi');
      highlighted = highlighted.replace(regex, `<span class="text-blue-600 font-semibold">${keyword}</span>`);
    });
    return highlighted;
  };

  const getSuggestions = (text, position) => {
    const beforeCursor = text.slice(0, position);
    const words = beforeCursor.split(/\s+/);
    const currentWord = words[words.length - 1].toUpperCase();

    if (currentWord) {
      return SQL_KEYWORDS.filter(keyword => 
        keyword.startsWith(currentWord) && keyword !== currentWord
      );
    }
    return [];
  };

  const handleInput = (e) => {
    const newText = e.target.value;
    const newPosition = e.target.selectionStart;
    setQuery(newText);
    setCursorPosition(newPosition);
    setSuggestions(getSuggestions(newText, newPosition));
  };

  const handleSuggestionClick = (suggestion) => {
    const beforeCursor = query.slice(0, cursorPosition);
    const afterCursor = query.slice(cursorPosition);
    const words = beforeCursor.split(/\s+/);
    const lastWord = words.pop();
    const newQuery = [...words, suggestion, ''].join(' ') + afterCursor;
    setQuery(newQuery);
    setSuggestions([]);
    textareaRef.current?.focus();
  };

  return (
    <Card className="p-4 w-full max-w-4xl">
      <div className="relative">
        <textarea
          ref={textareaRef}
          value={query}
          onChange={handleInput}
          className="w-full h-64 p-4 font-mono text-base bg-slate-50 border rounded-md resize-none"
          placeholder="Enter your SQL query..."
        />
        <div 
          className="w-full h-64 p-4 font-mono text-base absolute top-0 left-0 pointer-events-none"
          dangerouslySetInnerHTML={{ __html: highlightSQL(query) }}
        />
        {suggestions.length > 0 && (
          <div className="absolute z-10 bg-white border rounded-md shadow-lg mt-1">
            {suggestions.map((suggestion, index) => (
              <div
                key={index}
                className="px-4 py-2 hover:bg-slate-100 cursor-pointer"
                onClick={() => handleSuggestionClick(suggestion)}
              >
                {suggestion}
              </div>
            ))}
          </div>
        )}
      </div>
    </Card>
  );
};

export default SQLEditor;