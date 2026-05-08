# api/routes.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from agents.planner_agent import PlannerAgent
from agents.executor_agent import ExecutorAgent
from agents.analyzer_agent import AnalyzerAgent
from agents.summary_agent import SummaryAgent
from orcha_memory.memory_store import store, retrieve, list_all, compare, delete
from reports.report import generate_pdf, generate_html
import os

router = APIRouter()


# ── request models ────────────────────────────────────────
class AnalyzeRequest(BaseModel):
    product: str


class CompareRequest(BaseModel):
    product_a: str
    product_b: str


# ── analyze ───────────────────────────────────────────────
@router.post("/analyze")
async def analyze(request: AnalyzeRequest):
    product = request.product.strip()

    if not product:
        raise HTTPException(status_code=400, detail="Product name is required")

    # check memory first
    cached = retrieve(product)
    if cached:
        return {"source": "cache", "data": cached}

    try:
        # step 1 — plan
        plan = await PlannerAgent().plan(product)

        # step 2 — execute
        execution = await ExecutorAgent().execute(plan)

        if not execution or execution.get("total_results", 0) == 0:
            raise HTTPException(status_code=404, detail="No search results found for this product")

        # step 3 — analyze
        analysis = await AnalyzerAgent().analyze(product, execution.get("key_findings", []))

        # step 4 — summarize
        summary = await SummaryAgent().summarize(analysis)

        # save to memory
        store(product, summary)

        return {"source": "live", "data": summary}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── memory ────────────────────────────────────────────────
@router.get("/memory")
async def memory_list():
    entries = list_all()
    return {"entries": entries}


@router.get("/memory/{product}")
async def memory_get(product: str):
    result = retrieve(product)
    if not result:
        raise HTTPException(status_code=404, detail=f"No analysis found for '{product}'")
    return {"product": product, "data": result}


@router.delete("/memory/{product}")
async def memory_delete(product: str):
    delete(product)
    return {"message": f"Deleted analysis for '{product}'"}


# ── compare ───────────────────────────────────────────────
@router.post("/compare")
async def compare_products(request: CompareRequest):
    result = compare(request.product_a, request.product_b)
    if not result:
        raise HTTPException(
            status_code=404,
            detail="Both products must be analyzed before comparing"
        )
    return {"data": result}


# ── report export ─────────────────────────────────────────
@router.get("/report/html/{product}")
async def report_html(product: str):
    result = retrieve(product)
    if not result:
        raise HTTPException(status_code=404, detail=f"No analysis found for '{product}'")

    path = generate_html(product, result)
    return FileResponse(path, media_type="text/html", filename=f"{product}_report.html")


@router.get("/report/pdf/{product}")
async def report_pdf(product: str):
    result = retrieve(product)
    if not result:
        raise HTTPException(status_code=404, detail=f"No analysis found for '{product}'")

    path = generate_pdf(product, result)
    return FileResponse(path, media_type="application/pdf", filename=f"{product}_report.pdf")