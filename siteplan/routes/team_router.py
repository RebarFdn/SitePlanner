# Team Router 
from starlette.responses import HTMLResponse, RedirectResponse, JSONResponse, StreamingResponse
from decoRouter import Router
from modules.project import Project
from modules.employee import Employee

router = Router()

# Employee Related routes  
@router.get('/team')
async def team(request): 
    return StreamingResponse(Employee().team_index_generator(), media_type="text/html")



@router.get('/team/{id}')
async def team_member(request):    
    return HTMLResponse(await Employee().html_worker(id=request.path_params.get('id')))

@router.get('/team_json/{id}')
async def team_json(request):  
  return JSONResponse( await Employee().get_worker(id=request.path_params.get('id')))



@router.post('/newworker')
async def new_worker(request):
    payload = {}
    try:
        async with request.form() as form:            
            payload['name'] = form.get('name')
            payload['oc'] = form.get('oc')
            payload['sex'] = form.get('sex')
            payload['dob'] = form.get('dob')
            payload['height'] = form.get('height')
            payload['identity'] = form.get('identity')
            payload['id_type'] = form.get('id_type')
            payload['trn'] = form.get('trn')
            payload['occupation'] = form.get('occupation')
            payload['rating'] = form.get('rating')
            payload['imgurl'] = ""
            payload['address'] = {
                'lot': form.get('lot'),
                'street': form.get('street'),
                  'town': form.get('town'),
                   'city_parish': form.get('city_parish')
                  
                
                }
            payload['contact'] = {
                'tel': form.get('tel'),
                'mobile': form.get('mobile'),
                'email': form.get('email')
                
            }
            payload['account'] = {
                "bank": {
                "name": form.get('bank'),
                "branch": form.get('bank_branch'),
                "account": form.get('account_no'),
                "account_type": form.get('account_type')
                },
                "payments": [],
                "loans": []
                
            }
            payload["nok"] = {
                "name": form.get('kin_name'),
                "relation": form.get('kin_relation'),
                "address": form.get('kin_address'),
                "contact":  form.get('kin_contact')
            }
            payload[ "tasks"] = []
            payload["jobs"] = []
            payload["days"] =  []
            payload["earnings"] = []
            payload["state"] = {
                "active": True,
                "onleave": False,                
                "terminated": False
            },
            payload["event"] = {
                "started": None,
                "onleave":[] ,
                "restart": [],
                "terminated": None,
                "duration": 0
            },
            payload["reports"] = []
            
        ne = await Employee().save(data = payload)   

              
        return HTMLResponse(f"""<p class="bg-blue-800 text-white text-sm font-bold py-3 px-4 mx-5 my-2 rounded-md">{ne }</p>""")
    except Exception as e:
        return HTMLResponse(f"""<p class="bg-red-400 text-red-800 text-2xl font-bold py-3 px-4"> An error occured! ---- {str(e)}</p> """)

    finally:
        del(payload)
        
    
@router.get('/analytics')
async def analytics(request):
    t = f""" 
    <a class="uk-button uk-button-default" href="#modal-sections" uk-toggle>Open</a>

<div id="modal-sections" uk-modal>
    <div class="uk-modal-dialog">
        <button class="uk-modal-close-default" type="button" uk-close></button>
        <div class="uk-modal-header">
            <h2 class="uk-modal-title">Modal Title</h2>
        </div>
        <div class="uk-modal-body">
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>
        </div>
        <div class="uk-modal-footer uk-text-right">
            <button class="uk-button uk-button-default uk-modal-close" type="button">Cancel</button>
            <button class="uk-button uk-button-primary" type="button">Save</button>
        </div>
    </div>
</div>
    
    <table class="uk-table uk-table-divider">
    <thead>
        <tr>
            <th>Table Heading</th>
            <th>Table Heading</th>
            <th>Table Heading</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Table Data</td>
            <td>Table Data</td>
            <td>Table Data</td>
        </tr>
        <tr>
            <td>Table Data</td>
            <td>Table Data</td>
            <td>Table Data</td>
        </tr>
        <tr>
            <td>Table Data</td>
            <td>Table Data</td>
            <td>Table Data</td>
        </tr>
    </tbody>
</table>
"""
    return HTMLResponse(t)