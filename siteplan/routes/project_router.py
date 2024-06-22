## Project router
# This route handles all project related requests 

from starlette.responses import HTMLResponse, RedirectResponse, JSONResponse, StreamingResponse
from decoRouter import Router
from modules.project import Project
from modules.employee import Employee
from modules.utils import timestamp, to_dollars, convert_timestamp
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
    p = await Project().get(id=id)
    return TEMPLATES.TemplateResponse('/project/account/accountPage.html', {
        "request": request,
        "id": id,
        "name": p.get('name'),
        "account": p.get('account')
        })

# PROCESS DEPOSITS
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


@router.get("/edit_account_deposit/{id}")
async def edit_account_deposit(request):
    id = request.path_params.get('id')
    idd = id.split('_')
    did = idd[1].split('-')
    p = await Project().get(id=idd[0])
    account = p.get('account')
    deposit = [dep for dep in account.get('transactions').get('deposit') if dep.get('id') == did[0]][0]

    return TEMPLATES.TemplateResponse("/project/account/editDeposit.html", {
        "request": request, 
        "d": deposit,
        "id": idd[0]

        })


@router.put('/update_account_deposit/{id}')
async def update_account_deposit(request):
    id = request.path_params.get('id')
    p = await Project().get(id=id)
    account = p.get('account')    
    dep = {}
    async with request.form() as form:       
        deposit = [item for item in account.get('transactions').get('deposit') if item.get('id') == form.get('id')][0]
    deposit['ref'] = form.get('ref')
    deposit['amount'] = form.get('amount')
    deposit['payee'] = form.get('payee')
    if len(form.get('date')) > 1:
         deposit['date'] = timestamp(form.get('date'))
    else: pass
    await Project().update(data=p)

    

    return HTMLResponse( f"""
        <div class="uk-alert-success" uk-alert>
            <a href class="uk-alert-close" uk-close></a>
            <p>Account Deposit { deposit.get('ref')} Updated!</p>
            <table  class="uk-table uk-table-small">
                <thead>
                    <tr>
                        <th>Id</th>
                        <th>Date</th>
                        <th>Ref</th>
                        <th>Amount</th>
                        <th>Payee</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>{deposit.get('id')}</td>
                        <td>{deposit.get('date')}</td>
                        <td>{deposit.get('ref')}</td>
                        <td>{to_dollars(deposit.get('amount'))}</td>
                        <td>{deposit.get('payee')}</td>

                    </tr>
                </tbody>
            </table>
        </div>
    """)

# PROCESS WITHDRAWALS
@router.get('/project_account_withdrawals/{id}')
async def get_project_account_withdrawals(request):
    id = request.path_params.get('id')
    generator =  Project().html_account_withdrawal_generator(id=id)
    return StreamingResponse(generator, media_type="text/html")


@router.post('/account_withdrawal/{id}')
async def project_account_withdrawal(request):
    return HTMLResponse("""<div class="uk-alert-warning" uk-alert>
                        <a href class="uk-alert-close" uk-close></a>
                        <p class="text-sm">Process Not Implemented Yet!.</p>
                    </div>""")


@router.get("/edit_account_withdrawal/{id}")
async def edit_account_withdrawal(request):
    return HTMLResponse("""<div class="uk-alert-warning" uk-alert>
                        <a href class="uk-alert-close" uk-close></a>
                        <p class="text-sm">Process Not Implemented Yet!.</p>
                    </div>""")


@router.put('/update_account_withdrawal/{id}')
async def update_account_withdrawal(request):
    return HTMLResponse("""<div class="uk-alert-warning" uk-alert>
                        <a href class="uk-alert-close" uk-close></a>
                        <p class="text-sm">Process Not Implemented Yet!.</p>
                    </div>""")


# PROCESS PAYBILLS
@router.get('/project_account_paybills/{id}')
async def get_project_account_paybills(request):
    id = request.path_params.get('id')
    p = await Project().get(id=id)
    
    return TEMPLATES.TemplateResponse('/project/account/projectPaybills.html',
                                      
        {
            "request": request,
            "id": id,
            "p": {
                "_id": p.get('_id'),
                "name": p.get("name"),
                "account": {
                    "records": {
                        "paybills": p.get("account").get('records').get('paybills')
                    }
                 
                }
            }
        })


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
        bill = [bill for bill in project.get('account').get('records').get('paybills') if bill.get('ref') == id][0]
        return TEMPLATES.TemplateResponse(
            '/project/account/projectPaybill.html',
            {"request": request, "bill": bill, "items_count": len(bill.get('items')) })
    except Exception as e:
        return HTMLResponse(f"""<p class="bg-red-400 text-red-800 text-2xl font-bold py-3 px-4"> An error occured! ---- {str(e)}</p> """)

    finally:
        #del(bill)
        print('done')
            

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


# PROCESS SALARIES
@router.get('/project_account_salaries/{id}')
async def get_project_account_salaries(request):
    id = request.path_params.get('id')
    generator = await Project().html_account_salaries_generator(id=id)
    #return StreamingResponse(generator, media_type="text/html")
    return HTMLResponse(f"""<div class="bg-yellow-500 py-5 px-5">{generator}</div>""")


# PROCESS EXPENCES & purchases
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


# PROCESS RATES
@router.get('/project_rates/{id}')
async def get_project_rates(request):
    id = request.path_params.get('id')
    from modules.rate import Rate        
    industry_rates = await Rate().all_rates()
    p = await Project().get(id=id)
    
    return TEMPLATES.TemplateResponse('/project/rates/projectRates.html', 
        {
            "request": request,
            "p": {
                "_id": p.get('_id'),
                "name": p.get('name'),
                "rates": p.get('rates', [])
            },
            "industry_rates": industry_rates
        } )




@router.get('/update_project_job_state/{id}/{state}')
async def update_project_job_state(request):
    id = request.path_params.get('id')
    status = request.path_params.get('state')
    idd = id.split('-')
    current_paybill =  await RedisCache().get(key="CURRENT_PAYBILL")
    categories = set()
    roles = set()
    p = await Project().get(id=idd[0])

    for task_rate in p.get("rates"): # Loads job categories
        categories.add(task_rate.get('category'))

    for worker in p.get("workers"): # Loads job roles
        roles.add(worker.get('value').get('occupation'))

    jb = [j for j in p.get('tasks') if j.get('_id') == id ] 
    if len(jb) > 0:
        job = jb[0] 
    else:
        job={}

    crew_members = len(job.get('crew').get('members'))
    project_phases = Project().projectPhases.keys()

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
    def test_func(a:str=None):
        return f"tested {a}"
    data = {
            "request": request, 
            "p": {
                "name": p.get('name'),
                "rates": p.get('rates'),
                "workers": p.get('workers')

            }, 
            "job": job, 
            "crew_members": crew_members,
            "project_phases": project_phases,  
            "current_paybill": current_paybill,          
            "test_func": test_func,
            "categories": list(categories),
            "job_roles": list(roles)

        }
    
    return TEMPLATES.TemplateResponse(
        '/project/jobPage.html', 
        {
            "request": request, 
            "p": {
                "name": p.get('name'),
                "rates": p.get('rates'),
                "workers": p.get('workers')

            }, 
            "job": job, 
            "crew_members": crew_members,
            "project_phases": project_phases,  
            "current_paybill": current_paybill,          
            "test_func": test_func,
            "categories": list(categories),
            "job_roles": list(roles)

        }) 


@router.get('/html_job/{id}')
async def html_job_page(request):
    id = request.path_params.get('id')
    idd = id.split('-')
    project = Project()
    current_paybill =  await RedisCache().get(key="CURRENT_PAYBILL")
    categories = set()
    roles = set()
    
    p = await project.get(id=idd[0])

    for task_rate in p.get("rates"): # Loads job categories
        categories.add(task_rate.get('category'))

    for worker in p.get("workers"): # Loads job roles
        roles.add(worker.get('value').get('occupation'))
    

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
            "p": {
                "name": p.get('name'),
                "rates": p.get('rates'),
                "workers": p.get('workers')

            }, 
            "job": job, 
            "crew_members": crew_members,
            "project_phases": project_phases,  
            "current_paybill": current_paybill,          
            "test_func": test_func,
            "categories": list(categories),
            "job_roles": list(roles)

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
        
# JOB TASKS
@router.get('/jobtasks/{id}')
async def get_jobtasks(request):
    id = request.path_params.get('id')
    idd = id.split('-')
   
    p = await Project().get(id=idd[0])
    
    jb = [j for j in p.get('tasks') if j.get('_id') == id] 
    if len(jb) > 0:
        job = jb[0] 
    else:
        job={}
    
    return TEMPLATES.TemplateResponse('/project/jobTasks.html',
        {"request": request, "job": job, "standard": p.get('standard')})


@router.delete('/jobtask/{id}')
async def delete_jobtask(request):
    id = request.path_params.get('id')
    idd = id.split('_')
    pid = idd[0].split('-')[0]
    p = await Project().get(id=pid)
    
    jb = [j for j in p.get('tasks') if j.get('_id') == idd[0] ] 
    if len(jb) > 0:
        job = jb[0] 
    else:
        job={}
    task = [t for t in job.get('tasks') if t.get('_id') == idd[1] ][0]
    job['tasks'].remove(task)
    await Project().update(data=p)
    return HTMLResponse(f"<div>{ task.get('title')} was Removed from Job {job.get('title')}</div>")
    


@router.get('/edit_jobtask/{id}')
async def edit_jobtask(request):
    id = request.path_params.get('id')
    idd = id.split('_')
    pid = idd[0].split('-')[0]
    p = await Project().get(id=pid)
    
    jb = [j for j in p.get('tasks') if j.get('_id') == idd[0] ] 
    if len(jb) > 0:
        job = jb[0] 
    else:
        job={}
    task = [t for t in job.get('tasks') if t.get('_id') == idd[1] ] 
    contact = request.app.state
    display = {
        "metric": True,
        "imperial": True
    }
    return TEMPLATES.TemplateResponse('/project/jobTask.html',
        {
            "request": request, 
            "display": display ,
            "task": task[0], 
            "standard": p.get('standard'), 
            "job_id": job.get('_id'), 
            "crew": job.get('crew').get('members'),
            "contact": contact})


@router.post('/assign_task/{id}')
async def assign_task(request):
    id = request.path_params.get('id')
    idd = id.split('_')
    pid = idd[0].split('-')[0]
    p = await Project().get(id=pid)
    
    jb = [j for j in p.get('tasks') if j.get('_id') == idd[0] ] 
    if len(jb) > 0:
        job = jb[0] 
    else:
        job={}
    task = [t for t in job.get('tasks') if t.get('_id') == idd[1] ][0]
    try:
        async with request.form() as form:
            crew_member = form.get('crew_member')
        crew_member = crew_member.split(" ")[0]
        eid = crew_member.split('-')[1]
        #eid = eid.split(" ")[0]
        employee = await Employee().get_worker(id=eid)
        
        if task.get('assigned'):
            if type(task.get('assignedto')) == str:
                task['assignedto'] = []
            else:
                pass
            if eid in task.get('assignedto'):
                return HTMLResponse(f""" 
                    <div class="uk-alert-warning" uk-alert>
                        <a href class="uk-alert-close" uk-close></a>
                        <p class="text-sm">That crew mamber is already on this task.</p>
                    </div>
                    """)
            else:
                task['assignedto'].append(eid)
                if idd[1] in employee.get('tasks'):
                    pass
                else:
                    employee['tasks'].append(idd[1])
                if employee.get('jobs'):
                    if idd[0] in employee.get('jobs'):
                        pass
                    else:
                        employee['jobs'].append(idd[0])
                else:
                    employee['jobs'] = [idd[0]]


                await Project().update(data=p)
                await Employee().update(data=employee)
                return HTMLResponse(f"""
                    <div class="uk-alert-success" uk-alert>
                        <a href class="uk-alert-close" uk-close></a>
                        <p class="text-sm">{employee.get('oc')} has been assigned to task {idd[1]}.</p>
                    </div>
                        
                        """)
        else:
            task['assignedto'] = [eid]
            task['assigned'] = True
            if idd[1] in employee.get('tasks'):
                    pass
            else:
                employee['tasks'].append(idd[1])
            if employee.get('jobs'):
                if idd[0] in employee.get('jobs'):
                    pass
                else:
                    employee['jobs'].append(idd[0])
            else:
                employee['jobs'] = [idd[0]]

            await Project().update(data=p)
            await Employee().update(data=employee)
        return HTMLResponse(f"""
                    <div class="uk-alert-success" uk-alert>
                        <a href class="uk-alert-close" uk-close></a>
                        <p class="text-sm"> {employee.get('oc')}  has been assigned to task {idd[1]}.</p>
                    </div>""")
    except Exception as e:
        return HTMLResponse(f"""<div class="uk-alert-danger" uk-alert>
            <a href class="uk-alert-close" uk-close></a>
            <p>{str(e)}</p>
            </div> """
        )

@router.post("/filter_job_rate/{id}") 
async def filter_job_rate(request):
    id = request.path_params.get('id')
    idd = id.split('-')
        
    p = await Project().get(id=idd[0])  
    async with request.form() as form:
        category = form.get('task_category')
    if category == 'all':
        rates = p.get('rates')
    else:
        rates = [ rate for rate in p.get('rates') if rate.get('category') == category]
    
    return TEMPLATES.TemplateResponse('/project/task/filteredJobRates.html', {
        "request": request,
        "rates": rates,
        "job_id": id
    }) 

@router.post('/clear_task_assignment/{id}')
async def clear_task_assignment(request):
    id = request.path_params.get('id')
    idd = id.split('_')
    pid = idd[0].split('-')[0]
    p = await Project().get(id=pid)
    
    jb = [j for j in p.get('tasks') if j.get('_id') == idd[0] ] 
    if len(jb) > 0:
        job = jb[0] 
    else:
        job={}
    task = [t for t in job.get('tasks') if t.get('_id') == idd[1] ][0]
    try:
        task['assignedto'] = job.get('crew').get('name')
        await Project().update(data=p)

        return HTMLResponse(f""" <div class="bg-teal-300 py-1 px-2">{job.get('crew').get('name')}</div> """)
    except Exception as e:
        return HTMLResponse(f"""<div class="uk-alert-danger" uk-alert>
                <a href class="uk-alert-close" uk-close></a>
                <p>{str(e)}</p>
            </div> """
        )
    finally: # Clean up.
        del(task)
        del(job)
        del(jb)
        del(p)
        del(pid)
        del(idd)
        del(id)



@router.get('/task_properties/{id}/{flag}')
async def get_task_properties(request):
    id = request.path_params.get('id')
    flag = request.path_params.get('flag')
   
    idd = id.split('_')
    pid = idd[0].split('-')[0]
    p = await Project().get(id=pid)
    
    jb = [j for j in p.get('tasks') if j.get('_id') == idd[0] ] 
    if len(jb) > 0:
        job = jb[0] 
    else:
        job={}
    task = [t for t in job.get('tasks') if t.get('_id') == idd[1] ][0]
    task['metric']['total'] = float(task.get('metric').get('quantity')) * float(task.get('metric').get('price'))
    return TEMPLATES.TemplateResponse('/project/task/metricProperties.html', {
        "request": request, "job_id": idd[0], "task": task,"to_dollars": to_dollars})



@router.get('/edit_task_properties/{id}/{flag}')
async def edit_metric_properties(request):
    id = request.path_params.get('id')
    flag = request.path_params.get('flag')
   
    idd = id.split('_')
    pid = idd[0].split('-')[0]
    p = await Project().get(id=pid)
    
    jb = [j for j in p.get('tasks') if j.get('_id') == idd[0] ] 
    if len(jb) > 0:
        job = jb[0] 
    else:
        job={}
    task = [t for t in job.get('tasks') if t.get('_id') == idd[1] ][0]
    if flag == 'metric':
        return TEMPLATES.TemplateResponse('/project/task/editMetric.html', {"request": request, "job_id": idd[0],"task": task})
    else:
        return HTMLResponse("")



@router.put('/update_task_properties/{id}/{flag}')
async def update_metric_properties(request):
    id = request.path_params.get('id')
    flag = request.path_params.get('flag')
   
    idd = id.split('_')
    pid = idd[0].split('-')[0]
    p = await Project().get(id=pid)
    
    jb = [j for j in p.get('tasks') if j.get('_id') == idd[0] ] 
    if len(jb) > 0:
        job = jb[0] 
    else:
        job={}
    task = [t for t in job.get('tasks') if t.get('_id') == idd[1] ][0]
    async with request.form() as form:
        total = float(form.get('quantity')) * float(form.get('price'))
        task['metric']['unit'] = form.get('unit')
        task['metric']['quantity'] = form.get('quantity')
        task['metric']['price'] = form.get('price')
        task['metric']['total'] = total
    await Project().update(data=p)

    return TEMPLATES.TemplateResponse("/project/task/updatedMetric.html", {"request": request, "id": id, "form": form, "total":total})



@router.post('/update_task_progress/{id}')
async def update_task_progress(request):
    id = request.path_params.get('id')
    idd = id.split('_')
    pid = idd[0].split('-')[0]
    p = await Project().get(id=pid)
    
    jb = [j for j in p.get('tasks') if j.get('_id') == idd[0] ] 
    if len(jb) > 0:
        job = jb[0] 
    else:
        job={}
    task = [t for t in job.get('tasks') if t.get('_id') == idd[1] ][0] 
    try:
        async with request.form() as form:
            progress = int(form .get('task_progress'))
        if progress == 100:
            task['state'] = {'active': False, 'complete': True, 'pause': False, 'terminate': False}
            task['event']['completed'] = timestamp()
            task['progress'] = progress
            # Log this update
        else:
            task['progress'] = progress
            #log this event
        await Project().update(data=p)
        return HTMLResponse(f""" {progress}""")
    except Exception as e:
        pass

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
    e = await Employee().get_worker(id=idds[0].split('-')[1])
    if idds[1] in e.get('jobs'):
        pass
    else:
        e['jobs'].append(idds[1])
        await Employee().update( data=e )
    await Project().update(data=p)


    return HTMLResponse(f"""<div uk-alert>
                            <a href class="uk-alert-close" uk-close></a>
                            <h3>Notice</h3>
                            <p>{worker[0].get('value').get('name')} is added to Job {idds[1]}.</p>
                            <p class="text-xs">{e}</p>
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
    e = await Employee().get_worker(id=idd[1])
    if idd[0] in e.get('jobs'):
        pass
    else:
        e['jobs'].append(idd[0])
        await Employee().update(data=e)
    await Project().update(p)
    return HTMLResponse(f"""<div uk-alert>
                            <a href class="uk-alert-close" uk-close></a>
                            <h3>Notice</h3>
                            <p>{employee.get('value').get('name')} is employed to Job {p.get('name')}.</p>
                            
                        </div>""")


@router.post('/update_project_standard/{id}')
async def update_project_standard(request):
    id = request.path_params.get('id')    
    p = await Project().get(id=id)
    try:
        async with request.form() as form:
            standard = form.get('standard')
        if standard == None:
            p['standard'] = "imperial"
            await Project().update(data=p)
            return HTMLResponse("Imperial")
        else:
            p['standard'] = "metric"
            await Project().update(data=p)
            return HTMLResponse("Metric")
    except:
        pass



