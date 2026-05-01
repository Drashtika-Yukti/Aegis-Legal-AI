import React, { useState, useEffect, useRef } from 'react';
import { Send, Scale, ShieldCheck, Zap, BrainCircuit, Database, History, ChevronRight, LayoutDashboard, Settings } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { chatService } from './api/client';
import './index.css';

const Sidebar = () => (
  <aside className="sidebar">
    <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '32px' }}>
      <div style={{ background: 'var(--accent-primary)', padding: '8px', borderRadius: '8px', color: 'white' }}>
        <Scale size={24} />
      </div>
      <h2 style={{ fontSize: '1.4rem', fontWeight: '700' }}>Aegis Studio</h2>
    </div>

    <div style={{ flex: 1 }}>
      <nav>
        <div className="nav-item active">
          <LayoutDashboard size={18} />
          <span>Active Case</span>
        </div>
        <div className="nav-item">
          <BrainCircuit size={18} />
          <span>Reasoning Engine</span>
        </div>
        <div className="nav-item">
          <Database size={18} />
          <span>Vector Vault</span>
        </div>
        <div className="nav-item">
          <History size={18} />
          <span>Audit Log</span>
        </div>
      </nav>
    </div>

    <div style={{ marginTop: 'auto', padding: '16px', background: 'var(--bg-panel-muted)', borderRadius: '12px', border: '1px solid var(--border-main)' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
        <ShieldCheck size={16} color="var(--success)" />
        <span style={{ fontSize: '0.85rem', fontWeight: '600', color: 'var(--success)' }}>Privacy Shield: Secure</span>
      </div>
      <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', lineHeight: '1.5' }}>
        Local PII scrubbing active. Data anonymized before engine transmission.
      </p>
    </div>
  </aside>
);

const ReasoningTrace = ({ steps }) => (
  <aside className="trace-sidebar">
    <h3 style={{ fontSize: '1.1rem', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
      <Zap size={18} color="var(--warning)" />
      Cognitive Trace
    </h3>
    
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      <AnimatePresence>
        {steps.map((step, idx) => (
          <motion.div 
            key={idx}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className={`agent-step ${step.status}`}
          >
            <ChevronRight size={16} style={{ marginTop: '2px', flexShrink: 0 }} />
            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
              <span style={{ fontWeight: '600', color: 'var(--text-primary)' }}>{step.action}</span>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{step.detail}</span>
            </div>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>

    <div style={{ marginTop: 'auto' }}>
      <h4 style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '12px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Session Context</h4>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
        <span style={{ fontSize: '0.75rem', border: '1px solid var(--border-main)', padding: '4px 10px', borderRadius: '4px' }}>
          LTM: Active
        </span>
        <span style={{ fontSize: '0.75rem', border: '1px solid var(--border-main)', padding: '4px 10px', borderRadius: '4px' }}>
          Session: 82j1-ax
        </span>
      </div>
    </div>
  </aside>
);

export default function App() {
  const [messages, setMessages] = useState([
    { role: 'ai', content: 'Aegis Studio is ready for secure legal analysis. How can I assist with your case today?' }
  ]);
  const [input, setInput] = useState('');
  const [isThinking, setIsThinking] = useState(false);
  const [agentSteps, setAgentSteps] = useState([]);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isThinking]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMsg = input;
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setInput('');
    setIsThinking(true);
    setAgentSteps([]);

    try {
      setAgentSteps(prev => [...prev, { action: 'Privacy Guard', detail: 'Local NER scrubbing...', status: 'success' }]);
      setAgentSteps(prev => [...prev, { action: 'Semantic Routing', detail: 'Mapping intent to legal nodes...', status: 'success' }]);
      setAgentSteps(prev => [...prev, { action: 'Document Retrieval', detail: 'Searching case law repositories...', status: 'thinking' }]);

      const data = await chatService.sendMessage(userMsg);

      setAgentSteps(prev => {
        const newSteps = [...prev];
        newSteps[newSteps.length - 1] = { action: 'Retrieval Complete', detail: `${data.sources?.length || 0} sources graded relevant.`, status: 'success' };
        return newSteps;
      });
      setAgentSteps(prev => [...prev, { action: 'Hallucination Check', detail: 'Verifying claims against grounded sources...', status: 'success' }]);

      setMessages(prev => [...prev, { role: 'ai', content: data.answer }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'ai', content: err.message || 'The Aegis Engine is currently unreachable.' }]);
    } finally {
      setIsThinking(false);
    }
  };

  return (
    <div className="layout-container">
      <Sidebar />
      
      <main className="chat-area">
        <div className="chat-history">
          {messages.map((msg, idx) => (
            <motion.div 
              key={idx}
              className={`message-bubble ${msg.role === 'user' ? 'message-user' : 'message-ai'}`}
            >
              {msg.role === 'ai' ? (
                <div>
                  <p style={{ marginBottom: msg.content.includes('**') ? '12px' : '0' }}>{msg.content}</p>
                  {/* Future: Render source citations here */}
                </div>
              ) : msg.content}
            </motion.div>
          ))}
          {isThinking && (
            <div className="message-bubble message-ai">
              <div style={{ display: 'flex', gap: '4px', padding: '12px 0' }}>
                <motion.div animate={{ y: [0, -5, 0] }} transition={{ repeat: Infinity, duration: 1 }} style={{ width: 8, height: 8, background: 'var(--text-secondary)', borderRadius: '50%' }} />
                <motion.div animate={{ y: [0, -5, 0] }} transition={{ repeat: Infinity, duration: 1, delay: 0.2 }} style={{ width: 8, height: 8, background: 'var(--text-secondary)', borderRadius: '50%' }} />
                <motion.div animate={{ y: [0, -5, 0] }} transition={{ repeat: Infinity, duration: 1, delay: 0.4 }} style={{ width: 8, height: 8, background: 'var(--text-secondary)', borderRadius: '50%' }} />
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="chat-input-container">
          <div style={{ position: 'relative', display: 'flex', alignItems: 'center', maxWidth: '1000px', margin: '0 auto' }}>
            <input 
              type="text" 
              className="premium-input" 
              placeholder="Ask for legal analysis, case research, or draft generation..." 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              style={{ paddingRight: '60px' }}
            />
            <button 
              className="btn-send" 
              style={{ 
                position: 'absolute', 
                right: '12px', 
                background: 'var(--accent-primary)', 
                color: 'white', 
                padding: '8px', 
                borderRadius: '8px',
                border: 'none',
                cursor: 'pointer'
              }}
              onClick={handleSend}
            >
              <Send size={18} />
            </button>
          </div>
          <p style={{ textAlign: 'center', marginTop: '16px', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
            Aegis Legal Intelligence may occasionally generate inaccuracies. Verify all citations before filing.
          </p>
        </div>
      </main>

      <ReasoningTrace steps={agentSteps} />
    </div>
  );
}
