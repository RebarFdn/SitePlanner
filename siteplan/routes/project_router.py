## Project router
# This route handles all project related requests 

from starlette.responses import HTMLResponse, RedirectResponse, JSONResponse, StreamingResponse
from decoRouter import Router
from modules.project import Project
from modules.employee import Employee
from modules.utils import timestamp, to_dollars

router = Router()

@router.GET('/projects')
async def get_projects(request):
    generator = Project().projects_index_generator()
    return StreamingResponse(generator, media_type="text/html")

@router.get('/project/{id}')
async def get_project(request):
    id = request.path_params.get('id')
    p = await Project().html_page(id=id)
    return HTMLResponse(p)

## Project Acconting
@router.get('/project_account/{id}')
async def get_project_account(request):
    id = request.path_params.get('id')
    p = await Project().html_account_page(id=id)
    return HTMLResponse(p)

@router.get('/project_account_deposits/{id}')
async def get_project_account_deposits(request):
    id = request.path_params.get('id')
    generator =  Project().html_account_deposits_generator(id=id)
    return StreamingResponse(generator, media_type="text/html")

@router.post('/account_deposit/{id}')
async def project_account_deposit(request):
    id = request.path_params.get('id')    
    payload = {}
    try:
        async with request.form() as form:
            payload['date'] = timestamp(form.get('date'))
            payload['type'] = form.get('type')
            payload['ref'] = form.get('ref')
            payload['amount'] = float(form.get('amount'))
            payload['payee'] = form.get('payee')
        #print(username, password)
        result = await Project().handleTransaction(id=id, data=payload)
        #return RedirectResponse(url='/dash', status_code=303)
        return HTMLResponse(f""" <div class="uk-alert-success" uk-alert>
                                <a href class="uk-alert-close" uk-close></a>
                                <p>{to_dollars(result.get('amount'))} was deposited on {result.get('date')}</p>
                                </div>""")
    except Exception as e:
        return HTMLResponse(f"""
                            <div class="uk-alert-warning" uk-alert>
                                <a href class="uk-alert-close" uk-close></a>
                                <p>{str(e)}</p>
                            </div>
                            """)


@router.get('/project_account_withdrawals/{id}')
async def get_project_account_withdrawals(request):
    id = request.path_params.get('id')
    generator =  Project().html_account_withdrawal_generator(id=id)
    return StreamingResponse(generator, media_type="text/html")


@router.get('/project_account_paybills/{id}')
async def get_project_account_paybills(request):
    id = request.path_params.get('id')
    generator = await Project().html_account_paybills_generator(id=id)
    #return StreamingResponse(generator, media_type="text/html")
    return HTMLResponse(f"""<div class="bg-yellow-500 py-5 px-5">{generator}</div>""")

@router.get('/project_account_salaries/{id}')
async def get_project_account_salaries(request):
    id = request.path_params.get('id')
    generator = await Project().html_account_salaries_generator(id=id)
    #return StreamingResponse(generator, media_type="text/html")
    return HTMLResponse(f"""<div class="bg-yellow-500 py-5 px-5">{generator}</div>""")

@router.get('/project_account_expences/{id}')
async def get_project_account_expences(request):
    id = request.path_params.get('id')
    generator = await Project().html_account_expences_generator(id=id)
    #return StreamingResponse(generator, media_type="text/html")
    return HTMLResponse(f"""<div class="bg-yellow-500 py-5 px-5">{generator}</div>""")

@router.get('/project_account_purchases/{id}')
async def get_project_account_purchases(request):
    id = request.path_params.get('id')
    generator = await Project().html_account_purchases_generator(id=id)
    #return StreamingResponse(generator, media_type="text/html")
    return HTMLResponse(f"""<div class="bg-yellow-500 py-5 px-5">{generator}</div>""")


## Project Jobs
@router.get('/project_jobs/{id}')
async def get_project_jobs(request):
    id = request.path_params.get('id')
    generator = Project().html_jobs_page_generator(id=id)
    return StreamingResponse(generator, media_type="text/html" )

@router.get('/project_days/{id}')
async def get_project_days(request):
    id = request.path_params.get('id')
    p = await Project().html_days_page(id=id)
    return HTMLResponse(p)

@router.get('/project_workers/{id}/{filter}')
async def get_project_workers(request):
    id = request.path_params.get('id')
    filter = request.path_params.get('filter')
    generator = Project().html_workers_page(id=id, filter=filter)
    return StreamingResponse(generator, media_type="text/html" )

@router.get('/project_rates/{id}')
async def get_project_rates(request):
    id = request.path_params.get('id')
    generator = Project().html_rates_page_generator(id=id)
    return StreamingResponse(generator, media_type="text/html" )


@router.get('/update_project_job_state/{id}/{state}')
async def update_project_job_state(request):
    id = request.path_params.get('id')
    state = request.path_params.get('state')
    jobstate = {
        "active": f"""<span class="badge badge-success">Active</span>""",
        "completed": f"""<span class="badge badge-primary">Completed</span>""",
        "paused": f"""<span class="badge badge-secondary">Paused</span>""",

        "terminated": f"""<span class="badge badge-error">Terminated</span>""",

    }
    
    return HTMLResponse(jobstate.get(state))

