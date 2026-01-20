'use client'

import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { chatApi, type ChatMessage, type ChatResponse } from '@/lib/api'
import ChatHeader from './ChatHeader'
import ChatMessages from './ChatMessages'
import ChatInput from './ChatInput'
import WelcomeScreen from './WelcomeScreen'

export default function Chat() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [conversationId, setConversationId] = useState<string | undefined>()

  const mutation = useMutation({
    mutationFn: (message: string) =>
      chatApi.sendMessage({
        message,
        conversation_id: conversationId,
      }),
    onSuccess: (data: ChatResponse) => {
      setConversationId(data.conversation_id)
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: data.message },
      ])
    },
    onError: (error) => {
      console.error('Error sending message:', error)
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'Lo siento, ocurrió un error. Por favor intenta de nuevo.',
        },
      ])
    },
  })

  const handleSendMessage = (message: string) => {
    if (!message.trim()) return

    // Add user message to UI
    setMessages((prev) => [...prev, { role: 'user', content: message }])

    // Send to API
    mutation.mutate(message)
  }

  const handleNewChat = () => {
    setMessages([])
    setConversationId(undefined)
  }

  return (
    <div className="flex flex-col h-screen w-full overflow-hidden bg-background">
      {/* Header - altura fija */}
      <div className="flex-none">
        <ChatHeader onNewChat={handleNewChat} />
      </div>

      {/* Messages area - altura dinámica */}
      <div className="flex-1 min-h-0 overflow-hidden">
        {messages.length === 0 ? (
          <WelcomeScreen onExampleClick={handleSendMessage} />
        ) : (
          <ChatMessages messages={messages} isLoading={mutation.isPending} />
        )}
      </div>

      {/* Input area - altura fija */}
      <div className="flex-none border-t border-border bg-background">
        <ChatInput
          onSendMessage={handleSendMessage}
          disabled={mutation.isPending}
        />
      </div>
    </div>
  )
}
