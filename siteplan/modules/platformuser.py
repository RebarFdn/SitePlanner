#modeler.py
#import aiohttp

from starlette.responses import JSONResponse
from decoRouter import Router
try:
    from modules.utils import timestamp
except ImportError:
    from utils import timestamp

from database import Recouch

#from memory_profiler import profile

#fp=open('mem_pflr.log', 'w+')


class User:    
    uernames:list=[]
    meta_data:dict = {
        "created": 0, 
        "database": {"name":"site-users", "partitioned": False},
        "img_url": None       
    }
    
    def __init__(self, data:dict=None) -> None:
        self.conn = Recouch(local_db=self.meta_data.get('database').get('name'))
        self._id:str = None    
        self.meta_data["created"] = timestamp()
        self.index:set = set()
        self.user:dict = {}
        if data:
            self.data = data
            if self.data.get("_id"):
                pass
            else:               
                self.generate_id()
          
    #@profile
    async def mount(self, data:dict=None) -> None:        
        if data:
            self.data = data
            if self.data.get("_id"):
                pass
            else:
                self.generate_id()
            await self.setup

    #@profile
    async def all(self):
        try:
            r = await self.conn.get(_directive="_design/auth/_view/name_index") 
            return r.get('rows')           
        except Exception as e:
            return {'error': str(e)}
        finally: del(r)

    
    #@profile(precision=4, stream=fp)
    async def nameIndex(self):
        def processIndex(p):
            return  p.get('value')
        r = None
        try:
            r = await self.conn.get(_directive="_design/users-index/_view/name-view") 
            return list(map( processIndex,  r.get('rows')))            
        except Exception as e:
            {'error': str(e)}
        finally: del(r)


    #@profile
    async def get(self, id:str=None):
        r = None
        try:
            r = await self.conn.get( _directive=id) 
            return r  
        except Exception as e:
            {'error': str(e)}
        finally: del(r)

    #@profile
    async def save(self): 
        uss = await self.all()
        check_list = [i.get('value').get('email') for i in uss]
        
        if self.data.get('email') in check_list:
            return {"status": 409, "message": "Conflict"} 
        else:
            try:
                await self.conn.post( json=self.data)
               
                return {"status": 202, "message": "Accepted"}
            except Exception as e:                
                return {"status": 500, "message": "Internal Server Error"}

                

    #@profile
    async def update(self, data:dict=None):
        if '_rev' in list(data.keys()): del(data['_rev'])
        try: return await self.conn.put(json=data)            
        except Exception as e: return {'error': str(e)}        

    #@profile
    async def delete(self, id:str=None):        
        try: return await self.conn.delete(_id=id)
        except Exception as e: return {'error': str(e)}     

    #@profile
    async def get_elist(self):
        try: return await self.all()            
        except Exception: return {'error': str(Exception)}

    #@profile
    def generate_id(self):
        ''' Generates a unique user id, also updates the User data''' 
        if self.data.get('email'):
            self.data["_id"] = self.data.get("email")
        else:
            from modules.utils import GenerateId 
            ln = None      
            gen = GenerateId()
            try:
                ln = self.data.get('name').split(' ')            
                self._id =  gen.name_id(ln=ln[1], fn=self.data.get('name'))
            except: self._id = gen.name_id('C', 'P')
            finally:
                self.data['_id']=self._id
                del(ln)
                del(gen)
                del(GenerateId)
                return self._id

    #@profile    
    async def make_password(self, raw_text:str=None):
        from werkzeug.security import generate_password_hash
        try: return  generate_password_hash(raw_text, method='pbkdf2:sha256', salt_length=8)
        except: return None
        finally: del generate_password_hash
    
    #@profile
    async def check_password(self, password_hash, raw_text):
        from werkzeug.security import check_password_hash
        try: return check_password_hash( password_hash, raw_text)
        except Exception: return False
        finally: del(check_password_hash)

    async def hash_user_password(self):
        if self.data and self.data.get('password') and self.data.get('password_confirm'):
            if self.data.get('password') == self.data.get('password_confirm'):
                self.data['password_hash'] = await self.make_password(raw_text=self.data.get('password'))
                del(self.data['password'])
                del(self.data['password_confirm'])

    #@profile
    def update_index(self, data:str) -> None:
        '''  Expects a unique id string ex. JD33766'''        
        self.index.add(data) 


    #@property 
    def list_index(self) -> list:
        ''' Converts set index to readable list'''
        return [item for item in self.index]

    async def process_username(self):
        ln = self.data.get('name').split(' ')
        self.data['username'] = ln[0]       
        check_list = [i.get('value').get('username') for i in await self.all()]
        occurence = 0
        for un in check_list:
            if self.data.get('username') in un:
                occurence += 1
        if occurence == 0:
            pass
        else:
            self.data['username'] = f"{ self.data['username']}-{occurence}"

    #@profile
    @property
    async def setup(self):     

        self.data["imgurl"] = f'{self.data["imgurl"]}{self.data["_id"]}.png'  
        self.data["role"] = "basicuser"
        self.meta_data['img_url'] = self.data["imgurl"]
        self.data['meta_data'] = self.meta_data
        await self.process_username()

    @property
    def user_access_data(self, data:dict=None):
        import json, hashlib
        if data:
            uad = json.loads(json.dumps(data))           
        else:
             uad = json.loads(json.dumps(self.data))            

        if uad.get('meta_data'):
            del(uad['meta_data'])
            del(uad['password_hash'])
                
        return hashlib.md5(json.dumps(uad).encode('utf-8')).hexdigest()
            


# User Router
u_router = Router()

# CREATE NEW
@u_router.post('/register')
async def register_new_user( request ):
    """
    """
    data = await request.json()   
    
    u = User(data=data)      
    await u.hash_user_password()  
    await u.setup
    try:
        #return JSONResponse(u.data)
        result = await u.save()
        if result.get('status') == 202:
            u.data['meta_data']['accessToken'] = u.user_access_data
            del(u.data["password_hash"])
            return JSONResponse(u.data)
        else: return JSONResponse(result)
    except Exception as e: return JSONResponse({"error": str(e)})

@u_router.post('/login')
async def login_user( request ):
    """
    """
    data = await request.json()     
    u = User()
    user = await u.get(id=data.get('email'))      
    
    try:
        #user['meta_data']['accessToken'] = u.user_access_data(data=user)
        del(user["password_hash"])
        return JSONResponse(user)
        
    except Exception as e: return JSONResponse({"error": str(e)})

# All
@u_router.get('/users')
async def get_all_users( request ):
    u = User()
    try:
        return JSONResponse(await u.all())
    except Exception as e:
        return JSONResponse({"error": str(e)}) 
    
