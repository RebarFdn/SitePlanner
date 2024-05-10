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
    id = request.path_params.get('id')
    e = await Employee().get_worker(id=id)
    
    return HTMLResponse(f"""
                        <div>
                        <div class="navbar">
                            <div class="navbar-start">
                                <div class="avatar">
                                    <img src="{e.get('imgurl')}" alt="avatar" />
                                </div>
                                 <a class="navbar-item">{e.get('oc')}</a>
                            </div>
                            <div class="navbar-end">
                                <a class="navbar-item">Home</a>
                                <a class="navbar-item">About</a>
                                <a class="navbar-item">Contact</a>
                            </div>
                        </div>

                            <div class="flex flex-row py-5 pv-5 space-y-1.5">
                            <div class="avatar avatar-xl avatar-square">
                                <img class="w-32" src="{e.get('imgurl')}" alt="avatar" />
                            </div>
                               
                                <div class="bg-gray-300 p-5 border rounded">{e.get('address')}</div>
                                </div
                                <div class="flex flex-col space-y-1.5">
                                <div class="bg-gray-300 p-5 border rounded">{e}</div>
                                </div>
                        </div>
                        """
                        )
    
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
            payload['address'] = {
                'lot': form.get('lot'),
                'street': form.get('street'),
                  'town': form.get('town'),
                   'city_parish': form.get('city_parish'),
                  
                
                }
            payload['contact'] = {
                'tel': form.get('tel'),
                'mobile': form.get('mobile'),
                'email': form.get('email'),
                
            }
            payload['account'] = {
                
            }
            
            for key in form:
                payload[key] = form.get(key)                
              
        return HTMLResponse(f"""<p class="bg-blue-800 text-white text-sm font-bold py-3 px-4 mx-5 my-2 rounded-md">{payload }</p>""")
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