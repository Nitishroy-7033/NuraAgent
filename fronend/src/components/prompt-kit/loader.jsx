import React from 'react'
import { Terminal } from 'lucide-react'

const LoaderVariants = {
  circular: () => (
    <div className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" />
  ),
  classic: () => (
    <div className="flex gap-1">
      {[0, 1, 2].map((i) => (
        <div key={i} className="h-2 w-2 animate-bounce rounded-full bg-primary" style={{ animationDelay: `${i * 150}ms` }} />
      ))}
    </div>
  ),
  pulse: () => (
    <div className="h-4 w-4 animate-ping rounded-full bg-primary" />
  ),
  'pulse-dot': () => (
    <div className="relative flex h-3 w-3 items-center justify-center">
      <div className="absolute h-full w-full animate-ping rounded-full bg-primary/40 opacity-75" />
      <div className="relative h-1.5 w-1.5 rounded-full bg-primary" />
    </div>
  ),
  dots: () => (
    <div className="flex gap-1">
      {[0, 1, 2].map((i) => (
        <div key={i} className="h-1.5 w-1.5 animate-pulse rounded-full bg-primary" style={{ animationDelay: `${i * 200}ms` }} />
      ))}
    </div>
  ),
  typing: () => (
    <div className="flex items-center gap-0.5 px-1 py-1 bg-primary/10 rounded-md border border-primary/20">
      <div className="h-1 w-1 rounded-full bg-primary animate-pulse" />
      <div className="h-1 w-1 rounded-full bg-primary animate-pulse [animation-delay:200ms]" />
      <div className="h-1 w-1 rounded-full bg-primary animate-pulse [animation-delay:400ms]" />
    </div>
  ),
  wave: () => (
    <div className="flex h-4 items-end gap-1">
      {[0, 1, 2, 3].map((i) => (
        <div 
          key={i} 
          className="w-1.5 bg-primary rounded-full animate-[loading-wave_1s_ease-in-out_infinite]" 
          style={{ animationDelay: `${i * 100}ms`, height: '40%' }} 
        />
      ))}
    </div>
  ),
  bars: () => (
    <div className="flex items-center gap-1">
      {[0, 1, 2].map((i) => (
        <div key={i} className="h-4 w-1 animate-scale-y rounded-full bg-primary" style={{ animationDelay: `${i * 150}ms` }} />
      ))}
    </div>
  ),
  terminal: () => (
    <div className="flex items-center gap-2 font-mono text-[10px] text-primary bg-primary/5 px-2 py-1 rounded border border-primary/20">
      <Terminal size={10} className="animate-pulse" />
      <span className="animate-pulse">_</span>
      <span className="opacity-60 uppercase tracking-tighter">Processing...</span>
    </div>
  ),
  'text-blink': () => (
    <span className="text-primary animate-pulse uppercase tracking-[0.2em] font-black italic text-[9px]">
      Loading...
    </span>
  ),
  'text-shimmer': () => (
    <span className="bg-gradient-to-r from-primary/20 via-primary to-primary/20 bg-[length:200%_100%] animate-shimmer bg-clip-text text-transparent uppercase tracking-widest font-bold text-[10px]">
      Synchronizing
    </span>
  ),
  'loading-dots': () => (
    <div className="flex gap-1">
      <div className="h-1.5 w-1.5 rounded-full bg-primary animate-[loading-dot_1.4s_infinite_ease-in-out_both]" />
      <div className="h-1.5 w-1.5 rounded-full bg-primary animate-[loading-dot_1.4s_infinite_ease-in-out_both_-0.32s]" />
      <div className="h-1.5 w-1.5 rounded-full bg-primary animate-[loading-dot_1.4s_infinite_ease-in-out_both_-0.16s]" />
    </div>
  ),
}

export const Loader = ({ variant = 'circular', className = '' }) => {
  const Component = LoaderVariants[variant] || LoaderVariants.circular
  return (
    <div className={`flex items-center justify-center ${className}`}>
      <Component />
    </div>
  )
}
