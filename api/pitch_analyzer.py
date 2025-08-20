from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from dotenv import load_dotenv
from .schema import PitchFeedback
from .config import settings
from .logger import logger
from .exceptions import AnalysisError
import time
import uuid
from typing import Dict, Any

load_dotenv()



class PitchAnalyzer:
    def __init__(self):
        self.llm = ChatOpenAI(
            model_name=settings.openai_model,
            temperature=0,
            max_tokens=4000,
            request_timeout=60
        )
        self.parser = PydanticOutputParser(pydantic_object=PitchFeedback)
        self._load_prompt_template()
    
    def _load_prompt_template(self):
        """Load and prepare the prompt template"""
        try:
            with open("prompt/prompt.txt", "r", encoding="utf-8") as file:
                base_prompt = file.read()
        except FileNotFoundError:
            logger.error("Prompt template file not found")
            raise AnalysisError("Prompt template configuration error")
        except Exception as e:
            logger.error(f"Error loading prompt template: {e}")
            raise AnalysisError("Failed to load analysis configuration")
        
        # Enhanced prompt with additional instructions
        enhanced_prompt = base_prompt + """

Additional Analysis Requirements:
- Provide content statistics (word count, sentence count, paragraph count)
- Identify top 3 risk factors
- List top 3 strengths
- Ensure all scores are between 0-100
- Be specific and actionable in feedback
- Include analysis_id and processing metadata

Pitch deck content:
{pitch}

Respond ONLY in JSON format:
{format_instructions}
"""
        
        self.prompt = PromptTemplate(
            template=enhanced_prompt,
            input_variables=["pitch"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )
    
    def _calculate_content_stats(self, content: str) -> Dict[str, Any]:
        """Calculate basic content statistics"""
        words = len(content.split())
        sentences = len([s for s in content.split('.') if s.strip()])
        paragraphs = len([p for p in content.split('\n\n') if p.strip()])
        characters = len(content)
        
        return {
            "word_count": words,
            "sentence_count": sentences,
            "paragraph_count": paragraphs,
            "character_count": characters,
            "average_words_per_sentence": round(words / max(sentences, 1), 2),
            "reading_time_minutes": round(words / 200, 1)  # Assuming 200 words per minute
        }
    

    async def analyze_pitch(self, pitch_content: str) -> dict:
        """Analyze pitch content and return structured feedback"""
        start_time = time.time()
        analysis_id = str(uuid.uuid4())
        
        logger.info(f"Starting pitch analysis {analysis_id}")
        
        try:
            # Calculate content statistics
            content_stats = self._calculate_content_stats(pitch_content)
            logger.debug(f"Content stats: {content_stats}")
            
            # Create the chain and invoke analysis
            chain = self.prompt | self.llm | self.parser
            
            logger.debug("Invoking AI analysis chain")
            result = await chain.ainvoke({"pitch": pitch_content})
            
            # Add metadata
            result.analysis_id = analysis_id
            result.processing_time = round(time.time() - start_time, 2)
            result.content_statistics = content_stats
            
            logger.info(f"Analysis {analysis_id} completed in {result.processing_time}s")
            
            return result.dict()
            
        except Exception as e:
            processing_time = round(time.time() - start_time, 2)
            logger.error(f"Analysis {analysis_id} failed after {processing_time}s: {str(e)}")
            raise AnalysisError(f"AI analysis failed: {str(e)}")

pitch_analyzer = PitchAnalyzer()
















# llm = ChatOpenAI(model_name="gpt-4.1")
# parser = PydanticOutputParser(pydantic_object=PitchFeedback)

# async def analyze_pitch(pitch: str) -> dict:
    
#     with open("prompt/prompt.txt", "r") as file:
#         prompt_template = file.read()
        
    
#     prompt = PromptTemplate(
#         template= prompt_template + "\nRespond ONLY in JSON format:\n{format_instructions}",
#         input_variables=["pitch"],
#         partial_variables={"format_instructions":parser.get_format_instructions()}
#     )
    
#     formatted_prompt = prompt.format(pitch=pitch)
    
    
#     chain = prompt | llm | parser
    
#     result = await chain.ainvoke({"pitch":pitch})
    
#     return result.dict()