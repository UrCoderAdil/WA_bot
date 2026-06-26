from sqlalchemy import select
from app.models.knowledge import KnowledgeEntry
from app.db.database import async_session
from langchain_core.tools import tool


class KnowledgeBaseService:
    """Simple knowledge base for business-specific information (RAG-lite)."""

    async def add_entry(self, title: str, content: str, category: str = None,
                        tenant_id: str = None) -> dict:
        """Add a knowledge entry."""
        async with async_session() as session:
            entry = KnowledgeEntry(
                title=title,
                content=content,
                category=category,
                tenant_id=tenant_id,
            )
            session.add(entry)
            await session.commit()
            await session.refresh(entry)
            return self._to_dict(entry)

    async def search(self, query: str, tenant_id: str = None) -> list[dict]:
        """Search knowledge entries using semantic vector search (FAISS)."""
        async with async_session() as session:
            stmt = select(KnowledgeEntry)
            if tenant_id:
                stmt = stmt.where(KnowledgeEntry.tenant_id == tenant_id)
            result = await session.execute(stmt)
            entries = result.scalars().all()

            if not entries:
                return []

            from langchain_community.vectorstores import FAISS
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
            from app.core.config import settings
            
            embeddings = GoogleGenerativeAIEmbeddings(
                model="models/embedding-001", 
                google_api_key=settings.GEMINI_API_KEY
            )
            
            # Create FAISS index on the fly (acts as an intelligent semantic cache)
            texts = [f"{e.title}: {e.content}" for e in entries]
            metadatas = [self._to_dict(e) for e in entries]
            
            vectorstore = await FAISS.afrom_texts(texts, embeddings, metadatas=metadatas)
            docs = await vectorstore.asimilarity_search(query, k=3)
            
            return [doc.metadata for doc in docs]

    async def get_all(self, tenant_id: str = None) -> list[dict]:
        """List all knowledge entries."""
        async with async_session() as session:
            stmt = select(KnowledgeEntry).order_by(KnowledgeEntry.created_at.desc())
            if tenant_id:
                stmt = stmt.where(KnowledgeEntry.tenant_id == tenant_id)
            result = await session.execute(stmt)
            entries = result.scalars().all()
            return [self._to_dict(e) for e in entries]

    async def delete_entry(self, entry_id: str) -> bool:
        """Delete a knowledge entry by ID."""
        async with async_session() as session:
            result = await session.execute(
                select(KnowledgeEntry).where(KnowledgeEntry.id == entry_id)
            )
            entry = result.scalar_one_or_none()
            if entry:
                await session.delete(entry)
                await session.commit()
                return True
            return False

    def _to_dict(self, entry: KnowledgeEntry) -> dict:
        return {
            "id": entry.id,
            "title": entry.title,
            "content": entry.content,
            "category": entry.category,
            "tenant_id": entry.tenant_id,
            "created_at": str(entry.created_at),
        }


kb_service = KnowledgeBaseService()


@tool
def search_knowledge_base(query: str) -> str:
    """
    Search the business knowledge base for information about products, policies,
    menu items, FAQs, or any other business-specific data.
    """
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                results = pool.submit(asyncio.run, kb_service.search(query)).result()
        else:
            results = asyncio.run(kb_service.search(query))

        if not results:
            return "No relevant knowledge found for this query."
        return "\n".join([f"- {r['title']}: {r['content']}" for r in results])
    except Exception as e:
        return f"Knowledge base search failed: {e}"
