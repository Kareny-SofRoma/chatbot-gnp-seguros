'use client'

import { Bot, User } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import type { ChatMessage } from '@/lib/api'

interface MessageBubbleProps {
  message: ChatMessage
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user'

  return (
    <div className={`flex gap-2 sm:gap-3 md:gap-4 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
      {/* Avatar */}
      <div className="flex-shrink-0">
        <div
          className={`w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl flex items-center justify-center ${
            isUser
              ? 'bg-accent text-white'
              : 'gradient-primary text-white'
          }`}
        >
          {isUser ? (
            <User className="w-4 h-4 sm:w-5 sm:h-5" />
          ) : (
            <Bot className="w-4 h-4 sm:w-5 sm:h-5" />
          )}
        </div>
      </div>

      {/* Message content */}
      <div className={`flex-1 min-w-0 ${isUser ? 'flex justify-end' : ''}`}>
        <div
          className={`inline-block max-w-full sm:max-w-[85%] md:max-w-[80%] rounded-2xl px-3 sm:px-4 md:px-6 py-3 sm:py-4 ${
            isUser
              ? 'bg-accent text-white'
              : 'card border border-border'
          }`}
        >
          <div className={`prose prose-sm sm:prose-base max-w-none ${
            isUser 
              ? 'prose-invert prose-p:text-white prose-headings:text-white prose-strong:text-white prose-li:text-white' 
              : 'prose-primary'
          }`}>
            <ReactMarkdown
              components={{
                // Párrafos
                p: ({ children }) => (
                  <p className="text-sm sm:text-base leading-relaxed mb-3 last:mb-0 break-words">
                    {children}
                  </p>
                ),
                // Listas con viñetas
                ul: ({ children }) => (
                  <ul className="space-y-1.5 sm:space-y-2 my-3 ml-4 sm:ml-5 list-disc">
                    {children}
                  </ul>
                ),
                // Listas numeradas
                ol: ({ children }) => (
                  <ol className="space-y-1.5 sm:space-y-2 my-3 ml-4 sm:ml-5 list-decimal">
                    {children}
                  </ol>
                ),
                // Items de lista
                li: ({ children }) => (
                  <li className="text-sm sm:text-base leading-relaxed break-words">
                    {children}
                  </li>
                ),
                // Títulos
                h1: ({ children }) => (
                  <h1 className="text-lg sm:text-xl md:text-2xl font-bold mb-3 mt-4 first:mt-0 break-words">
                    {children}
                  </h1>
                ),
                h2: ({ children }) => (
                  <h2 className="text-base sm:text-lg md:text-xl font-bold mb-2 mt-3 first:mt-0 break-words">
                    {children}
                  </h2>
                ),
                h3: ({ children }) => (
                  <h3 className="text-sm sm:text-base md:text-lg font-semibold mb-2 mt-3 first:mt-0 break-words">
                    {children}
                  </h3>
                ),
                // Negrita
                strong: ({ children }) => (
                  <strong className="font-bold break-words">
                    {children}
                  </strong>
                ),
                // Código
                code: ({ children, className }) => {
                  const isInline = !className
                  if (isInline) {
                    return (
                      <code className="px-1.5 py-0.5 rounded bg-primary/5 text-sm font-mono break-all">
                        {children}
                      </code>
                    )
                  }
                  return (
                    <code className="block p-3 sm:p-4 rounded-lg bg-primary/5 text-xs sm:text-sm font-mono overflow-x-auto">
                      {children}
                    </code>
                  )
                },
                // Bloques de código
                pre: ({ children }) => (
                  <pre className="my-3 overflow-x-auto">
                    {children}
                  </pre>
                ),
                // Links
                a: ({ children, href }) => (
                  <a
                    href={href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-accent hover:underline break-all"
                  >
                    {children}
                  </a>
                ),
              }}
            >
              {message.content}
            </ReactMarkdown>
          </div>
        </div>
      </div>
    </div>
  )
}
