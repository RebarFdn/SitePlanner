## Project router
# This route handles all project related requests 

import json
from starlette.responses import HTMLResponse, RedirectResponse, JSONResponse, StreamingResponse
from starlette_login.decorator import login_required
from decoRouter import Router
from modules.project import Project
from modules.employee import Employee
from modules.utils import timestamp, to_dollars, convert_timestamp
from config import TEMPLATES
from database import RedisCache

router = Router()


@router.GET('/projects')
@login_required
async def get_projects(request):    
    username =  request.user.username        
    p = await Project().all()        
    projects = [project for project in p.get('rows', []) if project.get('value').get("meta_data", {}).get("created_by") == username]
    return TEMPLATES.TemplateResponse('/project/projectsIndex.html',{
        'request': request,
        'projects': projects
    })



@router.get('/project/{id}')
@login_required
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
@login_required
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
@login_required
async def get_project_account_deposits(request):
    id = request.path_params.get('id')
    generator =  Project().html_account_deposits_generator(id=id)
    return StreamingResponse(generator, media_type="text/html")


@router.post('/account_deposit/{id}')
@login_required
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
@login_required
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
@login_required
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
@login_required
async def get_project_account_withdrawals(request):
    id = request.path_params.get('id')
    generator =  Project().html_account_withdrawal_generator(id=id)
    return StreamingResponse(generator, media_type="text/html")


@router.post('/account_withdrawal/{id}')
@login_required
async def project_account_withdrawal(request):
    return HTMLResponse("""<div class="uk-alert-warning" uk-alert>
                        <a href class="uk-alert-close" uk-close></a>
                        <p class="text-sm">Process Not Implemented Yet!.</p>
                    </div>""")


@router.get("/edit_account_withdrawal/{id}")
@login_required
async def edit_account_withdrawal(request):
    return HTMLResponse("""<div class="uk-alert-warning" uk-alert>
                        <a href class="uk-alert-close" uk-close></a>
                        <p class="text-sm">Process Not Implemented Yet!.</p>
                    </div>""")


@router.put('/update_account_withdrawal/{id}')
@login_required
async def update_account_withdrawal(request):
    return HTMLResponse("""<div class="uk-alert-warning" uk-alert>
                        <a href class="uk-alert-close" uk-close></a>
                        <p class="text-sm">Process Not Implemented Yet!.</p>
                    </div>""")


# PROCESS PAYBILLS
@router.get('/project_account_paybills/{id}')
@login_required
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
                 
                },
                "new_billref": f"""Bill-{ len(p.get("account").get('records').get('paybills')) + 1} """
            },
            
        })


@router.get('/paybill_total/{id}')
async def paybill_total(request):   
    id = request.path_params.get('id')

    project = await Project().get(id=id.split('-')[0])
    items_total = 0
    
    for bill in project.get('account').get('records').get('paybills') :
        if bill.get('ref') == id:
            for item in bill.get('items'):
                items_total += float(item.get('metric').get('cost'))
            bill["itemsTotal"] = items_total
            bill["expence"] = {
                "contractor": items_total * ((item.get('fees', {}).get('contractor', 20 )) / 100),
                "insurance": items_total * ((item.get('fees', {}).get('insurance', 5 )) / 100),
                "misc": items_total * ((item.get('fees', {}).get('misc', 5 )) / 100),
                "overhead": items_total *  ((item.get('fees', {}).get('overhead', 5 )) / 100)

            }
            bill["expence"]["total"] = sum([
                bill["expence"]["contractor"],
                bill["expence"]["insurance"],
                bill["expence"]["misc"],
                bill["expence"]["overhead"],
            ])

 

@router.post('/new_paybill/{id}')
@login_required
async def new_paybill(request):
    bill_refs = set()
    id = request.path_params.get('id')
    project = await Project().get(id=id)
    paybill = {
        'project_id': id, 
        'items': [], 
        'fees': {
            "contractor": 10,
            "insurance": 3,
            "misc": 3,
            "overhead": 3,
            "unit": "%"
        }, 
        'itemsTotal': 0, 
        'total': 0
    }
    for bill in project.get('account').get('records').get('paybills') :
        bill_refs.add(bill.get('ref'))
    try:
        async with request.form() as form: 
            for key in form:
                paybill[key] = form.get(key) 
        paybill['ref'] = f"{id}-{paybill['ref']}"
        if paybill.get('ref') in bill_refs:
            return TEMPLATES.TemplateResponse('/project/account/paybills.html', {
                "request": request,
                "paybills":  project.get('account').get('records').get('paybills')
            }) 
        else:
            project['account']['records']['paybills'].append(paybill)    
            await Project().update(data=project)
            return TEMPLATES.TemplateResponse('/project/account/paybills.html', {
                "request": request,
                "paybills":  project.get('account').get('records').get('paybills')
            }) 
    except Exception as e:
        return TEMPLATES.TemplateResponse('/project/account/paybills.html', {
                "request": request,
                "paybills":  project.get('account').get('records').get('paybills')
            }) 
    finally:
        del(paybill)



@router.get('/paybill/{id}')
@login_required
async def get_paybill(request):
    id = request.path_params.get('id')
    idd = id.split('-')
    project = await Project().get(id=idd[0])
    bill = [bill for bill in project.get('account').get('records').get('paybills') if bill.get('ref').strip() == id][0]
    items_total = 0
    try:
        if bill.get('expence'):
            pass
        else:
            bill["expence"] = {
                    "contractor": 0,
                    "insurance": 0,
                    "misc": 0,
                    "overhead": 0,
                    "total": 0

                }       
        
        if len(bill.get('items')) == 0: 
            
            bill['fees'] = Project().default_fees
            await Project().update(data=project)
            return TEMPLATES.TemplateResponse('/project/account/projectPaybill.html',
            {"request": request, "bill": bill, "items_count": len(bill.get('items')) })
        else:

            for item in bill.get('items'):                    
                items_total += float(item.get('metric', {}).get('cost', item.get('metric', {}).get('total', 0))) # check for item cost or total
            
            if bill.get('fees', {}).get('contractor' ):
                bill["expence"]["contractor"] = items_total * ((bill.get('fees').get('contractor' )) / 100)
            else:
                bill['fees']['contractor'] = Project().default_fees.get('contractor') # fallback to default fees
                bill['fees']['unit'] = Project().default_fees.get('unit') # fallback to default fees

                bill["expence"]["contractor"] = items_total * ((bill.get('fees').get('contractor' )) / 100)
            
            if bill.get('fees', {}).get('insurance' ):
                bill["expence"]["insurance"] = items_total * ((bill.get('fees').get('insurance' )) / 100)
            else:
                bill['fees']['insurance'] = Project().default_fees.get('insurance') # fallback to default fees  
                bill["expence"]["insurance"] = items_total * ((bill.get('fees').get('insurance' )) / 100)
            
            if bill.get('fees', {}).get('misc' ):
                bill["expence"]["misc"] = items_total * ((bill.get('fees').get('misc' )) / 100)
            else:
                bill['fees']['misc'] = Project().default_fees.get('misc') # fallback to default fees
                bill["expence"]["misc"] = items_total * ((bill.get('fees').get('misc' )) / 100)
            
            if bill.get('fees', {}).get('overhead' ):
                bill["expence"]["overhead"] = items_total * ((bill.get('fees').get('overhead' )) / 100)
            else:
                bill['fees']['overhead'] = Project().default_fees.get('overhead') # fallback to default fees 
                bill["expence"]["overhead"] = items_total * ((bill.get('fees').get('overhead' )) / 100)
             
            bill["itemsTotal"] = items_total            
            bill["expence"]["total"] = sum([
                    bill["expence"]["contractor"],
                    bill["expence"]["insurance"],
                    bill["expence"]["misc"],
                    bill["expence"]["overhead"],
                ])
            bill['total'] = items_total + bill.get("expence").get("total")
            await Project().update(data=project)

            return TEMPLATES.TemplateResponse(
                '/project/account/projectPaybill.html',
                {"request": request, "bill": bill, "items_count": len(bill.get('items')) })
    except Exception as e:
        return HTMLResponse(f"""<p class="bg-red-400 text-red-800 text-2xl font-bold py-3 px-4"> An error occured! ---- {str(e)}</p> """)

    finally:
        print(f'Done GET /paybill/{id}')
       
            

@router.post('/current_paybill/{id}')
@login_required
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


@router.get('/unpaid_tasks/{id}')
async def unpaid_tasks(request):
    from modules.accumulator import ProjectDataAccumulator    
    id = request.path_params.get('id')
    idd = id.split('-')
    accumulator = ProjectDataAccumulator(project_id=idd[0])
    unpaid_tasks = await accumulator.unpaid_tasks()
    return TEMPLATES.TemplateResponse("/project/account/unpaidTasks.html", {
        "request": request,
        "unpaid_tasks": unpaid_tasks,
        "bill_ref": id
    })
    
@router.post('/add_task_to_bill/{id}')
@login_required
async def add_task_to_bill(request):
    id = request.path_params.get('id')    
    project = await Project().get(id=id.split('-')[0])
    try:
        async with request.form() as form:
            task_id = form.get('task')
        idds = task_id.split('_')
        for job in project.get('tasks'):
            if job.get('_id') == idds[0]:
                for task in job.get('tasks'):
                    if task.get('_id') == idds[1]:
                                   
                        bill_item = {
                                    "id": task.get('_id'),
                                        "job_id": task.get('job_id'),
                                        "title": task.get('title'),
                                        "description": task.get('description'),
                                        "metric": task.get('metric'),
                                        "imperial":task.get('imperial'),
                                        "assignedto": task.get('assignedto'),
                                        "paid": task.get('paid'),
                                        "phase": task.get('phase'),
                                        "progress": task.get('progress'),
                                        "category": task.get('category'),

                                    } 
                        for bill in project.get('account').get('records').get('paybills'):
                            if bill.get('ref') == id:
                                bill['items'].append(bill_item)
            
        await Project().update(data=project)
        """return TEMPLATES.TemplateResponse("/project/account/paybillItem.html", {
            "request": request,
            "bill_items": bill.get('items') })"""
        return RedirectResponse(url=f"/paybill/{id}", status_code=302)
       
    except Exception as e:
        return HTMLResponse(f"""<p class="bg-red-400 text-red-800 text-2xl font-bold py-3 px-4"> An error occured! ---- {str(e)}</p> """)

    finally:
        del(id)


@router.get('/edit_paybill_item/{id}')
@router.post('/edit_paybill_item/{id}')
@login_required
async def edit_paybill_item(request):
    id = request.path_params.get('id')   
    idd = id.split('_')
    project = await Project().get(id=id.split('-')[0])
    paybill = [bill for bill in project.get('account').get('records').get('paybills') if bill.get('ref') == idd[0]][0]
    bill_item = [item for item in paybill.get('items') if item.get('id') == idd[1]][0]
    #print(bill_item)
    if request.method == 'GET':
        
        return TEMPLATES.TemplateResponse('/project/account/editPaybillItem.html', {
            "request": request, 
            "bill_item": bill_item,
            "bill_ref": idd[0]
            
            }  )
    if request.method == 'POST':
        async with request.form() as form:
        
            updates = {
                "id": form.get('id'),
                
            }
            bill_item['id'] = form.get('id')
            if form.get('description'):
                bill_item['description'] = form.get('description')
            if form.get('title'):
                bill_item['title'] = form.get('title')
            bill_item['metric']['unit'] = form.get('metric_unit')
            bill_item['metric']['quantity'] = form.get('metric_quantity')
            bill_item['metric']['price'] = form.get('metric_price')
            bill_item['metric']['cost'] = round(float(bill_item['metric']['quantity']) * float(bill_item['metric']['price']),2)
            
        await Project().update(data=project)

        return RedirectResponse(url=f"/paybill/{idd[0]}", status_code=302)
    

@router.get('/update_contractor_fee/{id}')
@router.post('/update_contractor_fee/{id}')
@login_required
async def update_contractor_fee(request):
    id = request.path_params.get('id')   
   
    project = await Project().get(id=id.split('-')[0])
    paybill = [bill for bill in project.get('account').get('records').get('paybills') if bill.get('ref') == id ][0]
    
    if request.method == 'GET':
        
        response =f"""
        
            <form><input 
                            type="range" 
                            class="range range-secondary" 
                            name="contractor_fee"
                            min="0"
                            max="40"
                            step="1"
                            value="{paybill.get('fees').get('contractor')}"
                            hx-post="/update_contractor_fee/{paybill.get('ref')}"
                            hx-target="#account"
                            hx-trigger="change delay:500ms"
                            />
                        </form>{paybill.get('fees').get('contractor')}
            </p>
        
        """ 
        
            
    if request.method == 'POST':
        async with request.form() as form:
            fee = int(form.get('contractor_fee'))
            
        paybill['fees']['contractor'] = fee
        await Project().update(data=project)
        return RedirectResponse(url=f"/paybill/{id}", status_code=302)
    return HTMLResponse(response)
    


@router.get('/update_insurance_fee/{id}')
@router.post('/update_insurance_fee/{id}')
@login_required
async def update_insurance_fee(request):
    id = request.path_params.get('id')  
    project = await Project().get(id=id.split('-')[0])
    paybill = [bill for bill in project.get('account').get('records').get('paybills') if bill.get('ref') == id ][0]    
    if request.method == 'GET':        
        response =f"""        
            <form><input 
                            type="range" 
                            class="range range-secondary" 
                            name="insurance_fee"
                            min="0"
                            max="40"
                            step="1"
                            value="{paybill.get('fees').get('insurance')}"
                            hx-post="/update_insurance_fee/{paybill.get('ref')}"
                            hx-target="#account"
                            hx-trigger="change delay:500ms"
                            />
            </form>
            <p>{paybill.get('fees').get('insurance')}</p>
        
        """  
    if request.method == 'POST':
        async with request.form() as form:
            fee = int(form.get('insurance_fee'))            
        paybill['fees']['insurance'] = fee
        await Project().update(data=project)
        return RedirectResponse(url=f"/paybill/{id}", status_code=302)
    return HTMLResponse(response)
    


@router.get('/update_misc_fee/{id}')
@router.post('/update_misc_fee/{id}')
@login_required
async def update_misc_fee(request):
    id = request.path_params.get('id')  
    project = await Project().get(id=id.split('-')[0])
    paybill = [bill for bill in project.get('account').get('records').get('paybills') if bill.get('ref') == id ][0]    
    if request.method == 'GET':        
        response =f"""        
            <form><input 
                            type="number"                            
                            name="misc_fee"                            
                            step="1"
                            value="{paybill.get('fees').get('misc')}"
                            hx-post="/update_misc_fee/{paybill.get('ref')}"
                            hx-target="#account"
                            hx-trigger="change delay:500ms"
                            />
            </form>
            <p>{paybill.get('fees').get('misc')}</p>
        
        """  
    if request.method == 'POST':
        async with request.form() as form:
            fee = int(form.get('misc_fee'))            
        paybill['fees']['misc'] = fee
        await Project().update(data=project)
        return RedirectResponse(url=f"/paybill/{id}", status_code=302)
    return HTMLResponse(response)



@router.get('/update_overhead_fee/{id}')
@router.post('/update_overhead_fee/{id}')
@login_required
async def update_overhead_fee(request):
    id = request.path_params.get('id')  
    project = await Project().get(id=id.split('-')[0])
    paybill = [bill for bill in project.get('account').get('records').get('paybills') if bill.get('ref') == id ][0]    
    if request.method == 'GET':        
        response =f"""        
            <form><input 
                            type="range" 
                            class="range range-secondary" 
                            name="overhead_fee"
                            min="0"
                            max="40"
                            step="1"
                            value="{paybill.get('fees').get('overhead')}"
                            hx-post="/update_overhead_fee/{paybill.get('ref')}"
                            hx-target="#account"
                            hx-trigger="change delay:500ms"
                            />
            </form>
            <p>{paybill.get('fees').get('overhead')}</p>
        
        """  
    if request.method == 'POST':
        async with request.form() as form:
            fee = int(form.get('overhead_fee'))            
        paybill['fees']['overhead'] = fee
        await Project().update(data=project)
        return RedirectResponse(url=f"/paybill/{id}", status_code=302)
    return HTMLResponse(response)



@router.get("/project_paybills_cost/{id}")
async def project_paybills_cost(request):
    id = request.path_params.get('id')  
    project = await Project().get(id=id)
    paybills_cost = [bill.get('total', 0) for bill in project.get('account').get('records').get('paybills')  ]
    return TEMPLATES.TemplateResponse(
        "/project/account/projectPaybillsCost.html", 
        {"request": request, "paybills_cost": sum(paybills_cost)}
        )


@router.get("/project_deposits_total/{id}")
async def project_deposits_total(request):
    id = request.path_params.get('id')  
    project = await Project().get(id=id)
    deposits_total = [float(dep.get('amount', 0)) for dep in project.get('account').get('transactions').get('deposit')  ]
    return TEMPLATES.TemplateResponse(
        "/project/account/projectDepositsTotal.html", 
        {"request": request, "deposits_total": sum(deposits_total)}
        )



@router.get("/project_withdrawals_total/{id}")
async def project_withdrawals_total(request):
    id = request.path_params.get('id')  
    project = await Project().get(id=id)
    withdrawals_total = [float(dep.get('amount', 0)) for dep in project.get('account').get('transactions').get('withdraw')  ]
    return TEMPLATES.TemplateResponse(
        "/project/account/projectWithdrawalsTotal.html", 
        {"request": request, "withdrawals_total": sum(withdrawals_total)}
        )


@router.get("/project_expences_total/{id}")
async def project_expences_total(request):
    id = request.path_params.get('id')  
    project = await Project().get(id=id)
    expences_total = [float(exp.get('total', 0)) for exp in project.get('account').get('expences')  ]
    return TEMPLATES.TemplateResponse(
        "/project/account/projectExpencesTotal.html", 
        {"request": request, "expences_total": sum(expences_total)}
        )



@router.get("/project_purchases_total/{id}")
async def project_purchases_total(request):
    id = request.path_params.get('id')  
    project = await Project().get(id=id)
    purchases_total = [float(exp.get('total', 0)) for exp in project.get('account').get('records', {}).get('invoices', [])  ]
    return TEMPLATES.TemplateResponse(
        "/project/account/projectPurchasesTotal.html", 
        {"request": request, "purchases_total": sum(purchases_total)}
        )



@router.get("/project_salaries_total/{id}")
async def project_salaries_total(request):
    id = request.path_params.get('id')  
    project = await Project().get(id=id)
    salaries_total = [float(exp.get('total', 0)) for exp in project.get('account').get('records', {}).get('salary_statements', [])  ]
    return TEMPLATES.TemplateResponse(
        "/project/account/projectSalariesTotal.html", 
        {"request": request, "salaries_total": sum(salaries_total)}
        )


@router.post('/delete_paybill/{id}')
@login_required
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
@login_required
async def get_project_account_salaries(request):
    id = request.path_params.get('id')
    generator = await Project().html_account_salaries_generator(id=id)
    #return StreamingResponse(generator, media_type="text/html")
    return HTMLResponse(f"""<div class="bg-yellow-500 py-5 px-5">{generator}</div>""")


# PROCESS EXPENCES & purchases
@router.get('/project_account_expences/{id}')
@login_required
async def get_project_account_expences(request):
    id = request.path_params.get('id')
    generator = await Project().html_account_expences_generator(id=id)
    #return StreamingResponse(generator, media_type="text/html")
    return HTMLResponse(f"""<div class="bg-yellow-500 py-5 px-5">{generator}</div>""")


@router.get('/project_account_purchases/{id}')
@login_required
async def get_project_account_purchases(request):
    id = request.path_params.get('id')
    generator = await Project().html_account_purchases_generator(id=id)
    #return StreamingResponse(generator, media_type="text/html")
    return HTMLResponse(f"""<div class="bg-yellow-500 py-5 px-5">{generator}</div>""")


## Project Jobs
@router.get('/project_jobs/{id}')
@login_required
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
@login_required
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
@login_required
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
@login_required
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
@login_required
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
@login_required
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
@login_required
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
@login_required
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
@login_required
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
@login_required
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
@login_required
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
@login_required
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
@login_required
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
@login_required
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
@login_required
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
@login_required
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
@login_required
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



