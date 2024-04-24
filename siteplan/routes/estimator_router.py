from starlette.responses import HTMLResponse, RedirectResponse, JSONResponse, StreamingResponse
from decoRouter import Router
from modules.project import Project
from modules.estimator.wall import Wall
from modules.utils import timestamp, to_dollars
from config import (TEMPLATES,LOG_PATH ,SYSTEM_LOG_PATH ,SERVER_LOG_PATH, APP_LOG_PATH )





router = Router()

@router.GET('/estimate')
async def get_estimates(request):
    context = {"title": "Siteplanner Estimator"}
    return TEMPLATES.TemplateResponse("estimator.html", {"request": request, "context": context})       



@router.post('/wall')
async def process_wall(request):
       
    payload = {}
    try:
        async with request.form() as form:
            payload['date'] = timestamp(form.get('date'))
            payload['type'] = form.get('type')
            payload['width'] = form.get('width')
            payload['length'] = float(form.get('length'))
            payload['height'] = form.get('height')
       
        return HTMLResponse(f""" <div class="uk-alert-success" uk-alert>
                                <a href class="uk-alert-close" uk-close></a>
                                <p>Ref: {payload.get('ref')} {payload.get('length')} </p>
                                </div>""")
    except Exception as e:
        return HTMLResponse(f"""
                            <div class="uk-alert-warning" uk-alert>
                                <a href class="uk-alert-close" uk-close></a>
                                <p>{str(e)}</p>
                            </div>
                            """)
