from phi.knowledge.combined import CombinedKnowledgeBase
from phi.knowledge.website import WebsiteKnowledgeBase
from phi.knowledge.pdf import PDFKnowledgeBase, PDFReader
from phi.vectordb.pgvector import PgVector
from phi.embedder.ollama import OllamaEmbedder
from pathlib import Path

db_url="postgresql+psycopg://postgres:1234@localhost:5432/knowledge_base"

website_knowledge_base = WebsiteKnowledgeBase(
    urls=["https://www.msuiit.edu.ph/offices/clinic/index.php", "https://www.msuiit.edu.ph/offices/clinic/facilities.php", "https://www.msuiit.edu.ph/offices/clinic/staff.php"],
    # Number of links to follow from the seed URLs
    max_links=1,
    # Table name: ai.website_documents
    vector_db=PgVector(
        table_name="website_documents",
        db_url=db_url,
        embedder=OllamaEmbedder(model="nomic-embed-text", dimensions=768),
    ),
)

# Get all PDFs from your folder
pdf_folder = Path("app/Selfcare-PDFs")
local_pdf_knowledge_base = PDFKnowledgeBase(
    path=pdf_folder,
    # Table name: ai.pdf_documents
    vector_db=PgVector(
        table_name="pdf_documents",
        db_url=db_url,
        embedder=OllamaEmbedder(model="nomic-embed-text", dimensions=768),
    ),
    reader=PDFReader(chunk=True),
)

knowledge_base = CombinedKnowledgeBase(
    sources=[
        website_knowledge_base,
        local_pdf_knowledge_base,
    ],
    vector_db=PgVector(
        # Table name: ai.combined_documents
        table_name="combined_documents",
        db_url=db_url,
        embedder=OllamaEmbedder(model="nomic-embed-text", dimensions=768),
    ),
)
