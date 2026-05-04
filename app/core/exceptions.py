from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import ValidationError
from app.core.templating import templates, flash

def setup_exception_handlers(app: FastAPI):
    # Validation errors
    @app.exception_handler(ValidationError)
    async def validation_exception_handler(request: Request, exc: ValidationError):
        path = request.url.path
        
        if path == "/login":
            error_msg = "Invalid credentials"
        else:
            error_type = exc.errors()[0].get('type')
            
            if error_type == 'string_too_long':
                error_msg = "Значение слишком длинное"
            elif error_type == 'string_too_short':
                error_msg = "Значение слишком короткое"
            elif error_type == 'value_error':
                error_msg = exc.errors()[0].get('msg').replace('Value error, ', '')
            else:
                error_msg = exc.errors()[0].get('msg')

        flash(request, f"Error: {error_msg}", "error")
        
        form = await request.form()

        route_templates = {
            "/register": "register.html",
            "/login": "login.html",
        }

        template_name = route_templates.get(path)

        if template_name:
            context = {"request": request}
            context.update(form) 
            
            return templates.TemplateResponse(request, template_name, context=context, status_code=422)

        referer = request.headers.get("referer", "/")
        return RedirectResponse(url=referer, status_code=303)

    @app.exception_handler(404)
    async def not_found(request: Request, exception) -> HTMLResponse:
        return templates.TemplateResponse(request, "404.html", status_code=404)
