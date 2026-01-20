'use client'

import { Plus } from 'lucide-react'

interface ChatHeaderProps {
  onNewChat: () => void
}

export default function ChatHeader({ onNewChat }: ChatHeaderProps) {
  return (
    <header className="gradient-primary text-white shadow-lg">
      <div className="w-full px-3 sm:px-4 md:px-6 py-3 md:py-4">
        <div className="flex items-center justify-between gap-2 max-w-7xl mx-auto">
          {/* Logo y título */}
          <div className="flex items-center gap-2 sm:gap-3 min-w-0 flex-1">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-lg bg-white/20 flex items-center justify-center">
                <span className="text-lg sm:text-xl font-bold">S</span>
              </div>
            </div>
            
            <div className="min-w-0 flex-1">
              <h1 className="text-lg sm:text-xl md:text-2xl font-bold tracking-tight truncate">
                SOIA
              </h1>
              <p className="text-xs sm:text-sm text-white/80 truncate">
                Asistente de Consolida Capital
              </p>
            </div>
          </div>

          {/* Botón nueva conversación */}
          <button
            onClick={onNewChat}
            className="flex-shrink-0 flex items-center gap-2 px-3 sm:px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg sm:rounded-xl transition-all duration-200 backdrop-blur-sm"
          >
            <Plus className="w-4 h-4 sm:w-5 sm:h-5" />
            <span className="hidden sm:inline text-sm md:text-base">Nueva conversación</span>
            <span className="sm:hidden text-sm">Nueva</span>
          </button>
        </div>
      </div>
    </header>
  )
}
