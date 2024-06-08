# Base Router 
from starlette.responses import HTMLResponse, RedirectResponse, JSONResponse, StreamingResponse
from decoRouter import Router
from modules.rate import Rate
from modules.supplier import Supplier
from modules.equipment import Equipment
from config import TEMPLATES




router = Router()

# Employee Related routes  

@router.get('/rates_html_table/')
async def rates_html_table(request):
    return StreamingResponse(Rate().html_table_generator(), media_type="text/html")

@router.get('/industry_rates/{filter}')
async def industry_rates(request):
    store_room = request.app.state.STORE_ROOM
    filter = request.path_params.get('filter')
    rates = await Rate().all_rates()
    categories = {rate.get('category') for rate in rates }
    if filter:
        store_room['filter'] = filter
        if filter == 'all' or filter == 'None':            
            filtered = rates
        else:
            filtered = [rate for rate in rates if rate.get("category") == filter]
    return TEMPLATES.TemplateResponse('/rate/industryRates.html', {
        "request": request,
        "filter": filter,
        "rates": rates,
        "categories": categories,
        "filtered": filtered,
        "store_room":  store_room

    }
                                      )


@router.get('/rates_html_index/')
async def get_rates_html_index(request):    
    return StreamingResponse(Rate().html_index_generator(), media_type="text/html")


@router.get('/rates_html_index/{filter}')
async def get_filtered_rates_html_index(request):
    filter_request = request.path_params.get('filter')
    return StreamingResponse(Rate().html_index_generator(filter=filter_request), media_type="text/html")

@router.get('/rate/{id}')
async def get_rate(request):
    id = request.path_params.get('id')
    rate = await Rate().get(id=id)
    return TEMPLATES.TemplateResponse('/rate/industryRate.html', {"request": request, "rate": rate, "task": rate} )
