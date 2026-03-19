import React, { useRef, useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { 
  addMessages, 
  updateLastAssistantMessage, 
  setSystemState 
} from '../store/slices/chatSlice'
import { streamChat } from '../api/chat'
import { Loader } from '../components/prompt-kit/loader'
import { Markdown } from '../components/prompt-kit/markdown'
import {
  Plus,
  Send,
  Paperclip,
  Search,
  History,
  Cpu,
  User
} from 'lucide-react'
import { Button } from "@/components/ui/button"
import { Sidebar } from "@/components/layout/Sidebar"
import {
  PromptInput,
  PromptInputTextarea,
  PromptInputActions,
  PromptInputAction,
} from '@/components/ui/prompt-input'

const ChatHistoryItem = ({ title, active = false }) => (
  <div className={`p-3 rounded-xl cursor-pointer transition-all border group relative ${active ? 'bg-primary/10 border-primary/30 shadow-[0_0_15px_oklch(0.7_0.2_200_/_0.1)]' : 'bg-transparent border-transparent hover:bg-primary/5 hover:border-primary/10'}`}>
    <div className="flex items-center gap-3">
      <History size={16} className={active ? 'text-primary' : 'text-primary/40 group-hover:text-primary/60'} />
      <div className="flex flex-col overflow-hidden">
        <span className={`text-[13px] font-medium truncate tracking-tight ${active ? 'text-primary' : 'text-primary/70 group-hover:text-primary/90'}`}>{title}</span>
      </div>
    </div>
  </div>
)

export default function ChatPage() {
  const [inputValue, setInputValue] = useState('')
  const chatEndRef = useRef(null)
  
  const dispatch = useDispatch()
  const messages = useSelector((state) => state.chat.messages)
  const systemState = useSelector((state) => state.chat.systemState)

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async () => {
    if (!inputValue.trim()) return

    const userText = inputValue
    setInputValue('')
    
    // 1. Add user message
    dispatch(addMessages([{ role: 'user', content: userText }]))
    dispatch(setSystemState('Processing'))

    // 2. Add empty assistant message to be filled
    dispatch(addMessages([{ role: 'assistant', content: '' }]))

    // 3. Start streaming
    await streamChat(
      userText,
      (chunk, fullContent) => {
        // On each chunk
        dispatch(updateLastAssistantMessage(fullContent))
      },
      () => {
        // On done
        dispatch(setSystemState('Online'))
      },
      (error) => {
        // On error
        console.error('Streaming error:', error)
        dispatch(updateLastAssistantMessage(`[SYSTEM ERROR]: Neural link failed. ${error.message}`))
        dispatch(setSystemState('Online'))
      }
    )
  }

  return (
    <div className="flex flex-1 overflow-hidden">
      <Sidebar
        footer={
          <div className="flex items-center gap-3 p-3 rounded-2xl bg-primary/10 border border-primary/20">
            <div className="w-10 h-10 rounded-xl bg-primary/20 flex items-center justify-center border border-primary/30">
              <User size={20} className="text-primary" />
            </div>
            <div className="flex-1 overflow-hidden text-glow">
              <p className="text-xs font-bold text-primary uppercase tracking-wider truncate">Operator#09</p>
              <p className="text-[9px] text-primary/60 font-mono italic truncate font-black tracking-widest uppercase italic border-b border-primary/10">Secured</p>
            </div>
          </div>
        }
      >
        <div className="space-y-1">
          <div className="px-2 py-2 text-[10px] font-bold text-primary/40 uppercase tracking-[0.2em] flex items-center justify-between">
            Neural Thread Logs
            <Plus size={14} className="cursor-pointer hover:text-primary transition-colors" />
          </div>
          <ChatHistoryItem title="Neural Protocol v4" active={true} />
          <ChatHistoryItem title="System Resource Optimization" />
          <ChatHistoryItem title="Vite Pipeline Debugging" />
          <ChatHistoryItem title="Matrix Data Extraction" />
        </div>
      </Sidebar>

      <div className="flex-1 flex flex-col relative tech-grid min-w-0">
        <div className="flex-1 overflow-y-auto px-6 py-10 md:px-20 space-y-12 custom-scrollbar relative">
           <div className="noise-overlay" />
           {/* Visual Flourish: Active Line Indicator */}
           <div className="absolute left-0 top-0 bottom-0 w-[1px] bg-gradient-to-b from-primary/5 via-primary/40 to-primary/5" />
           
          {messages.map((msg, i) => (
            <div key={i} className={`flex gap-6 ${msg.role === 'user' ? 'flex-row-reverse' : ''} animate-in fade-in slide-in-from-bottom-4 duration-500 group/message`}>
              <div className={`w-12 h-12 rounded-xl flex items-center justify-center shrink-0 border-2 transition-all duration-300 ${msg.role === 'user'
                ? 'bg-primary/20 border-primary text-primary shadow-[0_0_20px_oklch(0.7_0.2_200_/_0.3)] group-hover/message:scale-110'
                : 'bg-black/80 border-primary/30 text-primary group-hover/message:border-primary group-hover/message:shadow-[0_0_15px_oklch(0.7_0.2_200_/_0.2)]'
                }`}>
                {msg.role === 'user' ? <User size={24} /> : <Cpu size={24} />}
              </div>
              <div className={`flex flex-col gap-3 max-w-[80%] ${msg.role === 'user' ? 'items-end' : ''}`}>
                <div className={`px-6 py-5 rounded-2xl text-[15px] leading-relaxed relative overflow-hidden transition-all duration-300 ${msg.role === 'user'
                  ? 'bg-gradient-to-br from-primary/20 to-primary/5 border border-primary/30 text-primary font-bold rounded-tr-none user-bubble-glow corner-bottom-left animate-in fade-in zoom-in-95'
                  : 'bg-black/40 border-2 border-primary/20 text-primary/95 backdrop-blur-3xl rounded-tl-none shadow-[inset_0_0_30px_oklch(0.7_0.2_200_/_0.05)] hover:border-primary/40 corner-top-right transition-colors'
                  }`}>
                  
                  {/* Subtle Scanline for Assistant */}
                  {msg.role === 'assistant' && (
                    <div className="absolute inset-0 bg-gradient-to-b from-transparent via-primary/5 to-transparent bg-[length:100%_4px] opacity-20 pointer-events-none" />
                  )}

                  {msg.content ? (
                    <div className="relative z-10">
                      <Markdown>{msg.content}</Markdown>
                    </div>
                  ) : (
                    <div className="flex items-center gap-2 py-2">
                      <Loader variant="terminal" />
                    </div>
                  )}
                </div>
                <div className="flex items-center gap-2 group">
                  <span className="text-[9px] text-primary/40 uppercase tracking-[0.3em] font-black italic">
                    {msg.role === 'user' ? 'OPERATOR' : 'NERA_CORE'}
                  </span>
                  <div className="h-[1px] w-8 bg-primary/10" />
                  <span className="text-[9px] text-primary/30 font-mono tracking-tighter italic">LOG_ENTRY_{i.toString().padStart(3, '0')}</span>
                </div>
              </div>
            </div>
          ))}

          {systemState === 'Processing' && messages[messages.length - 1]?.role !== 'assistant' && (
             <div className="flex gap-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
                <div className="w-12 h-12 rounded-xl flex items-center justify-center shrink-0 border-2 bg-black/80 border-primary/30 text-primary">
                  <Cpu size={24} className="animate-pulse" />
                </div>
                <div className="flex flex-col gap-3">
                  <div className="px-6 py-4 rounded-3xl text-sm md:text-base leading-relaxed relative bg-primary/5 border-2 border-primary/30 text-primary/95 backdrop-blur-3xl rounded-tl-none corner-top-right">
                    <Loader variant="terminal" />
                  </div>
                </div>
             </div>
          )}
          <div ref={chatEndRef} />
        </div>

        <div className="p-8 bg-gradient-to-t from-black via-black/80 to-transparent sticky bottom-0 z-20">
          <div className="max-w-5xl mx-auto relative">
            <div className="absolute -top-4 -left-4 w-8 h-8 border-t-2 border-l-2 border-primary/30 rounded-tl-2xl" />
            <div className="absolute -top-4 -right-4 w-8 h-8 border-t-2 border-r-2 border-primary/30 rounded-tr-2xl" />

            <PromptInput
              value={inputValue}
              onValueChange={setInputValue}
              onSubmit={handleSend}
              className="bg-black/90 border-2 border-primary/30 focus-within:border-primary focus-within:shadow-[0_0_25px_oklch(0.7_0.2_200_/_0.2)] transition-all p-4 rounded-2xl backdrop-blur-xl"
            >
              <PromptInputTextarea
                placeholder="Initialize instruction..."
                className="text-lg min-h-[50px] font-mono text-primary placeholder:text-primary/20 selection:bg-primary selection:text-primary-foreground"
              />
              <PromptInputActions className="justify-between mt-4 border-t pt-4 border-primary/10">
                <div className="flex gap-2">
                  <PromptInputAction tooltip="Upload Data Package">
                    <Button variant="ghost" size="icon" className="h-10 w-10 rounded-xl hover:bg-primary/20 text-primary/60 hover:text-primary border border-transparent hover:border-primary/20">
                      <Paperclip size={20} />
                    </Button>
                  </PromptInputAction>
                  <PromptInputAction tooltip="Search Neural Web">
                    <Button variant="ghost" size="icon" className="h-10 w-10 rounded-xl hover:bg-primary/20 text-primary/60 hover:text-primary border border-transparent hover:border-primary/20">
                      <Search size={20} />
                    </Button>
                  </PromptInputAction>
                </div>
                <div className="flex items-center gap-4">
                  <Button
                    onClick={handleSend}
                    disabled={!inputValue.trim() || systemState === 'Processing'}
                    className="rounded-2xl px-8 h-12 gap-3 bg-primary text-primary-foreground hover:bg-primary/80 shadow-[0_0_20px_oklch(0.7_0.2_200_/_0.4)] active:scale-95 transition-all uppercase font-black italic tracking-tighter text-base"
                  >
                    {systemState === 'Processing' ? 'Thinking...' : 'Send'}
                    <Send size={20} className={systemState === 'Processing' ? 'animate-pulse' : 'text-glow'} />
                  </Button>
                </div>
              </PromptInputActions>
            </PromptInput>
          </div>
        </div>
      </div>
    </div>
  )
}
