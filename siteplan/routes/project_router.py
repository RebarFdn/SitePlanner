## Project router
# This route handles all project related requests 

from starlette.responses import HTMLResponse, RedirectResponse, JSONResponse, StreamingResponse
from decoRouter import Router
from modules.project import Project
from modules.employee import Employee
from modules.utils import timestamp, to_dollars
from config import TEMPLATES
from database import RedisCache


router = Router()

@router.GET('/projects')
async def get_projects(request):
    generator = Project().projects_index_generator()
    return StreamingResponse(generator, media_type="text/html")

@router.get('/project/{id}')
async def get_project(request):
    id = request.path_params.get('id')
    p = await Project().get(id=id)
    return TEMPLATES.TemplateResponse('/project/projectPage.html', 
                                      {
                                          "request": request, 
                                          "id": id, 
                                          "p": p
                                          })

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
                                <p>Ref: {result.get('ref')} {to_dollars(result.get('amount'))} was deposited on {result.get('date')}</p>
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
    p = await Project().get(id=id)
    
    return TEMPLATES.TemplateResponse('/project/account/projectPaybills.html',
                                      
        {"request": request,
         "id": id,
         "p": p
         })

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
    p = await Project().get(id=id)
    jobs = p.get('tasks')
    
    return TEMPLATES.TemplateResponse(
        '/project/jobsIndex.html', 
        { "request": request, "p": p, "jobs": jobs }
        )


@router.get('/project_days/{id}')
async def get_project_days(request):
    id = request.path_params.get('id')
    p = await Project().html_days_page(id=id)
    return HTMLResponse(p)

@router.get('/project_workers/{id}/{filter}')
async def get_project_workers(request):
    id = request.path_params.get('id')
    filter = request.path_params.get('filter')
    p = await Project().get(id=id)
    e = await Employee().all_workers()
    workers = p.get('workers')
    categories = { worker.get('value').get('occupation') for worker in workers }
    if filter:
        if filter == 'all' or filter == 'None':            
            filtered = workers 
        else:
            filtered = [worker for worker in workers if worker.get("value").get("occupation") == filter]

    
    return  TEMPLATES.TemplateResponse('/project/projectWorkers.html', 
                                       {
                                           "request": request,
                                           "id": id,
                                           "p": p,
                                           "employees": e,
                                           "workers": workers,
                                           "categories": categories,
                                           "filter" : filter,
                                           "filtered": filtered

                                           
                                        })



@router.get('/project_rates/{id}')
async def get_project_rates(request):
    id = request.path_params.get('id')
    generator = Project().html_rates_page_generator(id=id)
    return StreamingResponse(generator, media_type="text/html" )


@router.get('/update_project_job_state/{id}/{state}')
async def update_project_job_state(request):
    id = request.path_params.get('id')
    status = request.path_params.get('state')
    idd = id.split('-')
    p = await Project().get(id=idd[0])
    jb = [j for j in p.get('tasks') if j.get('_id') == id ] 
    if len(jb) > 0:
        job = jb[0] 
    else:
        job={}

    
    def set_state(state):
        if state == None:
            pass
        elif state == "active":
            job['state'] = {'active': True, 'complete': False, 'pause': False, 'terminate': False}
            job['event']['started'] = timestamp()            
        elif state == "completed":
            job['state'] = {'active': False, 'complete': True, 'pause': False, 'terminate': False}
            job['event']['completed'] = timestamp()
            job['progress'] = 100
        elif state == "paused":
            job['state'] = {'active': False, 'complete': False, 'pause': True, 'terminate': False}
            job['event']['paused'].append(timestamp())
        elif state == "resume":
            job['state'] = {'active': True, 'complete': False, 'pause': False, 'terminate': False}
            job['event']['restart'].append(timestamp())

        elif state == "terminated":
            job['state'] = {'active': False, 'complete': False, 'pause': False, 'terminate': True}
            job['event']['terminated'] = timestamp()
        else:
            pass

        result = {
            "active": f"""<span class="badge badge-success">Active {job['event']}</span>""",
            "completed": f"""<span class="badge badge-primary">Completed {job['event']}</span>""",
            "paused": f"""<span class="badge badge-secondary">Paused {job['event']}</span>""",
            "resume": f"""<span class="badge badge-success">Restarted {job['event']}</span>""",

            "terminated": f"""<span class="badge badge-error">Terminated {job['event']}</span>""",

        }        
        return result.get(state)
    job_state = set_state(status)
    await Project().update(data=p)
    
    return HTMLResponse(
        f"""<div uk-alert>
                <a href class="uk-alert-close" uk-close></a>
                <h3>Notice</h3>
                <p>{job_state} </p>
            </div>"""
        )


@router.get('/html_job/{id}')
async def html_job_page(request):
    id = request.path_params.get('id')
    idd = id.split('-')
    project = Project()
    current_paybill =  await RedisCache().get(key="CURRENT_PAYBILL")
    p = await project.get(id=idd[0])
    jb = [j for j in p.get('tasks') if j.get('_id') == id ] 
    if len(jb) > 0:
        job = jb[0] 
    else:
        job={}
    crew_members = len(job.get('crew').get('members'))
    project_phases = project.projectPhases.keys()
    #generator = Project().html_job_page_generator(id=id)
    def test_func(a:str=None):
        return f"tested {a}"
    
    return TEMPLATES.TemplateResponse(
        '/project/jobPage.html', 
        {
            "request": request, 
            "p": p, "job": job, 
            "crew_members": crew_members,
            "project_phases": project_phases,  
            "current_paybill": current_paybill,          
            "test_func": test_func

        }) 


@router.post('/add_job/{id}')
async def add_job(request):
    id = request.path_params.get('id')
    job = {"project_id": id}
    try:
        async with request.form() as form:    
            job["title"] = form.get("title")    
            job["description"] = form.get("description")    
            job["projectPhase"] = form.get("project_phase")    
            job["crew"] = {
                    "name": form.get("crew_name"),
                    "rating": 0,
                    "members": [],
                    "event": {
                    "created": form.get("date"),
                    "activated": None,
                    "terminated": None
                    },
                    "state": {
                    "enabled": True,
                    "active": False,
                    "terminated": False
                    }
                }
            job["worker"] = form.get("worker")
            job["tasks"] = []
            job["event"] = {
                    "started": 0,
                    "completed": 0,
                    "paused": [],
                    "restart": [],
                    "terminated": 0,
                    "created": form.get("date")
                }
            job["state"] =  {
                    "active": False,
                    "completed": False,
                    "paused": False,
                    "terminated": False
                }
            job["fees"] = {
                    "contractor": form.get("fees_contractor"),
                    "misc": form.get("fees_misc"),
                    "insurance": form.get("fees_insurance"),
                    "overhead": form.get("fees_overhead"),
                    "unit": "%"
                }
            job["cost"] = {
                    "task": 0,
                    "contractor": 0,
                    "misc": 0,
                    "insurance": 0,
                    "overhead": 0,
                    "total": {
                    "metric": 0,
                    "imperial": 0
                    },
                    "unit": "$"
                }
            job["result"] = {
                    "paid": False,
                    "payamount": 0,
                    "paydate": None
                }
            job["progress"] =  0

        await Project().addJobToQueue(id=id, data=job)
            
          
        return HTMLResponse(f"""<div>{job}</div>""")
    except Exception as e:
        return HTMLResponse(f"""<p class="bg-red-400 text-red-800 text-2xl font-bold py-3 px-4"> An error occured! ---- {str(e)}</p> """)

    finally:
        del(job)
        

@router.post('/add_worker_to_job_crew')
async def add_worker_to_job_crew(request):
    
    async with request.form() as form:
        wid = form.get('worker')
    idds = wid.split("_")
    idd = idds[0].split("-")
    p = await Project().get(id=idd[0])
    jb = [j for j in p.get('tasks') if j.get('_id') == idds[1] ] 
    worker = [w for w in p.get('workers', []) if w.get('id') == idds[0] ] 
    if len(jb) > 0:
        job = jb[0] 
    else:
        job={}
    
    job['crew']['members'].append(worker[0])
    await Project().update(data=p)


    return HTMLResponse(f"""<div uk-alert>
                            <a href class="uk-alert-close" uk-close></a>
                            <h3>Notice</h3>
                            <p>{worker[0].get('value').get('name')} is added to Job {idds[1]}.</p>
                        </div>""")


@router.post('/add_daywork/{id}')
async def add_daywork(request):
    id = request.path_params.get('id')
    payload = {"project_id": id}
    try:
        async with request.form() as form:    
            payload["form_data"] = form         
            for key in form.items():
                payload[key] = form.get(key) 
          
        return HTMLResponse(f"""<div>{payload}</div>""")
    except Exception as e:
        return HTMLResponse(f"""<p class="bg-red-400 text-red-800 text-2xl font-bold py-3 px-4"> An error occured! ---- {str(e)}</p> """)

    finally:
        del(payload)


@router.post('/add_job_task')
async def add_job_task(request):
    async with request.form() as form:
        data = form.get('task')
    idd = data.split('-')
    p = await Project().get(id=idd[0])
    jb = [j for j in p.get('rates') if j.get('_id') == f"{idd[0]}-{idd[1]}" ] 
    if len(jb) > 0:
        task = jb[0] 
    else:
        task={}
    await Project().addTaskToJob(id=f"{idd[0]}-{idd[3]}", data=task)
    return HTMLResponse(f"""<div uk-alert>
                            <a href class="uk-alert-close" uk-close></a>
                            <h3>Notice</h3>
                            <p>{task.get('title')} is added to Job {idd[3]}.</p>
                        </div>""")


@router.post('/add_job_crew')
async def add_job_crew(request):
    async with request.form() as form:
        data = form.get('crew')
    idd = data.split('-')
    p = await Project().get(id=idd[0])
    jb = [j for j in p.get('rates') if j.get('_id') == f"{idd[0]}-{idd[1]}" ] 
    if len(jb) > 0:
        task = jb[0] 
    else:
        task={}
    await Project().addTaskToJob(id=f"{idd[0]}-{idd[3]}", data=task)
    return HTMLResponse(f"""<div uk-alert>
                            <a href class="uk-alert-close" uk-close></a>
                            <h3>Notice</h3>
                            <p>{task.get('title')} is added to Job {idd[3]}.</p>
                        </div>""")



@router.post('/update_job_phase/{id}')
async def update_job_phase(request):
    id = request.path_params.get('id')
    async with request.form() as form:
        phase_resuest = form.get('projectphase')
    job_phase = await Project().update_project_job_phase(id=id, phase=phase_resuest)
    return HTMLResponse(f""" <div uk-alert>
                            <a href class="uk-alert-close" uk-close></a>
                            <h3>Notice</h3>
                            <p>{job_phase }.</p>
                        </div>
    """)



@router.post('/add_worker_to_project')
async def add_worker_to_project(request):
    async with request.form() as form:
        data = form.get('employee')
    idd = data.split('-')
    p = await Project().get(id=idd[0])
    employees = await Employee().all_workers()
    employee = [e for e in employees.get('rows') if e.get('id') == idd[1]][0]
    employee['id'] = data
    p['workers'].append(employee)
    await Project().update(p)
    return HTMLResponse(f"""<div uk-alert>
                            <a href class="uk-alert-close" uk-close></a>
                            <h3>Notice</h3>
                            <p>{employee.get('value').get('name')} is employed to Job {p.get('name')}.</p>
                        </div>""")


@router.post('/new_paybill/{id}')
async def new_paybill(request):
    bill_refs = set()
    id = request.path_params.get('id')
    project = await Project().get(id=id)
    paybill = {'project_id': id, 'items': [], 'fees': {}, 'itemsTotal': 0, 'total': 0}
    for bill in project.get('account').get('records').get('paybills') :
        bill_refs.add(bill.get('ref'))
   

    try:
        async with request.form() as form:    
              
            for key in form:
                paybill[key] = form.get(key) 
        paybill['ref'] = f"{id}-{paybill['ref']}"
        if paybill.get('ref') in bill_refs:
             return HTMLResponse(f"""<div uk-alert>
                            <a href class="uk-alert-close" uk-close></a>
                            <h3>Notice</h3>
                            <p>That Paybill already exists! .</p>
                        </div>""")
        else:
            project['account']['records']['paybills'].append(paybill)    
            await Project().update(data=project)

            return HTMLResponse(f"""<div uk-alert>
                            <a href class="uk-alert-close" uk-close></a>
                            <h3>Notice</h3>
                            <p>{paybill}</p>
                        </div>""")
    except Exception as e:
        return HTMLResponse(f"""<p class="bg-red-400 text-red-800 text-2xl font-bold py-3 px-4"> An error occured! ---- {str(e)}</p> """)

    finally:
        del(paybill)

@router.get('/paybill/{id}')
async def get_paybill(request):
    id = request.path_params.get('id')
    idd = id.split('-')
    project = await Project().get(id=idd[0])

    try:
        bill = [bill for bill in project.get('account').get('records').get('paybills') if bill.get('ref') == id ]
        return TEMPLATES.TemplateResponse(
            '/project/account/projectPaybill.html',
            {"request": request, "bill": bill[0] })
    except Exception as e:
        return HTMLResponse(f"""<p class="bg-red-400 text-red-800 text-2xl font-bold py-3 px-4"> An error occured! ---- {str(e)}</p> """)

    finally:
        del(bill)
            

@router.post('/current_paybill/{id}')
async def current_paybill(request):
    id = request.path_params.get('id')
    
    try:
        await RedisCache().set(key="CURRENT_PAYBILL", val=id)
        
          
        return HTMLResponse(f"""<div uk-alert>
                            <a href class="uk-alert-close" uk-close></a>
                            <h3>Notice</h3>
                            <p>Current Paybill is {id}.</p>
                        </div>""")
    except Exception as e:
        return HTMLResponse(f"""<p class="bg-red-400 text-red-800 text-2xl font-bold py-3 px-4"> An error occured! ---- {str(e)}</p> """)

    finally:
        del(id)


@router.post('/delete_paybill/{id}')
async def delete_paybill(request):
    id = request.path_params.get('id')
    idd = id.split('-')
    project = await Project().get(id=idd[0])

    try:
        for bill in project.get('account').get('records').get('paybills'):
            if bill.get('ref') == id:
                project['account']['records']['paybills'].remove(bill)
        await Project().update(data=project)
        return HTMLResponse(f"""<div uk-alert>
                            <a href class="uk-alert-close" uk-close></a>
                            <h3>Notice</h3>
                            <p>Bill with Ref {id} deleted from Records.</p>
                        </div>""")
    except Exception as e:
        return HTMLResponse(f"""<p class="bg-red-400 text-red-800 text-2xl font-bold py-3 px-4"> An error occured! ---- {str(e)}</p> """)

    finally:
        del(id)



