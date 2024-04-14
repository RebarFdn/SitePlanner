from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse, HTMLResponse, StreamingResponse, RedirectResponse
from starlette.background import BackgroundTasks
from starlette.websockets import WebSocket
import asyncio
from config import (DEBUG, SECRET_KEY, ALLOWED_HOSTS, HOST, PORT, TEMPLATES)
from modules.zen import zen_now

from routes.auth_router import router as auth_routes, loadusers
from routes.project_router import router as p_router
from routes.team_router import router as team_router
from routes.base_router import router as base_router
from modules.supplier import supplier_router 





async def get_users():
    users = loadusers()
    
    yield '<ul class="mx-10 p-2">'
    for user in users:
        yield f"""<li><div class="ml-3">
        <p 
        class="text-sm font-medium text-gray-900 cursor-pointer"
        hx-get="/user/{user.get('username')}"        
        hx-trigger="click"
        hx-target="#user"
        ><span class="text-xs font-bold text-indigo-500">User</span> {user.get("username")}</p>
        
        
      </div></li>"""
        await asyncio.sleep(0.015)
    yield '</ul>'

async def get_user(request):
    name = request.path_params.get('name')
    store = loadusers({"name": "Haley", "age": 29 })
    search = [user for user in store if user.get('name') == name][0]
    return HTMLResponse(f"""<p class="mx-5 p-2">{search.get("name")}</p><p 
        class="text-sm text-gray-500"
        >Age { search.get("age") }</p>"""
        )

async def home(request):
    return TEMPLATES.TemplateResponse('/intro/intro.html', {'request': request})

async def loading(request):      
    return HTMLResponse(f""" <div class="animate-spin inline-block size-6 border-[3px] border-current border-t-transparent text-blue-600 rounded-full dark:text-blue-500" role="status" aria-label="loading">
    <span class="sr-only">Loading...</span>
  </div>""")

async def users(response):
    generator = get_users()
    return StreamingResponse(generator, media_type='text/html')

async def dashboard(request):
    return TEMPLATES.TemplateResponse('/dash.html', {'request': request})

async def uikit(request):
    return TEMPLATES.TemplateResponse('/analytics.html', {'request': request})



async def zenNow(request):
  return HTMLResponse(f"""
        
            <p class="text-xs font-bold bg-gray-100 py-2 px-4 rounded w-96">{zen_now()}</P> 
        
        """)
    
routes =[
    Route('/', endpoint=home), 
    Route('/uikit', endpoint=uikit), 
    Route('/dash', endpoint=dashboard),    
    Route('/loading', endpoint=loading),  
    Route('/users', endpoint=users),  
    Route('/user/{name}', endpoint=get_user),  
    Route('/zen', endpoint=zenNow),  
    Mount('/static', StaticFiles(directory='static'))
]

routes.extend([route for route in auth_routes])
routes.extend([route for route in p_router])
routes.extend([route for route in team_router])
routes.extend([route for route in base_router])
routes.extend([route for route in supplier_router])


def startApp():
    print('Starting SiteApp Servers ')
   
    


def shutdownApp():
    print('Application setup was Successfull ... !')

app = Starlette(
    debug=DEBUG, 
    routes=routes,
    on_startup= startApp(),
    on_shutdown= shutdownApp()
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=False,
    allow_origin_regex=None,
    expose_headers=[
        "Access-Control-Allow-Origin",
        "Access-Control-Allow-Cedentials",
        "Access-Control-Allow-Expose-Headers",
    ],
    max_age=3600,
)


def run_http():
    from uvicorn import run
    run(
        app,
        host=HOST,
        port= PORT     )
    
run_http()

