'use client'

import { Bot } from 'lucide-react'

export default function TypingIndicator() {
  return (
    <div className="flex gap-4 animate-fadeIn">
      <div className="flex-shrink-0 w-10 h-10 rounded-full gradient-primary flex items-center justify-center text-white">
        <Bot className="w-5 h-5" />
      </div>

      <div className="flex-1 max-w-3xl">
        <div className="bg-white rounded-2xl px-6 py-4 shadow-md border-2 border-background-dark inline-block">
          <div className="flex gap-2">
            <div className="w-2 h-2 bg-primary rounded-full animate-bounce [animation-delay:-0.3s]" />
            <div className="w-2 h-2 bg-primary rounded-full animate-bounce [animation-delay:-0.15s]" />
            <div className="w-2 h-2 bg-primary rounded-full animate-bounce" />
          </div>
        </div>
      </div>
    </div>
  )
}
