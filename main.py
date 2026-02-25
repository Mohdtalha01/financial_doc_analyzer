from fastapi import FastAPI, File, UploadFile, Form, HTTPException
import os
import uuid
import asyncio
from crewai import Crew, Process
from agents import financial_analyst, verifier, investment_advisor, risk_assessor
# BUG FIX 18: Imported "analyze_financial_document" from task.py, but main.py also defines
# a function called analyze_financial_document — this causes a name collision that silently
# overwrites the imported Task object with the FastAPI route function.
# Fix: rename the import to avoid the clash.
from task import (
    analyze_financial_document as analyze_task,
    investment_analysis,
    risk_assessment,
    verification,
)

app = FastAPI(title="Financial Document Analyzer")


def run_crew(query: str, file_path: str = "data/sample.pdf"):
    """Run the full multi-agent crew on the uploaded financial document."""
    # BUG FIX 19: Crew only included financial_analyst and analyze_financial_document.
    # All four agents and all four tasks must be included so the full pipeline runs.
    # BUG FIX 20: file_path was accepted as a parameter but never passed to the tasks.
    # Store it as an env var so FinancialDocumentTool can pick it up, OR pass via inputs.
    financial_crew = Crew(
        agents=[verifier, financial_analyst, investment_advisor, risk_assessor],
        tasks=[verification, analyze_task, investment_analysis, risk_assessment],
        process=Process.sequential,
        verbose=True,
    )

    result = financial_crew.kickoff(inputs={"query": query, "file_path": file_path})
    return result


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Financial Document Analyzer API is running"}


# BUG FIX 21: The FastAPI route function was named "analyze_financial_document" —
# the exact same name as the imported CrewAI Task object.
# This caused the Task object to be overwritten, breaking run_crew() silently.
# Fix: rename the route handler to "analyze_document_endpoint".
@app.post("/analyze")
async def analyze_document_endpoint(
    file: UploadFile = File(...),
    query: str = Form(default="Analyze this financial document for investment insights")
):
    """Analyze a financial document and provide comprehensive investment recommendations."""

    file_id = str(uuid.uuid4())
    file_path = f"data/financial_document_{file_id}.pdf"

    try:
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)

        # Save uploaded file
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # BUG FIX 22: Condition "query=="" or query is None" checks in the wrong order.
        # "query is None" should come first, otherwise calling .strip() on None elsewhere
        # would raise AttributeError. Also added .strip() check for whitespace-only input.
        if not query or not query.strip():
            query = "Analyze this financial document for investment insights"

        # Process the financial document with all analysts
        response = run_crew(query=query.strip(), file_path=file_path)

        return {
            "status": "success",
            "query": query,
            "analysis": str(response),
            "file_processed": file.filename,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing financial document: {str(e)}"
        )

    finally:
        # Clean up uploaded file
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass  # Ignore cleanup errors


if __name__ == "__main__":
    import uvicorn
    # BUG FIX 23: reload=True causes issues when running directly via __main__
    # because uvicorn tries to reload the module by import string, not file path.
    # Should be False when using direct object reference, or use "main:app" string form.
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)