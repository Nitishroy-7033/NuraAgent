import { Routes, Route, NavLink, Link, useLocation } from 'react-router-dom'
import { Provider, useSelector } from 'react-redux'
import store from './store'
import { 
  Settings, 
  MessageSquare, 
  Terminal, 
  Cpu, 
  LayoutGrid 
} from 'lucide-react'

// Page Imports
import ChatPage from './pages/Chat'
import AgentsPage from './pages/Agents'
import SettingsPage from './pages/Settings'
import { Loader } from './components/prompt-kit/loader'

import './App.css'

function AppContent() {
  const systemState = useSelector((state) => state.chat.systemState)
  const location = useLocation()

  const navLinks = [
    { to: '/', label: 'Neural Link', icon: MessageSquare, id: 'chat' },
    { to: '/agents', label: 'Agent Hub', icon: LayoutGrid, id: 'agents' },
    { to: '/settings', label: 'Sys Control', icon: Settings, id: 'settings' },
  ]

  return (
    <div className="flex flex-col h-screen w-screen bg-background text-foreground selection:bg-primary/30 selection:text-primary overflow-hidden relative">
      {/* Global HUD Flourishes */}
      <div className="fixed inset-0 pointer-events-none z-[100] overflow-hidden">
        <div className="absolute top-2 left-6 text-[8px] font-mono text-primary/20 tracking-[0.4em] uppercase">System_Active // Port_8080</div>
        <div className="absolute bottom-4 right-6 text-[8px] font-mono text-primary/20 tracking-[0.4em] uppercase">Nera_Core // v8.0.42</div>
        <div className="absolute top-1/2 left-2 w-1 h-32 bg-primary/5 rounded-full -translate-y-1/2" />
        <div className="absolute top-1/2 right-2 w-1 h-32 bg-primary/5 rounded-full -translate-y-1/2" />
        <div className="scanline opacity-5" />
      </div>

      {/* 1. TOP NAVBAR - Persistent across views */}
      <header className="h-12 border-b border-primary/10 flex items-center justify-between px-6 bg-black/80 backdrop-blur-3xl shadow-[0_4px_30px_rgba(0,0,0,0.5)] z-50 shrink-0">
        <div className="flex items-center gap-6 h-full">
          <Link to="/" className="flex items-center gap-2.5 cursor-pointer group pr-4 border-r border-primary/10">
            <Cpu size={18} className="text-glow animate-pulse text-primary" />
            <span className="font-bold text-lg tracking-tighter text-glow uppercase italic text-primary">NeraAgent</span>
          </Link>

          <nav className="flex items-center gap-1 h-full">
            {navLinks.map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                className={({ isActive }) => `flex items-center gap-2 px-4 h-full border-b transition-all relative ${
                  isActive 
                  ? 'border-primary text-primary bg-primary/5' 
                  : 'border-transparent text-primary/40 hover:text-primary/60 hover:bg-white/5'
                }`}
              >
                <link.icon size={14} />
                <span className="text-[10px] font-black uppercase tracking-[0.15em] italic">{link.label}</span>
                {location.pathname === link.to && (
                  <div className="absolute bottom-[-1px] left-0 w-full h-[1.5px] bg-primary shadow-[0_0_8px_oklch(0.7_0.2_200)]" />
                )}
              </NavLink>
            ))}
          </nav>
        </div>
        
        <div className="flex items-center gap-5">
          <div className="hidden lg:flex flex-col items-end mr-1">
             <div className="flex items-center gap-1.5">
                {systemState === 'Processing' ? (
                  <Loader variant="terminal" className="scale-75 origin-right" />
                ) : (
                  <>
                    <div className="w-1.5 h-1.5 rounded-full bg-primary animation-pulse" />
                    <span className="text-[9px] font-mono text-primary text-glow uppercase tracking-wider">{systemState}</span>
                  </>
                )}
              </div>
              <span className="text-[7px] font-bold text-primary/40 uppercase tracking-[0.2em] font-mono leading-none">Net_v8.0</span>
          </div>
          <div className="h-6 w-[1px] bg-primary/10" />
          <span className="text-xs font-mono text-primary/80 tracking-widest">{new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
        </div>
      </header>

      {/* 2. DYNAMIC PAGE CONTENT - Changes completely based on route */}
      <main className="flex-1 flex overflow-hidden">
        <Routes>
          <Route path="/" element={<ChatPage />} />
          <Route path="/agents" element={<AgentsPage />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="/terminal" element={
            <div className="flex-1 flex items-center justify-center bg-black/90 tech-grid">
               <div className="text-center space-y-4">
                 <div className="w-20 h-20 rounded-full border-2 border-primary/20 flex items-center justify-center mx-auto">
                    <Terminal className="text-primary animate-pulse" size={40} />
                 </div>
                 <h2 className="text-primary text-2xl font-black italic uppercase tracking-widest">Access Restricted</h2>
                 <p className="text-primary/40 font-mono text-xs">Waiting for admin authentication protocol...</p>
               </div>
            </div>
          } />
        </Routes>
      </main>
    </div>
  )
}

function App() {
  return (
    <Provider store={store}>
      <AppContent />
    </Provider>
  )
}

export default App
