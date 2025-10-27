"""
Persona Generator using LLM for rich character creation
"""

import logging
from typing import List, Optional
import httpx

from models import PersonaGenerationRequest, PersonaGenerationResponse

logger = logging.getLogger(__name__)


class PersonaGenerator:
    """Generates rich personas from simple keywords using LLM"""
    
    def __init__(self, persona_engine_url: str):
        self.persona_engine_url = persona_engine_url
    
    async def generate_persona(
        self,
        request: PersonaGenerationRequest
    ) -> PersonaGenerationResponse:
        """
        Generate a rich persona from personality traits and hobbies
        
        Args:
            request: PersonaGenerationRequest with traits and hobbies
            
        Returns:
            PersonaGenerationResponse with generated persona
        """
        try:
            # Build the generation prompt
            prompt = self._build_generation_prompt(
                personality_traits=request.personality_traits,
                hobbies=request.hobbies,
                background_hints=request.background_hints
            )
            
            # Call LLM for generation
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.persona_engine_url}/api/chat",
                    json={
                        "message": prompt,
                        "character_id": "system",
                        "user_id": "system",
                        "stream": False
                    }
                )
                
                if response.status_code != 200:
                    logger.error(f"Persona generation failed: {response.status_code}")
                    return self._fallback_persona(request)
                
                # Extract generated persona
                generated_text = response.json().get("response", "")
                
                # Clean and format the persona
                persona_prompt = self._clean_persona_text(generated_text)
                
                logger.info("Successfully generated persona")
                
                return PersonaGenerationResponse(
                    persona_prompt=persona_prompt,
                    traits_used=request.personality_traits,
                    hobbies_used=request.hobbies
                )
                
        except Exception as e:
            logger.error(f"Persona generation error: {e}")
            return self._fallback_persona(request)
    
    def _build_generation_prompt(
        self,
        personality_traits: List[str],
        hobbies: List[str],
        background_hints: Optional[str] = None
    ) -> str:
        """Build the prompt for persona generation"""
        
        traits_str = ", ".join(personality_traits)
        hobbies_str = ", ".join(hobbies) if hobbies else "various interests"
        
        prompt = f"""You are a master character writer. Based on the following traits and hobbies, write a rich, first-person backstory and personality description for an AI character.

Personality Traits: {traits_str}
Hobbies/Interests: {hobbies_str}
{f"Additional Context: {background_hints}" if background_hints else ""}

Write a compelling 2-3 paragraph character description in FIRST PERSON that:
1. Introduces the character naturally ("I'm...")
2. Weaves in the personality traits organically
3. Mentions hobbies and interests as part of their life story
4. Includes some personal philosophy or worldview
5. Adds unique quirks or characteristics that make them memorable
6. Sounds like a real person introducing themselves

Make it engaging, authentic, and avoid clichés. The character should feel three-dimensional and relatable."""
        
        return prompt
    
    def _clean_persona_text(self, text: str) -> str:
        """Clean and format the generated persona text"""
        # Remove any potential prompt leakage
        lines = text.strip().split('\n')
        
        # Filter out meta-instructions or formatting
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            # Skip empty lines or meta-text
            if line and not line.startswith(('Write', 'Based on', 'Personality', 'Hobbies')):
                cleaned_lines.append(line)
        
        # Join with proper spacing
        cleaned_text = '\n\n'.join(cleaned_lines)
        
        # Ensure it starts naturally
        if not cleaned_text.startswith(("I'm", "I am", "My name", "Hi,", "Hello")):
            cleaned_text = "I'm " + cleaned_text
        
        return cleaned_text
    
    def _fallback_persona(self, request: PersonaGenerationRequest) -> PersonaGenerationResponse:
        """Generate a simple fallback persona if LLM fails"""
        traits_str = " and ".join(request.personality_traits[:3])
        hobbies_str = ", ".join(request.hobbies[:3]) if request.hobbies else "exploring new things"
        
        fallback_text = f"""I'm someone who values being {traits_str}. These qualities shape how I interact with the world and the people around me.

In my free time, I enjoy {hobbies_str}. These activities help me stay balanced and bring joy to my life. I believe in continuous growth and learning, always seeking new experiences and perspectives.

I approach conversations with genuine curiosity and empathy, aiming to understand and connect with others on a meaningful level."""
        
        return PersonaGenerationResponse(
            persona_prompt=fallback_text,
            traits_used=request.personality_traits,
            hobbies_used=request.hobbies
        )
