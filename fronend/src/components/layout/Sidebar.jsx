import React from 'react'
import { cn } from "@/lib/utils"

export function Sidebar({ children, footer, className }) {
  return (
    <aside className={cn(
      "w-72 border-r bg-black/40 backdrop-blur-3xl hidden lg:flex flex-col border-primary/20 relative shrink-0",
      className
    )}>
      <div className="absolute inset-y-0 right-0 w-[1px] bg-gradient-to-b from-transparent via-primary/50 to-transparent shadow-[0_0_10px_oklch(0.7_0.2_200_/_0.5)]" />
      <div className="flex-1 overflow-y-auto p-4 space-y-6 custom-scrollbar">
        {children}
      </div>
      {footer && (
        <div className="p-4 border-t border-primary/10 bg-black/40 space-y-3">
          {footer}
        </div>
      )}
    </aside>
  )
}
