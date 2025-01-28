from phi.knowledge.combined import CombinedKnowledgeBase
from phi.vectordb.pgvector import PgVector
from phi.vectordb.sqlite import SQLiteVectorDB # trial

# url_pdf_knowledge_base = PDFUrlKnowledgeBase(
#     urls=["pdf_url"],
#     # Table name: ai.pdf_documents
#     vector_db=PgVector(
#         table_name="pdf_documents",
#         db_url="postgresql+psycopg://ai:ai@localhost:5532/ai",
#     ),
# )

website_knowledge_base = WebsiteKnowledgeBase(
    urls=["https://www.msuiit.edu.ph/offices/clinic/index.php"],
    # Number of links to follow from the seed URLs
    max_links=10,
    # Table name: ai.website_documents
    vector_db=PgVector(
        table_name="website_documents",
        db_url="postgresql+psycopg://ai:ai@localhost:5532/ai",
    ),
)

local_pdf_knowledge_base = PDFKnowledgeBase(
    path="ClinicBOT/Selfcare-PDFs",
    # Table name: ai.pdf_documents
    vector_db=PgVector(
        table_name="pdf_documents", 
        db_url="postgresql+psycopg://ai:ai@localhost:5532/ai",
    ),
    reader=PDFReader(chunk=True),
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
        db_url="postgresql+psycopg://ai:ai@localhost:5532/ai",
    ),
)
