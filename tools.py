## Importing libraries and files
import os
from dotenv import load_dotenv
load_dotenv()

# BUG FIX 1: "from crewai_tools import tools" — imports the module, not anything useful.
# This line is unused and would cause confusion. Removed entirely.
from crewai_tools import SerperDevTool

# BUG FIX 3: Missing import for PDF loading. "Pdf" is used below but never imported.
# LangChain's PyPDFLoader is the correct tool for this.
from langchain_community.document_loaders import PyPDFLoader

# BUG FIX 4: Missing import for crewai's @tool decorator, required to expose
# class methods as usable CrewAI tools.
from crewai import tool

## Creating search tool
search_tool = SerperDevTool()


## Creating custom pdf reader tool
class FinancialDocumentTool:

    # BUG FIX 5: Method was "async def" but CrewAI tools must be synchronous.
    # async tools are never awaited by CrewAI's executor — they return a coroutine
    # object instead of actual text, silently breaking the agent.
    # BUG FIX 6: Missing @tool decorator — without it, CrewAI cannot discover or
    # invoke this method as a tool; agents would error on execution.
    # BUG FIX 7: Method uses "Pdf(...).load()" but "Pdf" was never imported anywhere.
    # Replaced with PyPDFLoader which is the correct LangChain PDF loader.
    # BUG FIX 8: Method is not a @staticmethod — instance methods on a class
    # require "self" as first arg, but it's called as FinancialDocumentTool.read_data_tool
    # (no instance), which would raise TypeError. Made it a @staticmethod.
    @staticmethod
    @tool("Read Financial Document")
    def read_data_tool(path: str = "data/sample.pdf") -> str:
        """Tool to read data from a PDF file at the given path.

        Args:
            path (str): Path of the PDF file. Defaults to 'data/sample.pdf'.

        Returns:
            str: Full text content of the financial document.
        """
        if not os.path.exists(path):
            return f"Error: File not found at '{path}'. Please provide a valid PDF path."

        try:
            loader = PyPDFLoader(file_path=path)
            docs = loader.load()
            full_report = ""
            for data in docs:
                content = data.page_content

                # Clean and format the financial document data
                while "\n\n" in content:
                    content = content.replace("\n\n", "\n")

                full_report += content + "\n"

            if not full_report.strip():
                return "Warning: No extractable text found in the PDF. It may be a scanned image."

            return full_report

        except Exception as e:
            return f"Error reading PDF: {str(e)}"


## Creating Investment Analysis Tool
class InvestmentTool:

    # BUG FIX 9: async def — same issue as above; must be synchronous for CrewAI.
    # BUG FIX 10: Missing @staticmethod and @tool decorator.
    # BUG FIX 11: The while-loop for removing double spaces is O(n²) and mutates
    # a string inside a loop using manual index tracking — fragile and slow.
    # Replaced with a simple, correct one-liner.
    @staticmethod
    @tool("Analyze Investment Data")
    def analyze_investment_tool(financial_document_data: str) -> str:
        """Analyse pre-extracted financial document text for investment insights.

        Args:
            financial_document_data (str): Raw text extracted from a financial PDF.

        Returns:
            str: Processed financial data ready for investment analysis.
        """
        if not financial_document_data:
            return "Error: No financial data provided for analysis."

        # BUG FIX 11: Replaced broken O(n²) manual string mutation loop with
        # a simple, correct approach
        processed_data = " ".join(financial_document_data.split())

        # TODO: Extend with ratio calculations, trend analysis, etc.
        return processed_data


## Creating Risk Assessment Tool
class RiskTool:

    # BUG FIX 12: async def — same synchronous requirement issue.
    # BUG FIX 13: Missing @staticmethod and @tool decorator.
    @staticmethod
    @tool("Create Risk Assessment")
    def create_risk_assessment_tool(financial_document_data: str) -> str:
        """Perform a risk assessment on extracted financial document text.

        Args:
            financial_document_data (str): Raw text extracted from a financial PDF.

        Returns:
            str: Risk assessment output based on the financial data.
        """
        if not financial_document_data:
            return "Error: No financial data provided for risk assessment."

        # TODO: Implement risk scoring, flag high-debt ratios, low liquidity, etc.
        return "Risk assessment functionality to be implemented"