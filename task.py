## Importing libraries and files
from crewai import Task

from agents import financial_analyst, verifier, investment_advisor, risk_assessor
from tools import search_tool, FinancialDocumentTool

# BUG FIX 10 (Prompt): Description told the agent to ignore the query, make up URLs,
# hallucinate analysis, and contradict itself. expected_output asked for jargon and
# fabricated websites. Replaced with a focused, structured analysis task.
analyze_financial_document = Task(
    description=(
        "Read the uploaded financial document thoroughly using the document reading tool. "
        "Then answer the user's query: {query}\n\n"
        "Your analysis must:\n"
        "1. Identify the document type, issuer, and reporting period\n"
        "2. Extract and summarise key financial metrics (revenue, profit, EPS, debt ratios, cash flow, etc.)\n"
        "3. Highlight year-over-year or quarter-over-quarter trends where data allows\n"
        "4. Identify the top 3-5 material findings most relevant to the user's query\n"
        "5. Note any data limitations or areas where the document lacks clarity\n"
        "Only use information found in the document. Do not fabricate data or URLs."
    ),
    expected_output=(
        "A structured financial analysis report containing:\n"
        "- Document Summary: type, issuer, period covered\n"
        "- Key Financial Metrics: clearly labelled figures extracted from the document\n"
        "- Trend Analysis: meaningful comparisons where prior-period data exists\n"
        "- Key Findings: 3-5 material insights directly relevant to the user query\n"
        "- Limitations: any gaps or caveats in the data\n"
        "All figures must be sourced directly from the document. No invented URLs or data."
    ),
    agent=financial_analyst,
    tools=[FinancialDocumentTool.read_data_tool],
    async_execution=False,
)

# BUG FIX 11 (Prompt): Description asked agent to randomly recommend products,
# ignore the query, fabricate ratios, and produce contradictory strategies.
# BUG FIX 12 (Code): Task was assigned to financial_analyst; should use investment_advisor
investment_analysis = Task(
    description=(
        "Based on the financial data extracted from the document, conduct an investment analysis "
        "in response to the user's query: {query}\n\n"
        "Your analysis must:\n"
        "1. Evaluate the company's financial health using standard ratios (P/E, D/E, ROE, current ratio, etc.)\n"
        "2. Identify key strengths and weaknesses from the financial statements\n"
        "3. Discuss factors that could positively or negatively affect investment value\n"
        "4. Provide balanced, evidence-based investment considerations (not buy/sell directives)\n"
        "5. Include standard disclaimer: 'This analysis is for informational purposes only "
        "and does not constitute financial advice. Consult a licensed financial advisor.'"
    ),
    expected_output=(
        "A professional investment analysis containing:\n"
        "- Financial Health Summary: key ratios with values sourced from the document\n"
        "- Strengths & Weaknesses: backed by specific data points\n"
        "- Investment Considerations: balanced pros and cons based strictly on the document\n"
        "- Disclaimer: clearly stated at the end\n"
        "No fabricated data, no specific buy/sell recommendations, no imaginary websites."
    ),
    agent=investment_advisor,
    tools=[FinancialDocumentTool.read_data_tool],
    async_execution=False,
)

# BUG FIX 13 (Prompt): Description told agent to ignore real risk factors, create
# dramatic scenarios, and skip regulatory compliance.
# BUG FIX 14 (Code): Task was assigned to financial_analyst; should use risk_assessor
risk_assessment = Task(
    description=(
        "Perform a structured risk assessment of the financial document in the context of "
        "the user's query: {query}\n\n"
        "Your assessment must:\n"
        "1. Identify financial risks (liquidity, credit, leverage) from the document's data\n"
        "2. Identify market and operational risks mentioned or implied in the report\n"
        "3. Rate each identified risk as Low / Medium / High with a brief justification\n"
        "4. Suggest realistic, standard mitigation strategies for each material risk\n"
        "5. Summarise the overall risk profile of the entity\n"
        "Base all assessments on document evidence. Do not fabricate risk scenarios."
    ),
    expected_output=(
        "A structured risk assessment report containing:\n"
        "- Risk Register: table of identified risks with category, rating, and evidence from the document\n"
        "- Mitigation Strategies: practical, standard approaches for each High/Medium risk\n"
        "- Overall Risk Profile: Low / Medium / High with summary justification\n"
        "- Disclaimer: 'Risk assessments are based solely on the provided document and "
        "should be validated by a qualified risk professional before decision-making.'"
    ),
    agent=risk_assessor,
    tools=[FinancialDocumentTool.read_data_tool],
    async_execution=False,
)

# BUG FIX 15 (Prompt): Description told verifier to guess and hallucinate.
# BUG FIX 16 (Code): Had broken indentation causing IndentationError at import time.
# BUG FIX 17 (Code): Task was assigned to financial_analyst; should use verifier agent
verification = Task(
    description=(
        "Verify the uploaded document before any analysis takes place.\n\n"
        "Your verification must:\n"
        "1. Confirm the file is readable and not corrupted\n"
        "2. Identify whether it is a recognised financial document type "
        "(annual report, 10-K, earnings release, balance sheet, income statement, etc.)\n"
        "3. Extract and confirm: issuer name, reporting period, currency, and auditor (if present)\n"
        "4. Flag any concerns: missing sections, unusual formatting, or non-financial content\n"
        "5. Provide a clear PASS or FAIL verdict with reasoning before analysis proceeds"
    ),
    expected_output=(
        "A verification report containing:\n"
        "- Document Type: identified category of financial document\n"
        "- Issuer & Period: company name and reporting period extracted from the document\n"
        "- Key Sections Present: list of major financial sections found (e.g. Income Statement, Balance Sheet)\n"
        "- Concerns: any anomalies, missing data, or non-financial content detected\n"
        "- Verdict: PASS or FAIL with a one-paragraph justification\n"
        "Do not approve documents without actually reading them."
    ),
    agent=verifier,
    tools=[FinancialDocumentTool.read_data_tool],
    async_execution=False
)