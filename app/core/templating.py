from fastapi.templating import Jinja2Templates
from fastapi import Request
import time
from jinja2 import pass_context

def flash(request: Request, message: str, category: str = "info"):
    if "_messages" not in request.session:
        request.session["_messages"] = []
    request.session["_messages"].append({"message": message, "category": category})

@pass_context
def get_flashed_messages(context: dict):
    request: Request = context.get("request")
    if request and "_messages" in request.session:
        return request.session.pop("_messages")
    return []

templates = Jinja2Templates(directory="app/templates")
templates.env.globals.update(
    config={'VERSION': int(time.time())}, 
    get_flashed_messages=get_flashed_messages
)