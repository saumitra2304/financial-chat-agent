import React, { useEffect, useRef } from 'react';
import { MessageSquare, Plus, Send, Bot, User, Sparkles } from "lucide-react";
import { marked } from 'marked';
import useChatStore from '@/stores/chatStore';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { cn } from '@/lib/utils';

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
    <div className="min-h-screen bg-gradient-to-br from-black via-gray-950 to-black text-white flex flex-col">
      {/* Fixed Header - Completely Fixed Position */}
      <div className="fixed top-0 left-0 right-0 z-40 bg-black/90 backdrop-blur-md border-b border-gray-800">
        <div className="p-2 px-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-3">
              <div className="relative">
                <Avatar className="h-7 w-7">
                  <AvatarFallback className="bg-gradient-to-r from-purple-500 to-pink-600 text-white">
                    <Sparkles size={14} />
                  </AvatarFallback>
                </Avatar>
                <div className="absolute -top-0.5 -right-0.5">
                  <div className="w-1.5 h-1.5 bg-green-400 rounded-full animate-pulse" />
                </div>
              </div>
              <div>
                <div className="text-sm font-semibold text-white">
                  Financial Assistant
                </div>
                <div className="flex items-center space-x-2">
                  <Badge variant="secondary" className="bg-green-500/20 text-green-400 border-green-500/30 text-xs px-1.5 py-0">
                    Online
                  </Badge>
                  <Separator orientation="vertical" className="h-2.5 bg-gray-700" />
                  <span className="text-xs text-gray-400">AI-Powered</span>
                </div>
              </div>
            </div>
            <Button
              onClick={startNewChat}
              variant="outline"
              size="sm"
              className="bg-gray-900 hover:bg-gray-800 border-gray-700 text-white h-7 px-3 text-xs hover:shadow-lg hover:shadow-purple-500/20 hover:border-purple-500/50 transition-all duration-300"
            >
              <Plus size={10} className="mr-1.5" />
              New Chat
            </Button>
          </div>
        </div>
      </div>

      {/* Scrollable Messages Area - With Top Padding for Fixed Header */}
      <div className="flex-1 pt-16 overflow-hidden">
        <div className="h-full overflow-y-auto p-3">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full py-8">
              <Card className="bg-gray-900/80 backdrop-blur-sm border-gray-800 max-w-md mx-auto hover:shadow-lg hover:shadow-purple-500/10 transition-all duration-300">
                <CardContent className="p-5 text-center space-y-3">
                  <div className="relative mx-auto w-12 h-12">
                    <div className="absolute inset-0 bg-gradient-to-r from-purple-400 to-pink-500 rounded-full animate-pulse opacity-20" />
                    <div className="absolute inset-1 bg-gray-950 rounded-full flex items-center justify-center">
                      <MessageSquare size={20} className="text-purple-400" />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <h3 className="text-lg font-bold text-white">
                      Welcome to Financial Chat
                    </h3>
                    <p className="text-gray-400 text-xs leading-relaxed">
                      Your AI-powered financial assistant is ready to help with stocks, portfolio management, 
                      market analysis, and investment strategies.
                    </p>
                  </div>
                  <div className="flex flex-wrap gap-1.5 justify-center">
                    <Badge variant="outline" className="border-purple-400/30 text-purple-400 bg-purple-500/10 text-xs px-2 py-0.5">Stock Analysis</Badge>
                    <Badge variant="outline" className="border-green-400/30 text-green-400 bg-green-500/10 text-xs px-2 py-0.5">Portfolio</Badge>
                    <Badge variant="outline" className="border-pink-400/30 text-pink-400 bg-pink-500/10 text-xs px-2 py-0.5">Market News</Badge>
                  </div>
                </CardContent>
              </Card>
            </div>
          ) : (
            <div className="max-w-4xl mx-auto space-y-2.5 pb-24">
              {messages.map((message, index) => (
                <div
                  key={message.id || index}
                  className={`flex gap-2.5 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  {/* AI Avatar */}
                  {message.role !== 'user' && (
                    <div className="flex-shrink-0">
                      <Avatar className="h-5 w-5">
                        <AvatarFallback className="bg-gradient-to-r from-purple-500 to-pink-600 text-white">
                          <Bot size={10} />
                        </AvatarFallback>
                      </Avatar>
                    </div>
                  )}

                  <Card className={`max-w-[70%] transition-all duration-300 hover:shadow-lg ${
                    message.role === 'user' 
                      ? 'bg-gradient-to-r from-purple-600/20 to-pink-600/20 border-purple-500/30 hover:shadow-purple-500/20 hover:border-purple-400/50' 
                      : 'bg-gray-950/90 border-gray-800 hover:shadow-gray-500/20 hover:border-gray-700'
                  }`}>
                    <CardContent className="p-1.5 py-1">
                      {message.role === 'assistant' ? (
                        <div 
                          className="markdown-content text-sm leading-tight text-gray-200"
                          dangerouslySetInnerHTML={{ 
                            __html: marked.parse(message.content || '') 
                          }}
                        />
                      ) : (
                        <p className="text-sm leading-tight text-white whitespace-pre-wrap">
                          {message.content}
                        </p>
                      )}
                    </CardContent>
                  </Card>

                  {/* User Avatar */}
                  {message.role === 'user' && (
                    <div className="flex-shrink-0">
                      <Avatar className="h-5 w-5">
                        <AvatarFallback className="bg-gray-700 text-white">
                          <User size={10} />
                        </AvatarFallback>
                      </Avatar>
                    </div>
                  )}
                </div>
              ))}

              {/* Loading State */}
              {isLoading && (
                <div className="flex gap-2.5 justify-start">
                  <div className="flex-shrink-0">
                    <Avatar className="h-5 w-5">
                      <AvatarFallback className="bg-gradient-to-r from-purple-500 to-pink-600 text-white">
                        <Bot size={10} />
                      </AvatarFallback>
                    </Avatar>
                  </div>
                  
                  <Card className="bg-gray-950/90 border-gray-800">
                    <CardContent className="p-1.5 py-1">
                      <div className="flex items-center space-x-2.5">
                        <div className="flex space-x-1">
                          <div className="w-1 h-1 bg-blue-400 rounded-full animate-bounce" />
                          <div className="w-1 h-1 bg-teal-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}} />
                          <div className="w-1 h-1 bg-blue-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}} />
                        </div>
                        <span className="text-xs text-gray-400">AI is thinking...</span>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          )}
        </div>
      </div>

      {/* Modern Floating Input */}
      <div className="pb-20">
        <div className="fixed bottom-3 left-1/2 transform -translate-x-1/2 w-full max-w-3xl px-4 z-50">
          <Card className="bg-black/95 backdrop-blur-md border-gray-700 shadow-2xl rounded-full hover:shadow-blue-500/20 hover:border-blue-500/50 transition-all duration-300">
            <CardContent className="p-1 flex items-center space-x-2">
              <div className="flex-1 px-3">
                <Input
                  type="text"
                  value={currentInput}
                  onChange={(e) => setCurrentInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask about stocks, portfolio management, or financial insights..."
                  disabled={isLoading}
                  className="bg-transparent border-none text-white placeholder:text-gray-500 focus-visible:ring-0 shadow-none h-7 text-sm hover:placeholder:text-gray-400 transition-colors duration-300"
                />
              </div>

              <div className="flex items-center space-x-2 pr-1">
                {isLoading ? (
                  <div className="flex space-x-1 px-2">
                    <div className="w-1 h-1 bg-blue-400 rounded-full animate-bounce" />
                    <div className="w-1 h-1 bg-teal-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}} />
                    <div className="w-1 h-1 bg-blue-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}} />
                  </div>
                ) : (
                  currentInput.trim() && (
                    <Button
                      onClick={handleSend}
                      size="sm"
                      className="h-6 w-6 rounded-full p-0 bg-gradient-to-r from-blue-500 to-teal-600 hover:from-blue-600 hover:to-teal-700 shadow-lg hover:shadow-xl hover:shadow-blue-500/30 transition-all duration-300"
                    >
                      <Send size={10} />
                    </Button>
                  )
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
