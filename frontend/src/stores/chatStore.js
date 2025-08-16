import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

const useChatStore = create(devtools((set, get) => ({
  // Chat state
  messages: [],
  isLoading: false,
  currentInput: '',
  userId: localStorage.getItem('userId') || `user_${Date.now()}`,
  chatId: localStorage.getItem('chatId') || `chat_${Date.now()}`,
  
  // Chat actions
  setCurrentInput: (input) => set({ currentInput: input }),
  
  addMessage: (message) => set((state) => ({
    messages: [...state.messages, {
      id: Date.now(),
      timestamp: new Date().toISOString(),
      ...message
    }]
  })),
  
  setLoading: (loading) => set({ isLoading: loading }),
  
  clearMessages: () => set({ messages: [] }),
  
  setMessages: (messages) => set({ messages }),
  
  // Send message to backend
  sendMessage: async (content) => {
    const { userId, chatId, addMessage, setLoading, setCurrentInput } = get();
    
    // Clear input immediately and add user message
    setCurrentInput('');
    addMessage({
      role: 'user',
      content,
      userId,
      chatId
    });
    
    setLoading(true);
    
    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: content,
          user_id: userId,
          chat_id: chatId
        })
      });
      
      console.log('Response status:', response.status);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('Response data:', data);
      
      // Add assistant response
      addMessage({
        role: 'assistant',
        content: data.answer, // Fixed: backend returns 'answer' not 'response'
        userId,
        chatId
      });
      
    } catch (error) {
      console.error('Error sending message:', error);
      addMessage({
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your request.',
        userId,
        chatId,
        error: true
      });
    } finally {
      setLoading(false);
    }
  },
  
  // Load conversation history
  loadConversationHistory: async () => {
    const { userId, chatId, setMessages } = get();
    
    try {
      const response = await fetch(`http://localhost:8000/conversation/${userId}/${chatId}`);
      
      if (response.ok) {
        const data = await response.json();
        if (data.messages) {
          setMessages(data.messages);
        }
      }
    } catch (error) {
      console.error('Error loading conversation history:', error);
    }
  },
  
  // Start new chat
  startNewChat: () => {
    const newChatId = `chat_${Date.now()}`;
    localStorage.setItem('chatId', newChatId);
    set({ 
      chatId: newChatId,
      messages: []
    });
  },
  
  // Set user ID
  setUserId: (newUserId) => {
    localStorage.setItem('userId', newUserId);
    set({ userId: newUserId });
  }
})));

export default useChatStore;
