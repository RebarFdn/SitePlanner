import json
import asyncio
from starlette.responses import HTMLResponse, RedirectResponse
from decoRouter import Router
from database import RedisCache
from modules.platformuser import User, timestamp
from config import TEMPLATES
router = Router()


async def loadusers( usr:dict = None):

    data = await User().nameIndex()
    if data:
        if usr:
            data.append(usr)

        return data
    else:
        return []


@router.GET('/register')
@router.POST('/register')
async def register(request):
    form = f"""<form action="/register" method="post">
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
                                <div class="flex rounded-lg shadow-sm mb-5">
                                    <span class="px-4 inline-flex items-center min-w-fit rounded-s-md border border-e-0 border-gray-200 bg-gray-50 text-sm text-gray-500 dark:bg-gray-700 dark:border-gray-700 dark:text-gray-400">
                                    Full Name
                                    </span>
                                    <input 
                                        type="text" 
                                        class="py-2 px-3 pe-11 block w-full border-gray-200 shadow-sm rounded-e-lg text-sm focus:z-10 focus:border-blue-500 focus:ring-blue-500 disabled:opacity-50 disabled:pointer-events-none dark:bg-slate-900 dark:border-gray-700 dark:text-gray-400 dark:focus:ring-gray-600"
                                        name="name"
                                        >
                                </div>
                            </div>
                            <div>
                                <div class="flex rounded-lg shadow-sm mb-5">
                                    <span class="px-4 inline-flex items-center min-w-fit rounded-s-md border border-e-0 border-gray-200 bg-gray-50 text-sm text-gray-500 dark:bg-gray-700 dark:border-gray-700 dark:text-gray-400">
                                    Email
                                    </span>
                                    <input 
                                        type="email" 
                                        class="py-2 px-3 pe-11 block w-full border-gray-200 shadow-sm rounded-e-lg text-sm focus:z-10 focus:border-blue-500 focus:ring-blue-500 disabled:opacity-50 disabled:pointer-events-none dark:bg-slate-900 dark:border-gray-700 dark:text-gray-400 dark:focus:ring-gray-600"
                                        name="email"
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
                            <div>
                                <div class="flex rounded-lg shadow-sm">
                                    <span class="px-4 inline-flex items-center min-w-fit rounded-s-md border border-e-0 border-gray-200 bg-gray-50 text-sm text-gray-500 dark:bg-gray-700 dark:border-gray-700 dark:text-gray-400">
                                    Verify Password
                                    </span>
                                    <input 
                                        type="password" 
                                        class="py-3 px-4 pe-11 block w-full border-gray-200 shadow-sm rounded-e-lg text-sm focus:z-10 focus:border-blue-500 focus:ring-blue-500 disabled:opacity-50 disabled:pointer-events-none dark:bg-slate-900 dark:border-gray-700 dark:text-gray-400 dark:focus:ring-gray-600"
                                        name="verify_password"
                                    >
                                </div>
                            </div>
                        <div class="my-5">
                        <button 
                            type="submit" 
                                  
                            class="py-3 px-4 inline-flex items-center gap-x-2 text-sm font-semibold rounded-lg border border-transparent bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50 disabled:pointer-events-none dark:focus:outline-none dark:focus:ring-1 dark:focus:ring-gray-600"
                            >
                                Register
                            </button>
                        </div>

                                
                        </form> 
            """
    if request.method == 'GET':
        return HTMLResponse(form)
    if request.method == 'POST': 
        
        async with request.form() as rform:
            if rform.get('password') == rform.get('verify_password'):
                password_hash = await User().make_password(raw_text=rform.get('password'))
                data = {
                    "username": rform.get("username"),
                    "name": rform.get("name"),
                    "email": rform.get("email"),
                    "password_hash": password_hash
                }
                user = User(data=data)
                await user.save()
                       
                return RedirectResponse(url='/', status_code=303)
            else:
                return HTMLResponse(f"""<div>Password Mismatch<div>""")
    

@router.GET('/login')
@router.POST('/login')
async def login(request):
    
    database = await loadusers()
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
        session = await RedisCache().get(key="SESSION_USER") 
      
        if session:
            return RedirectResponse(url='/dash', status_code=303)
        else:
            return TEMPLATES.TemplateResponse('/auth/login.html', {'request': request})
    if request.method == 'POST': 
        database = await loadusers()
        async with request.form() as rform:
            username = rform.get('username')
            password = rform.get('password')
        #print(username, password)
        
        authed_user = [user for user in database if user.get('username') == username and await User().check_password(password_hash=user.get('password_hash'), raw_text= password)]
        if len(authed_user ) > 0:
            authed_user = authed_user[0]
            print('AUTHED --', authed_user)
            session = {
                "_id": authed_user.get('username'),
                "user": {
                    "username": authed_user.get('username'),
                    "name": authed_user.get('name'),
                    "email": authed_user.get('email')
                },
                "login_time": timestamp(),
                "settings": {
                    "theme": "",
                },
                "log": []

            }
            await RedisCache().set(key="SESSION_USER", val= json.dumps(session))
            return RedirectResponse(url='/dash', status_code=303)
        else:
            return RedirectResponse(url='/', status_code=303)


@router.GET('/logout')
async def logout(request):
    await asyncio.sleep(1)
    await RedisCache().delete(key="SESSION_USER")
    return RedirectResponse(url='/', status_code=303)

@router.GET('/siteusers')
async def siteusers(request):
    users = await User().nameIndex()
    return HTMLResponse(f"""<div>{users}</div>""")

