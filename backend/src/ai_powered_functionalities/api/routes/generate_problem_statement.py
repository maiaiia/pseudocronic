# router file
from fastapi import APIRouter, HTTPException, Request
from ....rate_limiter import rate_limit
from ...generate_problem_statements.generate_problems import GenerateProblem
from ...models.responses import GenerateProblemStatementResponse

router = APIRouter(prefix="/generate-problems", tags=["Generate Problem Statements"])

generator = GenerateProblem()

@router.post("/", response_model=GenerateProblemStatementResponse)
@rate_limit(max_calls=10, window_hours=1)
async def generate_problem_statement(request: Request):
    """
    Generate problem statements that can be solved in pseudocode.
    """
    try:
        result = await generator.generate_problem()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
