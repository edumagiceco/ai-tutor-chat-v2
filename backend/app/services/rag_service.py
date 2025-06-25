"""
RAG (Retrieval-Augmented Generation) Service using LangChain and LangGraph
"""
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_anthropic import ChatAnthropic
from langchain_core.runnables import RunnablePassthrough
from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict

from .vector_service import vector_service
from ..core.config import settings

logger = logging.getLogger(__name__)


class RAGState(TypedDict):
    """State for RAG workflow"""
    query: str
    context: List[Document]
    answer: str
    metadata: Dict[str, Any]


class RAGService:
    """Service for RAG-based question answering"""
    
    def __init__(self):
        self.llm = None
        self.text_splitter = None
        self.prompt_template = None
        self.graph = None
        self._initialize()
    
    def _initialize(self):
        """Initialize RAG components"""
        try:
            # Initialize LLM
            self.llm = ChatAnthropic(
                model="claude-3-sonnet-20240229",
                anthropic_api_key=settings.ANTHROPIC_API_KEY,
                temperature=0.7
            )
            
            # Initialize text splitter
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
                separators=["\n\n", "\n", ".", " ", ""]
            )
            
            # Initialize prompt template
            self.prompt_template = ChatPromptTemplate.from_template("""
당신은 AI 교육 전문 어시스턴트입니다. 제공된 컨텍스트를 바탕으로 사용자의 질문에 정확하고 도움이 되는 답변을 제공하세요.

컨텍스트:
{context}

질문: {question}

답변 시 다음 사항을 고려하세요:
1. 컨텍스트에 있는 정보를 기반으로 답변하세요
2. 정확하고 이해하기 쉬운 설명을 제공하세요
3. 필요한 경우 예시를 들어 설명하세요
4. 컨텍스트에 없는 정보는 일반적인 지식을 활용하되, 명확히 구분하세요

답변:
""")
            
            # Build RAG graph
            self._build_graph()
            
            logger.info("RAG service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG service: {e}")
            raise
    
    def _build_graph(self):
        """Build LangGraph workflow for RAG"""
        graph_builder = StateGraph(RAGState)
        
        # Add nodes
        graph_builder.add_node("retrieve", self._retrieve)
        graph_builder.add_node("generate", self._generate)
        
        # Add edges
        graph_builder.set_entry_point("retrieve")
        graph_builder.add_edge("retrieve", "generate")
        graph_builder.add_edge("generate", END)
        
        # Compile graph
        self.graph = graph_builder.compile()
    
    async def _retrieve(self, state: RAGState) -> Dict[str, Any]:
        """Retrieve relevant documents"""
        try:
            # Perform similarity search
            documents = await vector_service.similarity_search(
                query=state["query"],
                k=5
            )
            
            return {"context": documents}
            
        except Exception as e:
            logger.error(f"Failed to retrieve documents: {e}")
            return {"context": []}
    
    async def _generate(self, state: RAGState) -> Dict[str, Any]:
        """Generate answer based on context"""
        try:
            # Prepare context
            context = "\n\n".join([doc.page_content for doc in state["context"]])
            
            # Generate answer
            messages = self.prompt_template.invoke({
                "question": state["query"],
                "context": context
            })
            
            response = await self.llm.ainvoke(messages)
            
            return {
                "answer": response.content,
                "metadata": {
                    "sources": [doc.metadata for doc in state["context"]],
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to generate answer: {e}")
            return {
                "answer": "죄송합니다. 답변을 생성하는 중에 오류가 발생했습니다.",
                "metadata": {"error": str(e)}
            }
    
    async def process_documents(
        self,
        texts: List[str],
        metadata: Optional[List[Dict[str, Any]]] = None
    ) -> List[str]:
        """Process and index documents"""
        try:
            all_documents = []
            
            # Split texts into chunks
            for i, text in enumerate(texts):
                chunks = self.text_splitter.split_text(text)
                
                # Create documents with metadata
                for j, chunk in enumerate(chunks):
                    doc_metadata = {
                        "source_index": i,
                        "chunk_index": j,
                        "total_chunks": len(chunks)
                    }
                    
                    # Add custom metadata if provided
                    if metadata and i < len(metadata):
                        doc_metadata.update(metadata[i])
                    
                    doc = Document(
                        page_content=chunk,
                        metadata=doc_metadata
                    )
                    all_documents.append(doc)
            
            # Add documents to vector store
            ids = await vector_service.add_documents(all_documents)
            
            logger.info(f"Processed and indexed {len(all_documents)} document chunks")
            return ids
            
        except Exception as e:
            logger.error(f"Failed to process documents: {e}")
            raise
    
    async def ask(
        self,
        question: str,
        user_id: Optional[int] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Ask a question using RAG"""
        try:
            # Initialize state
            initial_state = RAGState(
                query=question,
                context=[],
                answer="",
                metadata={}
            )
            
            # Add user context if provided
            if user_id:
                initial_state["metadata"]["user_id"] = user_id
            if session_id:
                initial_state["metadata"]["session_id"] = session_id
            
            # Run the graph
            result = await self.graph.ainvoke(initial_state)
            
            return {
                "question": question,
                "answer": result["answer"],
                "sources": result["metadata"].get("sources", []),
                "timestamp": result["metadata"].get("timestamp")
            }
            
        except Exception as e:
            logger.error(f"Failed to process question: {e}")
            raise


# Singleton instance
rag_service = RAGService()