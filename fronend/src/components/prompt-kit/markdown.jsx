import React from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { cn } from '@/lib/utils'

export function Markdown({ children, className, components = {} }) {
  const defaultComponents = {
    h1: ({ children }) => (
      <h1 className="my-6 text-2xl font-black uppercase italic tracking-tighter text-primary/90 text-glow border-b border-primary/10 pb-2">
        {children}
      </h1>
    ),
    h2: ({ children }) => (
      <h2 className="my-4 text-lg font-bold uppercase italic tracking-tight text-primary/80 border-l-2 border-primary/30 pl-3">
        {children}
      </h2>
    ),
    h3: ({ children }) => (
      <h3 className="my-3 text-base font-bold text-primary/70">{children}</h3>
    ),
    p: ({ children }) => (
      <p className="my-3 leading-relaxed text-primary/90 font-medium">
        {children}
      </p>
    ),
    a: ({ children, href }) => (
      <a
        href={href}
        target="_blank"
        rel="noopener noreferrer"
        className="text-primary underline underline-offset-4 hover:text-primary-foreground hover:bg-primary transition-colors px-1 rounded"
      >
        {children}
      </a>
    ),
    blockquote: ({ children }) => (
      <blockquote className="my-4 border-l-4 border-primary/40 pl-4 italic bg-primary/5 py-2 rounded-r-lg">
        {children}
      </blockquote>
    ),
    ul: ({ children }) => (
      <ul className="my-4 list-none space-y-3 ml-2">
        {children}
      </ul>
    ),
    ol: ({ children }) => (
      <ol className="my-4 list-decimal space-y-3 ml-6 text-primary/80 marker:text-primary marker:font-bold">
        {children}
      </ol>
    ),
    li: ({ children }) => (
      <li className="flex items-start gap-2.5">
        <span className="mt-[0.6em] h-1.5 w-1.5 shrink-0 rounded-full bg-primary/60 shadow-[0_0_8px_oklch(0.7_0.2_200)]" />
        <span className="flex-1 leading-relaxed">{children}</span>
      </li>
    ),
    code: ({ node, inline, className, children, ...props }) => {
      const match = /language-(\w+)/.exec(className || '')
      return !inline ? (
        <div className="relative group my-6">
          <div className="absolute -inset-2 bg-gradient-to-r from-primary/10 to-primary/5 rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity" />
          <div className="relative bg-black/60 border border-primary/20 rounded-xl overflow-hidden backdrop-blur-3xl shadow-2xl">
            <div className="flex items-center justify-between px-4 py-2 bg-primary/10 border-b border-primary/10">
              <span className="text-[10px] font-black uppercase tracking-widest text-primary/60 italic font-mono">
                {match ? match[1] : 'terminal'}
              </span>
              <div className="flex gap-1.5">
                <div className="w-2 h-2 rounded-full bg-red-500/50" />
                <div className="w-2 h-2 rounded-full bg-yellow-500/50" />
                <div className="w-2 h-2 rounded-full bg-green-500/50" />
              </div>
            </div>
            <pre className="p-4 overflow-x-auto text-sm font-mono text-primary/90 selection:bg-primary/30">
              <code className={cn("inline-block min-w-full", className)} {...props}>
                {children}
              </code>
            </pre>
          </div>
        </div>
      ) : (
        <code className="bg-primary/20 text-primary px-1.5 py-0.5 rounded font-mono text-[0.85em] border border-primary/20 mx-0.5" {...props}>
          {children}
        </code>
      )
    },
    table: ({ children }) => (
      <div className="my-6 overflow-x-auto rounded-xl border border-primary/20 bg-primary/5 backdrop-blur-3xl">
        <table className="w-full text-sm text-left border-collapse">
          {children}
        </table>
      </div>
    ),
    th: ({ children }) => (
      <th className="px-4 py-3 bg-primary/10 text-primary uppercase text-[10px] font-black tracking-widest italic border-b border-primary/20 font-mono">
        {children}
      </th>
    ),
    td: ({ children }) => (
      <td className="px-4 py-3 border-b border-primary/10 text-primary/80">
        {children}
      </td>
    ),
  }

  return (
    <div className={cn('markdown-content prose-invert max-w-none text-primary/90', className)}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{ ...defaultComponents, ...components }}
      >
        {children}
      </ReactMarkdown>
    </div>
  )
}
