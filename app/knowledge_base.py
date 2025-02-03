from phi.knowledge.combined import CombinedKnowledgeBase
from phi.knowledge.website import WebsiteKnowledgeBase
from phi.knowledge.pdf import PDFKnowledgeBase, PDFReader
from phi.knowledge.pdf import PDFUrlKnowledgeBase
from phi.vectordb.pgvector import PgVector

db_url="postgresql+psycopg://postgres:1234@localhost:5432/knowledge_base"

# url_pdf_knowledge_base = PDFUrlKnowledgeBase(
#     urls=["pdf_url"],
#     # Table name: ai.pdf_documents
#     vector_db=PgVector(
#         table_name="pdf_documents",
#         db_url="postgresql+psycopg://root:1234@localhost:5432/knowledge_base",
#     ),
# )

website_knowledge_base = WebsiteKnowledgeBase(
    urls=["https://www.msuiit.edu.ph/offices/clinic/index.php"],
    # Number of links to follow from the seed URLs
    max_links=20,
    # Table name: ai.website_documents
    vector_db=PgVector(
        table_name="website_documents",
        db_url=db_url,
    ),
)

local_pdf_knowledge_base = PDFKnowledgeBase(
    path="Selfcare-PDFs",
    # Table name: ai.pdf_documents

)

knowledge_base = CombinedKnowledgeBase(
    sources=[
        # url_pdf_knowledge_base,
        website_knowledge_base,
        local_pdf_knowledge_base,
    ],
    vector_db=PgVector(
        # Table name: ai.combined_documents
        table_name="combined_documents",
        db_url=db_url,
    ),
)
