"""
Memory Extractor using LLM for intelligent fact extraction
"""

import logging
import json
from typing import Dict, List, Any
import httpx

logger = logging.getLogger(__name__)


class MemoryExtractor:
    """Extracts structured memories from conversations using LLM"""
    
    def __init__(self, persona_engine_url: str):
        self.persona_engine_url = persona_engine_url
    
    async def extract_memories(
        self,
        user_message: str,
        ai_response: str,
        user_id: str,
        character_id: str
    ) -> Dict[str, Any]:
        """
        Extract structured memories from a conversation turn
        
        Returns:
            Dictionary containing facts, entities, topics, and sentiment
        """
        try:
            # Construct extraction prompt
            extraction_prompt = f"""Analyze this conversation and extract important information.

User: {user_message}
Assistant: {ai_response}

Extract the following:
1. Key Facts: Important information about the user (preferences, events, relationships, personal info)
2. Entities: Named entities mentioned (people, places, things)
3. Topics: Main topics discussed
4. Sentiment: Overall emotional tone

Format your response as JSON:
{{
    "facts": [
        {{"type": "preference|event|relationship|personal_info|goal|habit|other", "key": "fact_name", "value": "fact_value"}}
    ],
    "entities": [
        {{"name": "entity_name", "type": "person|place|thing|organization"}}
    ],
    "topics": ["topic1", "topic2"],
    "sentiment": "positive|negative|neutral|mixed"
}}

Only extract facts that are explicitly stated or strongly implied. Be concise and accurate."""

            # Call LLM for extraction
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.persona_engine_url}/api/chat",
                    json={
                        "message": extraction_prompt,
                        "character_id": "system",
                        "user_id": "system",
                        "stream": False
                    }
                )
                
                if response.status_code != 200:
                    logger.error(f"LLM extraction failed: {response.status_code}")
                    return self._empty_extraction()
                
                # Parse LLM response
                llm_response = response.json().get("response", "{}")
                
                # Extract JSON from response
                extracted_data = self._parse_json_response(llm_response)
                
                # Validate and clean extracted data
                cleaned_data = self._validate_extraction(extracted_data)
                
                logger.info(f"Extracted {len(cleaned_data.get('facts', []))} facts from conversation")
                return cleaned_data
                
        except Exception as e:
            logger.error(f"Memory extraction failed: {e}")
            return self._empty_extraction()
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON from LLM response"""
        try:
            # Try to find JSON in the response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                # Try parsing the entire response
                return json.loads(response)
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from LLM response: {e}")
            return {}
    
    def _validate_extraction(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean extracted data"""
        validated = {
            "facts": [],
            "entities": [],
            "topics": [],
            "sentiment": "neutral"
        }
        
        # Validate facts
        if "facts" in data and isinstance(data["facts"], list):
            for fact in data["facts"]:
                if isinstance(fact, dict) and all(k in fact for k in ["type", "key", "value"]):
                    # Ensure fact values are strings and not empty
                    if fact["key"] and fact["value"]:
                        validated["facts"].append({
                            "type": str(fact["type"]).lower(),
                            "key": str(fact["key"])[:255],  # Limit key length
                            "value": str(fact["value"])
                        })
        
        # Validate entities
        if "entities" in data and isinstance(data["entities"], list):
            for entity in data["entities"]:
                if isinstance(entity, dict) and "name" in entity:
                    validated["entities"].append({
                        "name": str(entity["name"]),
                        "type": str(entity.get("type", "unknown")).lower()
                    })
        
        # Validate topics
        if "topics" in data and isinstance(data["topics"], list):
            validated["topics"] = [str(topic) for topic in data["topics"] if topic]
        
        # Validate sentiment
        if "sentiment" in data and data["sentiment"] in ["positive", "negative", "neutral", "mixed"]:
            validated["sentiment"] = data["sentiment"]
        
        return validated
    
    def _empty_extraction(self) -> Dict[str, Any]:
        """Return empty extraction result"""
        return {
            "facts": [],
            "entities": [],
            "topics": [],
            "sentiment": "neutral"
        }
