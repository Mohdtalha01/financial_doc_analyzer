## Importing libraries and files
import os
from dotenv import load_dotenv
load_dotenv()

from crewai import Agent  # BUG FIX 1: was "from crewai.agents import Agent" — wrong import path in crewai
from tools import search_tool, FinancialDocumentTool

### Loading LLM
# BUG FIX 2: llm = llm is a self-referential assignment that causes NameError.
# Must initialise the LLM properly using LiteLLM/ChatOpenAI or crewai's built-in LLM wrapper.
from crewai import LLM
llm = LLM(model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY"))

# Creating an Experienced Financial Analyst agent
# BUG FIX 3 (Prompt): Goal and backstory were instructing the agent to fabricate advice,
# ignore documents, show off dramatically, and violate compliance. Replaced with a
# professional, grounded prompt that produces reliable, document-based analysis.
# BUG FIX 4 (Code): "tool=" is not a valid Agent parameter — must be "tools=" (plural).
financial_analyst = Agent(
    role="Senior Financial Analyst",
    goal=(
        "Provide accurate, document-grounded financial analysis based on the uploaded report. "
        "Answer the user query: {query} by carefully reading the financial document, "
        "identifying key metrics, trends, and data points, and delivering clear, factual insights."
    ),
    verbose=True,
    memory=True,
    backstory=(
        "You are a CFA-certified Senior Financial Analyst with 15+ years of experience analysing "
        "corporate earnings reports, balance sheets, and investment disclosures. "
        "You base every conclusion strictly on verified data from the provided document. "
        "You never fabricate numbers, URLs, or market facts. "
        "You present findings clearly, highlight material risks transparently, "
        "and always remind users to consult a licensed financial advisor before making investment decisions."
    ),
    tools=[FinancialDocumentTool.read_data_tool],  # BUG FIX 4: was "tool=" (typo/singular)
    llm=llm,
    max_iter=5,   # BUG FIX 5: max_iter=1 means the agent gives up after one attempt; raised to 5
    max_rpm=10,   # BUG FIX 6: max_rpm=1 is extremely restrictive; raised to 10
    allow_delegation=True
)

# Creating a document verifier agent
# BUG FIX 7 (Prompt): Goal and backstory were telling agent to rubber-stamp everything
# without reading, hallucinate financial content from grocery lists, and skip compliance.
# Replaced with a proper document validation prompt.
verifier = Agent(
    role="Financial Document Verifier",
    goal=(
        "Verify that the uploaded file is a legitimate financial document (annual report, "
        "earnings release, balance sheet, income statement, etc.). "
        "Confirm the document structure, check that key financial sections are present, "
        "and flag any anomalies or non-financial content before analysis begins."
    ),
    verbose=True,
    memory=True,
    backstory=(
        "You are a financial compliance specialist with deep experience in document due-diligence "
        "at a Big Four accounting firm. You carefully read every document before approving it. "
        "You will not approve non-financial documents and you accurately identify the type, "
        "issuer, and reporting period of any financial filing you review."
    ),
    llm=llm,
    max_iter=5,   # BUG FIX 5 (same as above)
    max_rpm=10,
    allow_delegation=True
)

# BUG FIX 8 (Prompt): investment_advisor goal and backstory encouraged selling sketchy products,
# hiding conflicts of interest, ignoring SEC compliance, and fabricating credentials.
# Replaced with an ethical, document-driven advisor prompt.
investment_advisor = Agent(
    role="Certified Investment Advisor",
    goal=(
        "Based strictly on the verified financial document, provide balanced, evidence-based "
        "investment considerations. Highlight opportunities and risks equally. "
        "Never recommend specific securities without proper disclaimer. "
        "Always disclose that recommendations are for informational purposes only."
    ),
    verbose=True,
    backstory=(
        "You are a FINRA-registered investment advisor with 12 years of experience in "
        "portfolio management and financial planning. You rely entirely on verified financial data "
        "to form your views. You have zero tolerance for fabricated data or undisclosed conflicts. "
        "You always include appropriate regulatory disclaimers in your output."
    ),
    llm=llm,
    max_iter=5,
    max_rpm=10,
    allow_delegation=False
)

# BUG FIX 9 (Prompt): risk_assessor goal and backstory promoted reckless risk-taking,
# dismissed diversification, glorified volatility, and mocked regulations.
# Replaced with a structured, standards-based risk assessment prompt.
risk_assessor = Agent(
    role="Risk Assessment Specialist",
    goal=(
        "Conduct a structured, document-based risk assessment. Identify financial, operational, "
        "market, credit, and liquidity risks present in the document. "
        "Rate each risk using a standard framework (likelihood vs impact). "
        "Provide realistic, balanced mitigation strategies grounded in the data."
    ),
    verbose=True,
    backstory=(
        "You are a Chartered Risk Analyst (CRA) with institutional experience at a top-tier "
        "asset management firm. You apply rigorous, evidence-based risk frameworks such as "
        "COSO and Basel guidelines. You never dramatise risks beyond what the data supports, "
        "and you always recommend prudent, diversified risk management strategies."
    ),
    llm=llm,
    max_iter=5,
    max_rpm=10,
    allow_delegation=False
)