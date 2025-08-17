import React, { useEffect, useRef } from 'react';
import { MessageSquare, Plus } from "lucide-react";
import { marked } from 'marked';
import useChatStore from '@/stores/chatStore';
import { Boxes } from '@/components/ui/background-boxes';

const ChatInterface = () => {
  const {
    messages,
    isLoading,
    currentInput,
    setCurrentInput,
    sendMessage,
    loadConversationHistory,
    startNewChat
  } = useChatStore();

  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (messages.length > 0) {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  useEffect(() => {
    loadConversationHistory();
  }, [loadConversationHistory]);

  const handleSend = async () => {
    if (currentInput.trim() && !isLoading) {
      const messageToSend = currentInput.trim();
      setCurrentInput('');
      await sendMessage(messageToSend);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <>
      <style>
        {`
          @keyframes bounce {
            0%, 80%, 100% {
              transform: scale(0.8);
              opacity: 0.5;
            }
            40% {
              transform: scale(1);
              opacity: 1;
            }
          }
          
          .markdown-content {
            line-height: 1.6;
          }
          
          .markdown-content h1,
          .markdown-content h2,
          .markdown-content h3,
          .markdown-content h4,
          .markdown-content h5,
          .markdown-content h6 {
            color: #60a5fa;
            margin-top: 24px;
            margin-bottom: 12px;
            font-weight: 600;
          }
          
          .markdown-content h1 { font-size: 1.5em; }
          .markdown-content h2 { font-size: 1.3em; }
          .markdown-content h3 { font-size: 1.2em; }
          
          .markdown-content p {
            margin-bottom: 16px;
          }
          
          .markdown-content ul,
          .markdown-content ol {
            margin-bottom: 16px;
            padding-left: 20px;
          }
          
          .markdown-content li {
            margin-bottom: 8px;
          }
          
          .markdown-content strong {
            color: #fbbf24;
            font-weight: 600;
          }
          
          .markdown-content em {
            color: #a78bfa;
            font-style: italic;
          }
          
          .markdown-content code {
            background-color: rgba(55, 65, 81, 0.8);
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            color: #f59e0b;
          }
          
          .markdown-content pre {
            background-color: rgba(55, 65, 81, 0.8);
            padding: 16px;
            border-radius: 8px;
            overflow-x: auto;
            margin-bottom: 16px;
          }
          
          .markdown-content pre code {
            background: none;
            padding: 0;
          }
          
          .markdown-content blockquote {
            border-left: 4px solid #60a5fa;
            padding-left: 16px;
            margin: 16px 0;
            font-style: italic;
            color: #d1d5db;
          }
          
          .markdown-content table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 16px;
            background-color: rgba(31, 41, 55, 0.5);
            border-radius: 8px;
            overflow: hidden;
          }
          
          .markdown-content th,
          .markdown-content td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
          }
          
          .markdown-content th {
            background-color: rgba(55, 65, 81, 0.8);
            font-weight: 600;
            color: #60a5fa;
          }
          
          .markdown-content tr:hover {
            background-color: rgba(55, 65, 81, 0.3);
          }
          
          .markdown-content a {
            color: #60a5fa;
            text-decoration: none;
          }
          
          .markdown-content a:hover {
            text-decoration: underline;
          }
          
          .markdown-content hr {
            border: none;
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
            margin: 24px 0;
          }
        `}
      </style>
      <div style={{
        height: '100vh',
        backgroundColor: '#000',
        color: '#fff',
        display: 'flex',
        flexDirection: 'column',
        position: 'relative'
      }}>
      {/* Animated Background - Behind everything */}
      <div style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        zIndex: -10,
        opacity: 0.2,
        overflow: 'hidden',
        pointerEvents: 'none'
      }}>
        <Boxes />
      </div>

      {/* Header */}
      <div style={{
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        backdropFilter: 'blur(20px)',
        padding: '16px 24px',
        borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        position: 'relative',
        zIndex: 20
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            width: '32px',
            height: '32px',
            borderRadius: '8px',
            backgroundColor: 'rgba(255, 255, 255, 0.1)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <MessageSquare size={16} color="white" strokeWidth={2} />
          </div>
          <div>
            <h1 style={{ 
              margin: 0, 
              fontSize: '16px', 
              fontWeight: '600',
              color: '#ffffff',
              letterSpacing: '-0.01em'
            }}>
              Financial Chat
            </h1>
            <p style={{ 
              margin: 0, 
              fontSize: '13px', 
              color: 'rgba(255, 255, 255, 0.6)',
              fontWeight: '400'
            }}>
              AI Assistant
            </p>
          </div>
        </div>
        <button
          onClick={startNewChat}
          style={{
            backgroundColor: 'rgba(255, 255, 255, 0.1)',
            backdropFilter: 'blur(10px)',
            color: '#ffffff',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            padding: '8px 12px',
            borderRadius: '20px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            fontSize: '13px',
            fontWeight: '500',
            transition: 'all 0.2s ease'
          }}
          onMouseOver={(e) => {
            e.target.style.backgroundColor = 'rgba(255, 255, 255, 0.15)';
          }}
          onMouseOut={(e) => {
            e.target.style.backgroundColor = 'rgba(255, 255, 255, 0.1)';
          }}
        >
          <Plus size={14} />
          New
        </button>
      </div>

      {/* Messages */}
      <div style={{
        flex: 1,
        padding: '16px',
        overflowY: 'auto',
        paddingBottom: '120px',
        position: 'relative',
        zIndex: 10
      }}>
        {messages.length === 0 ? (
          <div style={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            height: '100%',
            textAlign: 'center'
          }}>
            <div>
              <div style={{
                width: '64px',
                height: '64px',
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
                backdropFilter: 'blur(8px)',
                borderRadius: '50%',
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                margin: '0 auto 16px',
                border: '1px solid rgba(255, 255, 255, 0.1)'
              }}>
                <MessageSquare size={32} color="#60a5fa" />
              </div>
              <h3 style={{ margin: '0 0 8px', fontSize: '20px' }}>
                Welcome to Financial Chat
              </h3>
              <p style={{ margin: 0, color: '#9ca3af', maxWidth: '400px' }}>
                Ask me about stocks, portfolio management, financial news, market analysis, 
                or any investment-related questions.
              </p>
            </div>
          </div>
        ) : (
          <div style={{ maxWidth: '800px', margin: '0 auto' }}>
            {messages.map((message, index) => (
              <div
                key={message.id || index}
                style={{
                  marginBottom: '16px',
                  display: 'flex',
                  justifyContent: message.role === 'user' ? 'flex-end' : 'flex-start',
                  alignItems: 'flex-start',
                  gap: '8px'
                }}
              >
                {/* AI Avatar - minimal */}
                {message.role !== 'user' && (
                  <div style={{
                    width: '24px',
                    height: '24px',
                    borderRadius: '6px',
                    backgroundColor: 'rgba(255, 255, 255, 0.1)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexShrink: 0,
                    marginTop: '2px'
                  }}>
                    <MessageSquare size={12} color="white" strokeWidth={2} />
                  </div>
                )}

                <div style={{
                  maxWidth: '70%',
                  padding: message.role === 'user' ? '12px 16px' : '12px 16px',
                  borderRadius: message.role === 'user' ? 
                    '18px 18px 4px 18px' : 
                    '18px 18px 18px 4px',
                  backgroundColor: message.role === 'user' ? 
                    'rgba(255, 255, 255, 0.1)' : 
                    'rgba(255, 255, 255, 0.05)',
                  backdropFilter: 'blur(10px)',
                  border: '1px solid rgba(255, 255, 255, 0.08)',
                  color: '#fff',
                  fontSize: '14px',
                  lineHeight: '1.5',
                  fontWeight: '400'
                }}>
                  {/* Render message content with markdown support for assistant */}
                  {message.role === 'assistant' ? (
                    <div 
                      className="markdown-content"
                      style={{ 
                        whiteSpace: 'normal',
                        wordBreak: 'break-word'
                      }}
                      dangerouslySetInnerHTML={{ 
                        __html: marked.parse(message.content || '') 
                      }}
                    />
                  ) : (
                    <div style={{ 
                      whiteSpace: 'pre-wrap',
                      wordBreak: 'break-word'
                    }}>
                      {message.content}
                    </div>
                  )}
                </div>

                {/* User Avatar - minimal */}
                {message.role === 'user' && (
                  <div style={{
                    width: '24px',
                    height: '24px',
                    borderRadius: '6px',
                    backgroundColor: 'rgba(255, 255, 255, 0.15)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '10px',
                    flexShrink: 0,
                    marginTop: '2px'
                  }}>
                    •
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {isLoading && (
          <div style={{
            maxWidth: '800px',
            margin: '16px auto 0',
            padding: '0 16px',
            display: 'flex',
            justifyContent: 'flex-start',
            alignItems: 'flex-start',
            gap: '8px'
          }}>
            {/* AI Avatar for loading - minimalistic */}
            <div style={{
              width: '24px',
              height: '24px',
              borderRadius: '6px',
              backgroundColor: 'rgba(255, 255, 255, 0.1)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0,
              marginTop: '2px'
            }}>
              <MessageSquare size={12} color="white" strokeWidth={2} />
            </div>
            
            <div style={{
              padding: '12px 16px',
              borderRadius: '18px 18px 18px 4px',
              backgroundColor: 'rgba(255, 255, 255, 0.05)',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              <div style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
                <div style={{
                  width: '6px',
                  height: '6px',
                  backgroundColor: 'rgba(255, 255, 255, 0.6)',
                  borderRadius: '50%',
                  animation: 'bounce 1.4s ease-in-out infinite both',
                  animationDelay: '0s'
                }}></div>
                <div style={{
                  width: '6px',
                  height: '6px',
                  backgroundColor: 'rgba(255, 255, 255, 0.6)',
                  borderRadius: '50%',
                  animation: 'bounce 1.4s ease-in-out infinite both',
                  animationDelay: '0.2s'
                }}></div>
                <div style={{
                  width: '6px',
                  height: '6px',
                  backgroundColor: 'rgba(255, 255, 255, 0.6)',
                  borderRadius: '50%',
                  animation: 'bounce 1.4s ease-in-out infinite both',
                  animationDelay: '0.4s'
                }}></div>
              </div>
              <span style={{
                fontSize: '14px',
                fontWeight: '400',
                color: 'rgba(255, 255, 255, 0.7)'
              }}>
                Thinking...
              </span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Dynamic Island Input */}
      <div style={{
        position: 'fixed',
        bottom: '20px',
        left: '50%',
        transform: 'translateX(-50%)',
        zIndex: 30
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          backgroundColor: 'rgba(0, 0, 0, 0.85)',
          backdropFilter: 'blur(20px)',
          borderRadius: currentInput ? '24px' : '40px',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          padding: currentInput ? '8px 12px 8px 20px' : '12px 20px',
          minWidth: currentInput ? '400px' : '200px',
          maxWidth: '500px',
          transition: 'all 0.3s cubic-bezier(0.25, 0.1, 0.25, 1)',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.6)'
        }}>
          {/* Input field */}
          <input
            type="text"
            value={currentInput}
            onChange={(e) => setCurrentInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={currentInput ? "" : "Ask me anything..."}
            disabled={isLoading}
            style={{
              flex: 1,
              backgroundColor: 'transparent',
              border: 'none',
              outline: 'none',
              color: '#ffffff',
              fontSize: '14px',
              fontWeight: '400',
              placeholder: 'rgba(255, 255, 255, 0.5)',
              minWidth: '0'
            }}
          />

          {/* Loading indicator or Send button */}
          {isLoading ? (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              paddingRight: '4px'
            }}>
              <div style={{
                width: '4px',
                height: '4px',
                backgroundColor: 'rgba(255, 255, 255, 0.6)',
                borderRadius: '50%',
                animation: 'bounce 1.4s ease-in-out infinite both',
                animationDelay: '0s'
              }}></div>
              <div style={{
                width: '4px',
                height: '4px',
                backgroundColor: 'rgba(255, 255, 255, 0.6)',
                borderRadius: '50%',
                animation: 'bounce 1.4s ease-in-out infinite both',
                animationDelay: '0.2s'
              }}></div>
              <div style={{
                width: '4px',
                height: '4px',
                backgroundColor: 'rgba(255, 255, 255, 0.6)',
                borderRadius: '50%',
                animation: 'bounce 1.4s ease-in-out infinite both',
                animationDelay: '0.4s'
              }}></div>
            </div>
          ) : currentInput.trim() ? (
            <button
              onClick={handleSend}
              style={{
                width: '24px',
                height: '24px',
                borderRadius: '50%',
                backgroundColor: 'rgba(255, 255, 255, 0.2)',
                border: 'none',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                transition: 'all 0.2s ease',
                fontSize: '12px',
                color: '#ffffff'
              }}
              onMouseOver={(e) => {
                e.target.style.backgroundColor = 'rgba(255, 255, 255, 0.3)';
                e.target.style.transform = 'scale(1.1)';
              }}
              onMouseOut={(e) => {
                e.target.style.backgroundColor = 'rgba(255, 255, 255, 0.2)';
                e.target.style.transform = 'scale(1)';
              }}
            >
              →
            </button>
          ) : null}
        </div>
      </div>
      </div>
    </>
  );
};

export default ChatInterface;
