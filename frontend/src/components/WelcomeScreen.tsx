'use client'

import { Shield, FileText, HelpCircle, TrendingUp } from 'lucide-react'

interface WelcomeScreenProps {
  onExampleClick: (message: string) => void
}

const examples = [
  {
    icon: Shield,
    title: 'Productos disponibles',
    question: 'Lista todos los seguros de GNP',
  },
  {
    icon: FileText,
    title: 'Requisitos',
    question: '¿Cuáles son los requisitos para cambio de contratante?',
  },
  {
    icon: HelpCircle,
    title: 'Definiciones',
    question: '¿Qué es el coaseguro y cuándo aplica?',
  },
  {
    icon: TrendingUp,
    title: 'Coberturas',
    question: '¿Qué coberturas incluyen los padecimientos catastróficos?',
  },
]

export default function WelcomeScreen({ onExampleClick }: WelcomeScreenProps) {
  return (
    <div className="h-full overflow-y-auto">
      <div className="min-h-full flex items-center justify-center p-4 sm:p-6 md:p-8">
        <div className="w-full max-w-4xl space-y-6 sm:space-y-8 md:space-y-12 animate-fadeIn">
          {/* Welcome Header */}
          <div className="text-center space-y-3 sm:space-y-4">
            <div className="w-16 h-16 sm:w-20 sm:h-20 mx-auto gradient-primary rounded-2xl sm:rounded-3xl flex items-center justify-center shadow-lg">
              <Shield className="w-8 h-8 sm:w-10 sm:h-10 text-white" />
            </div>
            
            <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold gradient-primary bg-clip-text text-transparent px-4">
              ¡Hola! Soy SOIA
            </h1>
            
            <p className="text-base sm:text-lg md:text-xl text-primary/70 max-w-2xl mx-auto px-4">
              Tu asistente virtual de Consolida Capital. Estoy aquí para ayudarte con información sobre productos y servicios de GNP.
            </p>
            
            <div className="inline-flex items-center gap-2 px-3 sm:px-4 py-2 rounded-full bg-accent/10 text-accent text-xs sm:text-sm font-medium">
              <Shield className="w-3 h-3 sm:w-4 sm:h-4 flex-shrink-0" />
              <span className="whitespace-nowrap">Exclusivo para agentes de Consolida Capital</span>
            </div>
          </div>

          {/* Example Questions */}
          <div className="px-4">
            <h2 className="text-base sm:text-lg font-semibold text-primary/80 mb-3 sm:mb-4 text-center">
              Ejemplos de preguntas:
            </h2>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
              {examples.map((example, index) => {
                const Icon = example.icon
                return (
                  <button
                    key={index}
                    onClick={() => onExampleClick(example.question)}
                    className="card p-4 sm:p-6 hover:shadow-xl transition-all duration-200 hover:scale-105 text-left group"
                  >
                    <div className="flex items-start gap-3 sm:gap-4">
                      <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-lg sm:rounded-xl bg-accent/10 group-hover:bg-accent transition-colors flex items-center justify-center flex-shrink-0">
                        <Icon className="w-5 h-5 sm:w-6 sm:h-6 text-accent group-hover:text-white transition-colors" />
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <h3 className="font-semibold text-sm sm:text-base text-primary mb-1 group-hover:text-accent transition-colors">
                          {example.title}
                        </h3>
                        <p className="text-xs sm:text-sm text-primary/60 line-clamp-2">
                          {example.question}
                        </p>
                      </div>
                    </div>
                  </button>
                )
              })}
            </div>
          </div>

          {/* Info Footer */}
          <div className="text-center space-y-2 px-4 pb-4">
            <p className="text-xs sm:text-sm text-primary/60">
              Puedo ayudarte con:
            </p>
            <div className="flex flex-wrap justify-center gap-2">
              <span className="px-2 sm:px-3 py-1 rounded-full bg-primary/5 text-xs text-primary/70 whitespace-nowrap">
                Información de productos
              </span>
              <span className="px-2 sm:px-3 py-1 rounded-full bg-primary/5 text-xs text-primary/70 whitespace-nowrap">
                Requisitos y procedimientos
              </span>
              <span className="px-2 sm:px-3 py-1 rounded-full bg-primary/5 text-xs text-primary/70 whitespace-nowrap">
                Coberturas y beneficios
              </span>
              <span className="px-2 sm:px-3 py-1 rounded-full bg-primary/5 text-xs text-primary/70 whitespace-nowrap">
                Gestión de pólizas
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
