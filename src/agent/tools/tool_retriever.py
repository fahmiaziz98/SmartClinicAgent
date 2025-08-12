import faiss
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

        self.documents = self._load_docs()
        self.vector_store = self._build_vector_store()

    def _load_docs(self):
        """Load and split Markdown documents."""
        logger.info(f"Loading documents from {self.path_docs}")
        loader = UnstructuredMarkdownLoader(str(self.path_docs))
        docs = loader.load()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
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
            index_to_docstore_id={}
        )
        logger.info(f"Building vector store from {len(self.documents)} documents")
        vector_store.add_documents(self.documents)
        vector_store.save_local(str(self.index_dir))
        return vector_store

    def load_retriever(self):
        """Load the FAISS index and return a retriever."""
        vector_store = FAISS.load_local(
            str(self.index_dir),
            self.embeddings,
            allow_dangerous_deserialization=True
        )
        logger.info(f"Loading retriever from {self.index_dir}")
        return vector_store.as_retriever(search_kwargs={"k": 5})
    
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