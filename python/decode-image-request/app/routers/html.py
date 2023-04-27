from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse


router = APIRouter(
    prefix="/forms",
    tags=["forms"],
)

templates = Jinja2Templates(directory="app/templates")


@router.get("/consent", response_class=HTMLResponse)
async def get_consent_form(request: Request, postback_url: str):
    """
    Going to serve the consent form based on tenant ID.
    """
    return templates.TemplateResponse(
        "consent-form.html",
        {
            "request": request,
            "postback_url": postback_url,
            "logo": "templates/logo.png",
        },
    )
