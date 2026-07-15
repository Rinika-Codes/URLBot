import { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Bot, Send, Search, Link as LinkIcon, Loader2 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import './App.css';

const API_URL = import.meta.env.VITE_API_URL;

function App() {
  const [url, setUrl] = useState('');
  const [messages, setMessages] = useState([
    { role: 'bot', content: 'Hello! I am URLBot. Provide a website URL to scrape, then ask me anything about it.' }
  ]);
  const [input, setInput] = useState('');
  
  const [isScraping, setIsScraping] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [scrapeResult, setScrapeResult] = useState('');

  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleScrape = async (e) => {
    e.preventDefault();
    if (!url) return;
    
    setIsScraping(true);
    setScrapeResult('');
    
    try {
      const response = await axios.post(
        `${API_URL}/scrape`,
        { url, max_pages: 5 },
        { timeout: 120000 }  // 2 minutes — large sites can take a while
      );
      setScrapeResult(`✅ Successfully scraped ${response.data.pages_crawled} page(s). You can now ask questions!`);
      setMessages(prev => [...prev, { role: 'bot', content: `I have finished studying **${url}**. What would you like to know?` }]);
    } catch (err) {
      const detail = err.response?.data?.detail || err.message || 'Unknown error';
      setScrapeResult(`❌ Failed to scrape: ${detail}`);
      console.error('Scrape error:', err);
    } finally {
      setIsScraping(false);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMsg = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setIsTyping(true);

    try {
      const response = await axios.post(`${API_URL}/chat`, {
        message: userMsg,
        chat_history: messages
      });
      setMessages(prev => [...prev, { role: 'bot', content: response.data.response }]);
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'An error occurred while generating the response.';
      setMessages(prev => [...prev, { role: 'bot', content: `Error: ${errorMsg}` }]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="app-container">
      {/* Sidebar - Scraper Config */}
      <aside className="sidebar glass-panel">
        <div className="brand">
          <Bot size={32} color="#10b981" />
          <h1>URLBot</h1>
        </div>

        <form className="config-section" onSubmit={handleScrape}>
          <h2>Configuration</h2>
          
          <div className="input-group">
            <label>Website URL</label>
            <div style={{ position: 'relative' }}>
              <LinkIcon size={16} color="#94a3b8" style={{ position: 'absolute', top: '12px', left: '12px' }} />
              <input 
                type="url" 
                placeholder="https://example.com" 
                className="styled-input"
                style={{ paddingLeft: '2.5rem', width: '100%' }}
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                required
              />
            </div>
          </div>

          <button type="submit" className="primary-btn" disabled={isScraping || !url}>
            {isScraping ? (
              <><Loader2 size={18} className="spinner" /> Scraping...</>
            ) : (
              <><Search size={18} /> Scrape Website</>
            )}
          </button>

          {isScraping && (
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', textAlign: 'center', marginTop: '-0.25rem' }}>
              ⏳ This may take a minute for large sites...
            </p>
          )}

          {scrapeResult && (
            <div className={`scrape-status ${scrapeResult.startsWith('✅') ? 'success' : scrapeResult.startsWith('❌') ? 'error' : ''}`}>
              {scrapeResult}
            </div>
          )}
        </form>
      </aside>

      {/* Main Chat Area */}
      <main className="chat-container glass-panel">
        <header className="chat-header">
          <div>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 600 }}>Assistant</h2>
          </div>
        </header>

        <div className="messages-area">
          {messages.map((msg, idx) => (
            <div key={idx} className={`message-wrapper ${msg.role}`}>
              <div className="avatar">
                {msg.role === 'bot' ? <Bot size={20} color="white" /> : 'U'}
              </div>
              <div className="message-content">
                {msg.role === 'bot' ? (
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                ) : (
                  msg.content
                )}
              </div>
            </div>
          ))}
          {isTyping && (
            <div className="message-wrapper bot">
              <div className="avatar">
                <Bot size={20} color="white" />
              </div>
              <div className="message-content typing-indicator">
                <div className="dot"></div>
                <div className="dot"></div>
                <div className="dot"></div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <form className="input-area" onSubmit={handleSendMessage}>
          <textarea 
            className="chat-input" 
            placeholder="Ask a question..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSendMessage(e);
              }
            }}
          />
          <button type="submit" className="send-btn" disabled={!input.trim() || isTyping}>
            <Send size={20} />
          </button>
        </form>
      </main>
    </div>
  );
}

export default App;