'use client'

import { useEffect, useRef } from 'react'
import MessageBubble from './MessageBubble'
import TypingIndicator from './TypingIndicator'
import type { ChatMessage } from '@/lib/api'

interface ChatMessagesProps {
  messages: ChatMessage[]
  isLoading: boolean
}

export default function ChatMessages({ messages, isLoading }: ChatMessagesProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, isLoading])

  return (
    <div 
      ref={containerRef}
      className="h-full overflow-y-auto px-3 sm:px-4 md:px-6 py-4 sm:py-6"
    >
      <div className="max-w-4xl mx-auto space-y-4 sm:space-y-6">
        {messages.map((message, index) => (
          <MessageBubble key={index} message={message} />
        ))}
        
        {isLoading && <TypingIndicator />}
        
        <div ref={messagesEndRef} />
      </div>
    </div>
  )
}
