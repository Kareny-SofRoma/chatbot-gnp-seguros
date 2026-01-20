'use client'

import { useState, useRef, useEffect } from 'react'
import { Send } from 'lucide-react'

interface ChatInputProps {
  onSendMessage: (message: string) => void
  disabled?: boolean
}

export default function ChatInput({ onSendMessage, disabled }: ChatInputProps) {
  const [message, setMessage] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px'
    }
  }, [message])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (message.trim() && !disabled) {
      onSendMessage(message.trim())
      setMessage('')
      
      // Reset textarea height
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto'
      }
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    // Enter sin Shift = enviar (solo en desktop)
    if (e.key === 'Enter' && !e.shiftKey && window.innerWidth >= 640) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <div className="w-full bg-background border-t border-border">
      <div className="max-w-4xl mx-auto px-3 sm:px-4 md:px-6 py-3 sm:py-4">
        <form onSubmit={handleSubmit} className="relative">
          <div className="flex gap-2 items-end">
            {/* Textarea con fondo blanco y bordes definidos */}
            <div className="flex-1 relative">
              <textarea
                ref={textareaRef}
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Escribe tu pregunta aquí..."
                disabled={disabled}
                rows={1}
                className="w-full resize-none rounded-xl sm:rounded-2xl border-2 border-gray-300 bg-white px-3 sm:px-4 md:px-6 py-3 sm:py-4 text-sm sm:text-base text-primary placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-accent focus:border-accent disabled:opacity-50 disabled:cursor-not-allowed disabled:bg-gray-50 transition-all duration-200 max-h-32 overflow-y-auto shadow-sm hover:border-gray-400 focus:shadow-md"
                style={{
                  minHeight: '44px', // Mínimo para touch targets
                }}
              />
            </div>

            {/* Botón enviar */}
            <button
              type="submit"
              disabled={disabled || !message.trim()}
              className="flex-shrink-0 w-11 h-11 sm:w-12 sm:h-12 rounded-xl sm:rounded-2xl gradient-primary text-white flex items-center justify-center hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-lg hover:shadow-xl active:scale-95"
            >
              <Send className="w-4 h-4 sm:w-5 sm:h-5" />
            </button>
          </div>

          {/* Hint text - solo en desktop */}
          <p className="hidden sm:block text-xs text-primary/40 mt-2 text-center">
            Presiona Enter para enviar, Shift + Enter para nueva línea
          </p>
        </form>
      </div>
    </div>
  )
}
