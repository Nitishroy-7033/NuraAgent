import React from 'react'
import {
  Activity,
  Lock,
  HardDrive,
  ChevronRight
} from 'lucide-react'
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

export default function SettingsPage() {
  return (
    <div className="flex flex-1 overflow-hidden animate-in fade-in duration-500 bg-black/60 backdrop-blur-3xl">
      {/* Settings Sidebar */}
      <aside className="w-80 border-r border-primary/10 hidden md:flex flex-col p-6 space-y-6">
        <div className="space-y-1">
          <h2 className="px-2 pb-2 text-[10px] font-bold text-primary/40 uppercase tracking-[0.2em]">Config Sectors</h2>
          {['General', 'Intelligence', 'Security', 'Interface', 'Advanced'].map((cat) => (
            <Button key={cat} variant="ghost" className={`w-full justify-start gap-3 rounded-xl uppercase text-[10px] tracking-widest font-black italic ${cat === 'General' ? 'bg-primary/10 text-primary' : 'text-primary/40 hover:text-primary/60'}`}>
              {cat === 'General' ? <Activity size={14} /> : <div className="w-1.5 h-1.5 bg-primary/20 rounded-full" />}
              {cat}
            </Button>
          ))}
        </div>
      </aside>

      <div className="flex-1 overflow-y-auto p-10 lg:p-20 custom-scrollbar">
        <div className="max-w-4xl mx-auto space-y-12">
          <header>
            <h1 className="text-5xl font-black italic uppercase tracking-tighter text-primary text-glow italic">System Configuration</h1>
            <p className="text-primary/40 text-xs font-mono tracking-widest uppercase mt-2">Modify NeraAgent Internal Protocols</p>
          </header>

          <div className="space-y-8">
            <section className="space-y-4">
              <h3 className="text-primary font-bold uppercase tracking-widest text-sm flex items-center gap-2">
                <Activity size={16} /> Identity Core
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 rounded-xl bg-primary/5 border border-primary/10 space-y-2">
                  <label className="text-[10px] text-primary/40 uppercase font-black italic">Agent Designation</label>
                  <input className="w-full bg-transparent border-none text-primary font-bold text-lg focus:outline-none" defaultValue="NeraAgent" />
                </div>
                <div className="p-4 rounded-xl bg-primary/5 border border-primary/10 space-y-2">
                  <label className="text-[10px] text-primary/40 uppercase font-black italic">Language Matrix</label>
                  <div className="flex items-center justify-between">
                    <span className="text-primary font-bold">English (UK) - Jarvis V4</span>
                    <ChevronRight size={16} className="text-primary/40" />
                  </div>
                </div>
              </div>
            </section>

            <section className="space-y-4">
              <h3 className="text-primary font-bold uppercase tracking-widest text-sm flex items-center gap-2">
                <Lock size={16} /> Neural Security
              </h3>
              <Card className="bg-primary/5 border-primary/20">
                <CardContent className="p-6 space-y-4">
                  <div className="flex items-center justify-between p-4 rounded-xl bg-black/40 border border-primary/10">
                    <div>
                      <p className="text-sm font-bold text-primary uppercase">Biometric Link</p>
                      <p className="text-xs text-primary/40">Requires operator iris verification</p>
                    </div>
                    <div className="w-12 h-6 bg-primary/20 rounded-full flex items-center px-1 border border-primary/30">
                      <div className="w-4 h-4 bg-primary rounded-full shadow-[0_0_8px_oklch(0.7_0.2_200)] ml-auto" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </section>
          </div>
        </div>
      </div>
    </div>
  )
}
