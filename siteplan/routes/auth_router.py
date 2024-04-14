from starlette.responses import HTMLResponse, RedirectResponse
from decoRouter import Router

router = Router()


def loadusers( usr:dict = None):

    data = [
       
        {"username": "Tatty", "age": 56 , "password": "hotchick"},
        {"username": "Ian", "age": 53 , "password": "cat"},
        {"username": "Ankh", "age": 32 , "password": "gazaman"},        
        {"username": "Anuk", "age": 23 , "password": "bredda"},
        {"username": "Ausar", "age": 20 , "password": "breddabredda"},
        {"username": "Akari", "age": 0.5 , "password": "chunky"},
    ]
    if usr:
        data.append(usr)
    return data


@router.GET('/login')
@router.POST('/login')
async def login(request):
    form = f"""<form action="/login" method="post">
                            <div>
                                <div class="flex rounded-lg shadow-sm mb-5">
                                    <span class="px-4 inline-flex items-center min-w-fit rounded-s-md border border-e-0 border-gray-200 bg-gray-50 text-sm text-gray-500 dark:bg-gray-700 dark:border-gray-700 dark:text-gray-400">
                                    Username
                                    </span>
                                    <input 
                                        type="text" 
                                        class="py-2 px-3 pe-11 block w-full border-gray-200 shadow-sm rounded-e-lg text-sm focus:z-10 focus:border-blue-500 focus:ring-blue-500 disabled:opacity-50 disabled:pointer-events-none dark:bg-slate-900 dark:border-gray-700 dark:text-gray-400 dark:focus:ring-gray-600"
                                        name="username"
                                        >
                                </div>
                            </div>

                            <div>
                                <div class="flex rounded-lg shadow-sm">
                                    <span class="px-4 inline-flex items-center min-w-fit rounded-s-md border border-e-0 border-gray-200 bg-gray-50 text-sm text-gray-500 dark:bg-gray-700 dark:border-gray-700 dark:text-gray-400">
                                    Password
                                    </span>
                                    <input 
                                        type="password" 
                                        class="py-3 px-4 pe-11 block w-full border-gray-200 shadow-sm rounded-e-lg text-sm focus:z-10 focus:border-blue-500 focus:ring-blue-500 disabled:opacity-50 disabled:pointer-events-none dark:bg-slate-900 dark:border-gray-700 dark:text-gray-400 dark:focus:ring-gray-600"
                                        name="password"
                                    >
                                </div>
                            </div>
                        <div class="my-5">
                        <button 
                            type="submit" 
                            class="py-3 px-4 inline-flex items-center gap-x-2 text-sm font-semibold rounded-lg border border-transparent bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50 disabled:pointer-events-none dark:focus:outline-none dark:focus:ring-1 dark:focus:ring-gray-600"
                            >
                                Login
                            </button>
                        </div>

                                
                        </form> 
            """
    if request.method == 'GET':
        return HTMLResponse(form)
    if request.method == 'POST': 
        database = loadusers()
        async with request.form() as rform:
            username = rform.get('username')
            password = rform.get('password')
        #print(username, password)
        authed_user = [user for user in database if user.get('username') == username and user.get('password') == password]
        if len(authed_user ) > 0:
            return RedirectResponse(url='/dash', status_code=303)
        else:
            return RedirectResponse(url='/', status_code=303)