from typing import List, Optional, AsyncGenerator
import httpx
from anthropic import Anthropic, AsyncAnthropic
import logging

from app.core.config import settings
from app.models.conversation import Message
from app.models.user import User

logger = logging.getLogger(__name__)


async def get_ai_response(
    user_message: str,
    conversation_history: List[Message],
    user: User,
    use_rag: bool = True
) -> str:
    """Get AI response using Anthropic Claude API with optional RAG"""
    
    # Initialize Anthropic client
    client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    
    # Try to get context from RAG if enabled
    rag_context = ""
    if use_rag:
        try:
            from .rag_service import rag_service
            rag_result = await rag_service.ask(
                question=user_message,
                user_id=user.id
            )
            if rag_result and rag_result.get("answer"):
                rag_context = f"\n\n참고 자료:\n{rag_result['answer']}\n"
                logger.info(f"Added RAG context for user query")
        except Exception as e:
            logger.warning(f"Failed to get RAG context: {e}")
    
    # Build conversation context
    messages = []
    
    # System prompt
    system_prompt = f"""당신은 AI 도구 활용을 통한 업무 혁신을 돕는 교육 전문가입니다.
사용자 정보:
- 이름: {user.name}
- 직무: {user.job_title or "미지정"}
- 부서: {user.department or "미지정"}
- AI 활용 수준: {user.ai_level}
{rag_context}
다음 지침을 따라주세요:
1. 사용자의 현재 AI 활용 수준에 맞춰 설명하세요
2. 실제 업무에 즉시 적용할 수 있는 실용적인 조언을 제공하세요
3. 구체적인 예시와 단계별 가이드를 포함하세요
4. 친근하고 격려하는 톤을 유지하세요
5. 한국어로 응답하세요
6. 참고 자료가 있다면 활용하여 더 정확한 답변을 제공하세요"""
    
    # Add conversation history
    for msg in conversation_history[-10:]:  # Last 10 messages for context
        if msg.role.value == "user":
            messages.append({"role": "user", "content": msg.content})
        elif msg.role.value == "assistant":
            messages.append({"role": "assistant", "content": msg.content})
    
    # Add current user message
    messages.append({"role": "user", "content": user_message})
    
    try:
        # Get response from Claude
        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=2048,
            temperature=0.7,
            system=system_prompt,
            messages=messages
        )
        
        return response.content[0].text
    
    except Exception as e:
        print(f"Error getting AI response: {str(e)}")
        raise


async def get_ai_response_stream(
    user_message: str,
    conversation_history: List[Message],
    user: User,
    use_rag: bool = True
) -> AsyncGenerator[str, None]:
    """Get AI response with streaming using Anthropic Claude API"""
    
    # Initialize Async Anthropic client
    client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
    
    # Try to get context from RAG if enabled
    rag_context = ""
    if use_rag:
        try:
            from .rag_service import rag_service
            rag_result = await rag_service.ask(
                question=user_message,
                user_id=user.id
            )
            if rag_result and rag_result.get("answer"):
                rag_context = f"\n\n참고 자료:\n{rag_result['answer']}\n"
                logger.info(f"Added RAG context for user query")
        except Exception as e:
            logger.warning(f"Failed to get RAG context: {e}")
    
    # Build conversation context
    messages = []
    
    # System prompt
    system_prompt = f"""당신은 AI 도구 활용을 통한 업무 혁신을 돕는 교육 전문가입니다.
사용자 정보:
- 이름: {user.name}
- 직무: {user.job_title or "미지정"}
- 부서: {user.department or "미지정"}
- AI 활용 수준: {user.ai_level}
{rag_context}
다음 지침을 따라주세요:
1. 사용자의 현재 AI 활용 수준에 맞춰 설명하세요
2. 실제 업무에 즉시 적용할 수 있는 실용적인 조언을 제공하세요
3. 구체적인 예시와 단계별 가이드를 포함하세요
4. 친근하고 격려하는 톤을 유지하세요
5. 한국어로 응답하세요
6. 참고 자료가 있다면 활용하여 더 정확한 답변을 제공하세요"""
    
    # Add conversation history
    for msg in conversation_history[-10:]:  # Last 10 messages for context
        if msg.role.value == "user":
            messages.append({"role": "user", "content": msg.content})
        elif msg.role.value == "assistant":
            messages.append({"role": "assistant", "content": msg.content})
    
    # Add current user message
    messages.append({"role": "user", "content": user_message})
    
    try:
        # Get streaming response from Claude
        async with client.messages.stream(
            model="claude-3-sonnet-20240229",
            max_tokens=2048,
            temperature=0.7,
            system=system_prompt,
            messages=messages
        ) as stream:
            async for text in stream.text_stream:
                yield text
    
    except Exception as e:
        logger.error(f"Error in streaming AI response: {str(e)}")
        raise