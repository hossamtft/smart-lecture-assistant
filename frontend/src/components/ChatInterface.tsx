import { useState, useRef, useEffect } from 'react';
import { queryLectures } from '../services/api';
import type { QueryRequest, QueryResponse } from '../types';
import './ChatInterface.css';

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  sources?: QueryResponse['sources'];
  processingTime?: number;
}

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [moduleCode, setModuleCode] = useState('');
  const [currentWeek, setCurrentWeek] = useState<number>(12);
  const [temporalFilter, setTemporalFilter] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!input.trim() || !moduleCode.trim()) {
      return;
    }

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: input
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const request: QueryRequest = {
        query: input,
        module_code: moduleCode.toUpperCase(),
        top_k: 5,
        temporal_filter: temporalFilter,
        current_week: temporalFilter ? currentWeek : undefined
      };

      const response = await queryLectures(request);

      // Add assistant message
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: response.answer,
        sources: response.sources,
        processingTime: response.processing_time
      };

      setMessages(prev => [...prev, assistantMessage]);

    } catch (error: any) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: `Error: ${error.response?.data?.detail || 'Failed to get response. Please try again.'}`
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const clearChat = () => {
    setMessages([]);
  };

  return (
    <div className="chat-container">
      {/* Configuration Panel */}
      <div className="chat-config">
        <h2>Q&A Assistant</h2>
        <div className="config-fields">
          <div className="config-group">
            <label htmlFor="moduleCode">Module Code *</label>
            <input
              type="text"
              id="moduleCode"
              placeholder="e.g., COMP3001"
              value={moduleCode}
              onChange={(e) => setModuleCode(e.target.value)}
            />
          </div>

          <div className="config-group checkbox-group">
            <label>
              <input
                type="checkbox"
                checked={temporalFilter}
                onChange={(e) => setTemporalFilter(e.target.checked)}
              />
              <span>Temporal Awareness</span>
            </label>
            {temporalFilter && (
              <div className="week-selector">
                <label htmlFor="currentWeek">Current Week:</label>
                <input
                  type="number"
                  id="currentWeek"
                  min="1"
                  max="24"
                  value={currentWeek}
                  onChange={(e) => setCurrentWeek(parseInt(e.target.value))}
                />
              </div>
            )}
          </div>

          {messages.length > 0 && (
            <button onClick={clearChat} className="clear-btn">
              Clear Chat
            </button>
          )}
        </div>
      </div>

      {/* Messages */}
      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="empty-state">
            <span className="empty-icon">💬</span>
            <p>Ask a question about your lecture content</p>
            <p className="empty-hint">
              I'll search through your uploaded lectures and provide answers with source citations.
            </p>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <div key={message.id} className={`message ${message.type}`}>
                <div className="message-header">
                  <span className="message-avatar">
                    {message.type === 'user' ? '👤' : '🤖'}
                  </span>
                  <span className="message-label">
                    {message.type === 'user' ? 'You' : 'Assistant'}
                  </span>
                  {message.processingTime && (
                    <span className="processing-time">
                      {message.processingTime.toFixed(2)}s
                    </span>
                  )}
                </div>

                <div className="message-content">
                  {message.content}
                </div>

                {message.sources && message.sources.length > 0 && (
                  <div className="message-sources">
                    <p className="sources-header">Sources:</p>
                    {message.sources.map((source, idx) => (
                      <div key={idx} className="source-item">
                        <div className="source-meta">
                          <span className="source-lecture">{source.lecture_title}</span>
                          <span className="source-location">
                            Week {source.week_number}, Slide {source.slide_number}
                          </span>
                          <span className="source-similarity">
                            {(source.similarity_score * 100).toFixed(0)}% match
                          </span>
                        </div>
                        <p className="source-content">{source.content}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
            {isLoading && (
              <div className="message assistant loading">
                <div className="message-header">
                  <span className="message-avatar">🤖</span>
                  <span className="message-label">Assistant</span>
                </div>
                <div className="message-content">
                  <div className="loading-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="chat-input-form">
        <input
          type="text"
          className="chat-input"
          placeholder={moduleCode ? "Ask a question..." : "Enter module code first..."}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={isLoading || !moduleCode}
        />
        <button
          type="submit"
          className="send-btn"
          disabled={isLoading || !input.trim() || !moduleCode}
        >
          Send
        </button>
      </form>
    </div>
  );
}
