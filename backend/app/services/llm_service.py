from anthropic import Anthropic
from app.core.config import settings
from app.core.logger import get_logger
from typing import List, Dict

logger = get_logger()

class LLMService:
    def __init__(self):
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.LLM_MODEL
        self.temperature = settings.TEMPERATURE
        self.max_tokens = settings.MAX_TOKENS
    
    def generate_response(
        self,
        user_message: str,
        context: str = "",
        conversation_history: List[Dict] = None
    ) -> tuple[str, int]:
        """
        Generate response using Claude
        Returns: (response_text, tokens_used)
        """
        try:
            # Build system prompt with context
            system_prompt = self._build_system_prompt(context)
            
            # Build messages
            messages = []
            if conversation_history:
                messages.extend(conversation_history)
            messages.append({
                "role": "user",
                "content": user_message
            })
            
            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_prompt,
                messages=messages
            )
            
            response_text = response.content[0].text
            tokens_used = response.usage.input_tokens + response.usage.output_tokens
            
            logger.info(f"Generated response with {tokens_used} tokens")
            
            return response_text, tokens_used
            
        except Exception as e:
            logger.error(f"Error generating LLM response: {str(e)}")
            raise
    
    def _build_system_prompt(self, context: str = "") -> str:
        """Build system prompt for the chatbot"""
        base_prompt = """Eres un asistente inteligente especializado en seguros de GNP (Grupo Nacional Provincial).
Tu objetivo es ayudar a los agentes de seguros a responder preguntas sobre los productos y manuales de GNP.

INSTRUCCIONES IMPORTANTES:
1. Responde SIEMPRE en español de México
2. Sé preciso y conciso en tus respuestas
3. Si tienes contexto de los manuales, úsalo para dar respuestas exactas
4. Si NO tienes información suficiente, di claramente que no tienes esa información específica
5. Mantén un tono profesional pero amigable
6. Cita las fuentes cuando sea posible (número de página, sección del manual)
7. Si la pregunta no está relacionada con seguros o GNP, redirige educadamente

FORMATO DE RESPUESTA:
- Párrafos cortos y fáciles de leer
- Usa listas numeradas o bullets cuando sea apropiado
- Resalta información clave
- Incluye ejemplos prácticos cuando ayude"""

        if context:
            base_prompt += f"\n\nCONTEXTO DE LOS MANUALES:\n{context}"
        
        return base_prompt

llm_service = LLMService()
