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

@router.get('/wall')
async def get_wall(request):
    return HTMLResponse(f"""<div class="text-3xl font-semibold">Wall Estimator</div>
                        <section class="bg-gray-2 rounded-xl">
                            <div class="p-8 shadow-lg">
                                <form 
                                    class="space-y-4" 
                                   
                                >
                        <ul class="uk-subnav uk-subnav-pill" uk-switcher>
                            <li><a href="#">Data</a></li>
                            <li><a href="#">Rebar</a></li>
                            <li><a href="#">Opening</a></li>
                        </ul>

                        <div class="uk-switcher uk-margin">
                            <div> <div class="w-full">
                                        <label class="sr-only" for="tag">Tag</label>
                                        <input class="input input-solid max-w-full" placeholder="Wall Tag" type="text" id="tag" name="tag" />
                                    </div>
                                    <div class="w-full">
                                        <label class="sr-only" for="type">Type</label>
                                        <input class="input input-solid max-w-full" placeholder="Wall Type" type="text" id="type" name="type" />
                                    </div>


                                    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
                                        <div>
                                            <label class="sr-only" for="unit">Unit</label>
                                            <input class="input input-solid" placeholder="Unit of measurement" type="text" id="unit" name="unit" />
                                        </div>
                                        <div>
                                            <label class="sr-only" for="thickness">Thickness</label>
                                            <input class="input input-solid" placeholder="Thickness of the wall" type="number" step="0.1" id="thickness" name="thickness" />
                                        </div>
                                        <div>
                                            <label class="sr-only" for="length">Length</label>
                                            <input class="input input-solid" placeholder="Length of the wall" type="number" step="0.1" id="length" name="length" />
                                        </div>

                                        <div>
                                            <label class="sr-only" for="height">Height</label>
                                            <input class="input input-solid" placeholder="Height of the wall" type="number" step="0.1" id="height" name="height" />
                                       </div>
                                    </div>

                                    <div class="w-full">
                                        <label class="sr-only" for="message">Message</label>

                                        <textarea class="textarea textarea-solid max-w-full" placeholder="Message" rows="3" id="message" name="message"></textarea>
                                    </div>
                                </div>
                            <div>
                                    
                                    <div class="uk-child-width-1-2@s uk-grid-collapse uk-text-center" uk-grid>
   
                                        <div>
                                            <div class="uk-tile uk-tile-primary">
                                                <p class="text-3xl font-semibold">Vertical Bars </p>
                                                    <div>
                                                    <label class="sr-only" for="v-bartype">Vertical Bar Type</label>
                                                    <input class="input input-solid max-w-full" placeholder="Bar Type" type="text" id="vbartype" name="vbar_type" />
                                                </div>
                                                <div>
                                                        <label class="sr-only" for="v-barspacing">Spacing</label>
                                                        <input class="input input-solid" placeholder="Bar Spacing" type="number" step="0.1" id="vbar_spacing" name="vbar_spacing" />
                                                </div>
                                            </div>
                                        </div>
                                        <div>
                                            <div class="uk-tile uk-tile-secondary">
                                                <p class="text-3xl font-semibold">Horizontal Bars </p>
                                    <div>
                                        <label class="sr-only" for="h-bartype">Horizontal Bar Type</label>
                                        <input class="input input-solid max-w-full" placeholder="Bar Type" type="text" id="hbartype" name="hbar_type" />
                                    </div>
                                    <div>
                                            <label class="sr-only" for="h-barspacing">Spacing</label>
                                            <input class="input input-solid" placeholder="Bar Spacing" type="number" step="0.1" id="hbar_spacing" name="hbar_spacing" />
                                    </div>
                                            </div>
                                        </div>
                                    </div>
                                    
                        </div>
                            <div>Bazinga!</div>
                        </div>
                                   
                                    <div class="mt-4">
                                        <button 
                                        type="button" 
                                        class="rounded-lg btn btn-primary btn-block"
                                         hx-post="/wall"
                                        hx-target="#e-content"
                                        >Send Enquiry</button>
                                    </div>
                                </form>
                            </div>
                        </section>
                        
                        """)


@router.post('/wall')
async def process_wall(request):
       
    payload = {}
    try:
        async with request.form() as form:            
            payload['tag'] = form.get('tag')        
            payload['type'] = form.get('type')  
            payload['unit'] = form.get('unit') 
            payload['thickness'] = float(form.get('thickness'))         
            payload['length'] = float(form.get('length'))
            payload['height'] = form.get('height')
        wall = Wall(data=payload)
        await wall.load_wall_system
        await wall.generate_report
       
        return HTMLResponse(f""" <div class="uk-alert-success" uk-alert>
                                <a href class="uk-alert-close" uk-close></a>
                                <p>{wall.report}  </p>
                                </div>""")
    except Exception as e:
        return HTMLResponse(f"""
                            <div class="uk-alert-warning" uk-alert>
                                <a href class="uk-alert-close" uk-close></a>
                                <p>{str(e)}</p>
                            </div>
                            """)
    
@router.get('/column')
async def get_column(request):
    return HTMLResponse(f"""<div class="text-3xl font-semibold">Column Estimator</div>
                        <section class="bg-gray-2 rounded-xl">
                            <div class="p-8 shadow-lg">
                                <form 
                                    class="space-y-4" 
                                   
                                >
                                    <div class="w-full">
                                        <label class="sr-only" for="tag">Tag</label>
                                        <input class="input input-solid max-w-full" placeholder="Column Tag" type="text" id="tag" name="tag" />
                                    </div>
                                    <div class="w-full">
                                        <label class="sr-only" for="type">Type</label>
                                        <input class="input input-solid max-w-full" placeholder="Column Type" type="text" id="type" name="type" />
                                    </div>


                                    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
                                        <div>
                                            <label class="sr-only" for="unit">Unit</label>
                                            <input class="input input-solid" placeholder="Unit of measurement" type="text" id="unit" name="unit" />
                                        </div>
                                        <div>
                                            <label class="sr-only" for="thickness">Thickness</label>
                                            <input class="input input-solid" placeholder="Thickness of the Column" type="number" step="0.1" id="thickness" name="thickness" />
                                        </div>
                                        <div>
                                            <label class="sr-only" for="length">Length</label>
                                            <input class="input input-solid" placeholder="Length of the Column" type="number" step="0.1" id="length" name="length" />
                                        </div>

                                        <div>
                                            <label class="sr-only" for="height">Height</label>
                                            <input class="input input-solid" placeholder="Height of the Column" type="number" step="0.1" id="height" name="height" />
                                       </div>
                                    </div>

                                    <div class="w-full">
                                        <label class="sr-only" for="message">Message</label>

                                        <textarea class="textarea textarea-solid max-w-full" placeholder="Message" rows="8" id="message" name="message"></textarea>
                                    </div>

                                    <div class="mt-4">
                                        <button 
                                        type="button" 
                                        class="rounded-lg btn btn-primary btn-block"
                                         hx-post="/column"
                                        hx-target="#e-content"
                                        >Send Enquiry</button>
                                    </div>
                                </form>
                            </div>
                        </section>
                        
                        """)


    
@router.get('/beam')
async def get_beam(request):
    return HTMLResponse(f"""<div class="text-3xl font-semibold">Beam Estimator</div>
                        <section class="bg-gray-2 rounded-xl">
                        <ul class="uk-subnav uk-subnav-pill" uk-switcher>
                            <li><a href="#">Data</a></li>
                            <li><a href="#">Reinforcement</a></li>
                            
                        </ul>

                        <div class="uk-switcher uk-margin">
                            <div class="p-8 shadow-lg">
                                <form 
                                    class="space-y-4" 
                                   
                                >
                                    <div class="w-full">
                                        <label class="sr-only" for="tag">Tag</label>
                                        <input class="input input-solid max-w-full" placeholder="Beam Tag" type="text" id="tag" name="tag" />
                                    </div>
                                    <div class="w-full">
                                        <label class="sr-only" for="type">Type</label>
                                        <input class="input input-solid max-w-full" placeholder="Beam  Type" type="text" id="type" name="type" />
                                    </div>


                                    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
                                        <div>
                                            <label class="sr-only" for="unit">Unit</label>
                                            <input class="input input-solid" placeholder="Unit of measurement" type="text" id="unit" name="unit" />
                                        </div>
                                        <div>
                                            <label class="sr-only" for="thickness">Bredth</label>
                                            <input class="input input-solid" placeholder="Bredth of the Beam " type="number" step="0.1" id="bredth" name="bredth" />
                                        </div>
                                        <div>
                                            <label class="sr-only" for="length">Length</label>
                                            <input class="input input-solid" placeholder="Length of the Column" type="number" step="0.1" id="length" name="length" />
                                        </div>

                                        <div>
                                            <label class="sr-only" for="depth">Depth>
                                            <input class="input input-solid" placeholder="Depth of the Column" type="number" step="0.1" id="depth" name="depth" />
                                       </div>
                                    </div>

                                    <div class="w-full">
                                        <label class="sr-only" for="message">Message</label>

                                        <textarea class="textarea textarea-solid max-w-full" placeholder="Message" rows="3" id="message" name="message"></textarea>
                                    </div>

                                    <div class="mt-4">
                                        <button 
                                        type="button" 
                                        class="rounded-lg btn btn-primary btn-block"
                                         hx-post="/column"
                                        hx-target="#e-content"
                                        >Send Enquiry</button>
                                    </div>
                                </form>
                            </div>
                            <div>Hello again!</div>
                            
                        </div>
                            
                        </section>
                        
                        """)

