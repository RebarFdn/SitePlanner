# Base Router 
from starlette.responses import HTMLResponse, RedirectResponse, JSONResponse, StreamingResponse
from decoRouter import Router
from modules.rate import Rate
from modules.supplier import Supplier
from modules.equipment import Equipment




router = Router()

# Employee Related routes  

@router.get('/rates_html_table/')
async def html_table(request):
    return StreamingResponse(Rate().html_table_generator(), media_type="text/html")

@router.get('/rates_html_table/{filter}')
async def html_table_filtered(request):
    filter_request = request.path_params.get('filter')
    return StreamingResponse(Rate().html_table_generator(filter=filter_request), media_type="text/html")


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
    html = await Rate().get_html_rate(id=id)
    return HTMLResponse( html )
