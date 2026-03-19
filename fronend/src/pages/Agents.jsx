import React from 'react'
import { 
  Globe, 
  Database, 
  Eye, 
  Terminal, 
  Zap, 
  Shield, 
  ChevronRight, 
  CloudLightning 
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export default function AgentsPage() {
  return (
    <div className="flex flex-1 overflow-hidden animate-in fade-in duration-500 tech-grid">
      <div className="flex-1 overflow-y-auto p-10 lg:p-20 custom-scrollbar">
        <div className="max-w-6xl mx-auto">
          <header className="mb-16 flex items-center justify-between">
            <div>
              <h1 className="text-5xl font-black italic uppercase tracking-tighter text-glow italic text-primary">Neural Agents</h1>
              <p className="text-primary/40 text-xs font-mono tracking-widest uppercase mt-1">Specialized Modular Sub-Agents</p>
            </div>
            <div className="w-16 h-16 rounded-full border border-primary/20 flex items-center justify-center">
              <CloudLightning size={32} className="text-primary animate-pulse" />
            </div>
          </header>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              { name: 'Neural Search', desc: 'Real-time extraction from planetary nets.', icon: Globe, status: 'Active' },
              { name: 'Data Architect', icon: Database, desc: 'Structure messy data into matrix schemas.', status: 'Installed' },
              { name: 'Vision X', icon: Eye, desc: 'OCR and spatial pattern recognition.', status: 'Beta' },
              { name: 'Code Weaver', icon: Terminal, desc: 'Automated script generation and debugging.', status: 'Installed' },
              { name: 'Sentience Check', icon: Zap, desc: 'Advanced reasoning and logic validator.', status: 'Active' },
              { name: 'Sentinel Shield', icon: Shield, desc: 'Threat detection and firewall maintenance.', status: 'Active' }
            ].map((item, id) => (
              <Card key={id} className="bg-primary/5 border-primary/20 backdrop-blur-xl group hover:border-primary hover:shadow-[0_0_20px_oklch(0.7_0.2_200_/_0.2)] transition-all cursor-pointer relative overflow-hidden">
                <div className="absolute top-0 right-0 w-2 h-20 bg-primary/10 translate-x-full group-hover:translate-x-[-1px] transition-transform" />
                <CardHeader className="pb-4">
                   <div className="w-16 h-16 rounded-2xl bg-primary/10 flex items-center justify-center border border-primary/20 group-hover:bg-primary/20 transition-colors mb-4">
                      {item.icon && <item.icon size={32} className="text-primary" />}
                   </div>
                   <CardTitle className="text-primary uppercase text-lg tracking-widest">{item.name}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-primary/60 text-sm mb-4 leading-relaxed">{item.desc}</p>
                   <div className="flex items-center justify-between mt-auto">
                     <span className="text-[10px] text-primary/40 font-mono tracking-widest uppercase">{item.status}</span>
                     <ChevronRight size={16} className="text-primary group-hover:translate-x-1 transition-transform" />
                   </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
