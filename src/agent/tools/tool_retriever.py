import faiss
from typing import Any, Callable, List
from pathlib import Path
from loguru import logger
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_core.tools import tool
from src.agent.setting import settings
from .schema import InputKnowledgeBase


class VectorStoreRetriever:
    """
    A utility class for creating and retrieving a FAISS-based vector store
    from Markdown documents.
    """

    def __init__(
        self,
        path_docs: str = settings.DOCS_PATH,
        index_dir: str = settings.FAISS_INDEX,
        chunk_size: int = 500,
        chunk_overlap: int = 100,
    ):
        self.path_docs = Path(path_docs)
        self.embeddings = FastEmbedEmbeddings()
        self.index_dir = Path(index_dir)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        if self._index_exists():
            logger.info(
                f"FAISS index found in {self.index_dir}, loading instead of rebuilding."
            )
            self.vector_store = self._load_vector_store()
        else:
            logger.info("No FAISS index found, building a new one.")
            self.documents = self._load_docs()
            self.vector_store = self._build_vector_store()

    def _index_exists(self) -> bool:
        """Check if FAISS index and pkl files exist."""
        faiss_file = self.index_dir / "index.faiss"
        pkl_file = self.index_dir / "index.pkl"
        return faiss_file.exists() and pkl_file.exists()

    def _load_docs(self):
        """Load and split Markdown documents."""
        logger.info(f"Loading documents from {self.path_docs}")
        loader = UnstructuredMarkdownLoader(str(self.path_docs / "faq.md"))
        docs = loader.load()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap
        )
        return splitter.split_documents(docs)

    def _build_vector_store(self):
        """Create a FAISS vector store from documents and save locally."""
        dim = len(self.embeddings.embed_query("hello world"))
        index = faiss.IndexFlatL2(dim)

        vector_store = FAISS(
            embedding_function=self.embeddings,
            index=index,
            docstore=InMemoryDocstore(),
            index_to_docstore_id={},
        )
        logger.info(f"Building vector store from {len(self.documents)} documents")
        vector_store.add_documents(self.documents)

        # pastikan folder ada
        self.index_dir.mkdir(parents=True, exist_ok=True)
        vector_store.save_local(str(self.index_dir))
        return vector_store

    def _load_vector_store(self):
        """Load existing FAISS index."""
        return FAISS.load_local(
            str(self.index_dir), self.embeddings, allow_dangerous_deserialization=True
        )

    def load_retriever(self):
        """Return retriever wrapper around vector store."""
        logger.info(f"Loading retriever from {self.index_dir}")
        return self.vector_store.as_retriever(search_kwargs={"k": 5})


VECTORESTORE: VectorStoreRetriever = VectorStoreRetriever()
retriever = VECTORESTORE.load_retriever()


@tool("knowledge_base_tool", args_schema=InputKnowledgeBase)
def knowledge_base_tool(query: str):
    """
    Use this tool to answer questions related to the clinic’s knowledge base,
    such as operating hours, address, available services, diagnoses,
    and other clinic-related information.
    The tool retrieves relevant content from stored documents and returns the most relevant excerpts to the user.
    """
    logger.info(f"Searching query: {query}")
    docs = retriever.invoke(query)
    return "\n\n".join([doc.page_content for doc in docs])


TOOLS_KNOWLEDGE_BASE: List[Callable[..., Any]] = [
    knowledge_base_tool,
]
