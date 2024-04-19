#modeler.py

from modules.utils import timestamp

from database import Recouch

class Employee:
    instances = 0
    _id:str = None   
    data:dict = {}  
    meta_data:dict = {
        "created": timestamp(),
        "database": {
            "name":"site-workers", "partitioned": False,
            "slave":"site-workers", "partitioned": False
            
            },
        "img_url": None      
    }
    index:set = set()
    worker:dict = {}
    workers:list = []

    def __init__(self, data:dict=None) -> None:
        Employee.instances += 1
        self.conn = Recouch(local_db=self.meta_data.get('database').get('name'))
        self.slave = Recouch(local_db=self.meta_data.get('database').get('slave'))
        try:
            if not data:
                self.generate_id()
            else:
                self.data = data
                if self.data.get("_id"):
                    pass
                else: self.generate_id()
        except Exception as e:
            print(e)
    
    def mount(self, data:dict=None) -> None:        
        if data:
            
            self.data = data
            if self.data.get("_id"):
                pass
            else:
                self.generate_id()

    async def all(self):
        try:
            return await self.conn.get(_directive="_all_docs") 
        except Exception as e:
            return {"error": str(e)}

    async def all_workers(self):
        try:
            return await self.slave.get(_directive="_design/workers/_view/name-index") 
        except Exception as e:
            return {"error": str(e)}

    async def get_worker(self, id:str=None):
        self.worker = await self.conn.get(_directive=id) 
        #self.processAccountTotals 
        return self.worker


    async def save(self, data:dict=None):
        self.mount(data=data)
        from asyncio import sleep
        try:
            self.data['imgurl'] = f"static/imgs/workers/{self._id}.png" 
            await self.conn.post( json=self.data)
            await sleep(1)
            self.data['_id'] = self._id                      
            await self.slave.post( json=self.data)                    
            return self.data
        except Exception:
            return {"status": str(Exception)}
        finally: del sleep


    async def update(self, data:dict=None):   
            
        try:
            payload =  await self.conn.put( json=data)
            
            return payload

        except Exception as e:
            return {"error": str(e)}
        finally: pass
        

    async def delete(self, id:str=None):
        worker = await self.get_worker(id=id)
        try:
            res = await self.conn.delete(_id=f"{id}?rev={worker.get('_rev')}")
            return res
        except Exception as e:
            return {"status": str(e)}
        finally:
            del(res); del(worker)       


    async def get_elist(self):
        await self.all_workers()
        return self.workers 
        

    def generate_id(self):
        ''' Generates a unique Worker id, also updates the worker data''' 
        from modules.utils import GenerateId       
        gen = GenerateId()
        try:
            ln = self.data.get('name').split(' ')
            self._id =  gen.name_id(ln=ln[1], fn=self.data.get('name'))   
                
            self.data['_id'] = f"{self.data.get('occupation')}s:{self._id}"    
            self.data[f"{self.data.get('occupation')}_id"] = f"{self.data.get('occupation')}s"                                
        except:
            self._id = gen.name_id('C', 'W')
                
            self.data['_id'] = f"{self.data.get('occupation')}s:{self._id}"    
            self.data[f"{self.data.get('occupation')}_id"] = f"{self.data.get('occupation')}s"
        finally:           
            del(gen)
            del(GenerateId)
 

    @property
    def processAccountTotals(self):
        #function to process pay 
        def processPay(p):
            return p['total']
        self.worker['account']['totals_payments'] = list(map(processPay, self.worker['account']['payments']))   
        self.worker['account']['total'] = sum(self.worker['account']['totals_payments'])   
        

    async def addPay(self, id=None, data=None):       
        try:        
            #get the worker's data
            await self.get_worker(id=id)        
            self.worker['account']['payments'].append(data) 
            self.processAccountTotals        
            await self.update(data=self.worker)
            return self.worker.get('account').get('payments')       
            
        except Exception as ex:
            return {"status": str(ex)}
        
    async def deletePay(self, id:str=None, data:dict=None):
        await self.get_worker(id=id)
        try:
            self.worker['account']['payments'].remove(data)
            await self.update(data=self.worker)
            return self.worker.get('account').get('payments') 
        except Exception as e:
            return str(e)


    async def addJobTask(self, id=None, data=None): 
        '''Assign a task from a job to a worker
            --- Returns a list of tasks of the said job asigned to the worker'''
        
        try:        
            #get the worker's data
            await self.get_worker(id=id)                   
            self.worker['tasks'].append(data)                   
            await self.update(data=self.worker) 
            idds = data.split('-')   
                    
            def process_job_tasks(item):
                if f"{idds[0]}-{idds[1]}" in item:
                    return item
            jobtasks = list(map(process_job_tasks, self.worker.get('tasks')))
            return {"worker": id, "job": f"{idds[0]}-{idds[1]}", "tasks": jobtasks}
            
        except Exception as ex:
            return {"status": str(ex)}
        
    async def submitDayWork(self, eid:str=None, data:dict=None)-> list:
        '''Returns the list of days worked'''
        e = await self.get_worker(id=eid)
        #print(e)
        e['days'].append(data)
        await self.update(data=e)
        return e.get('days')
    
    # Html Responses
    async def team_index_generator(self):
        e = await self.all_workers()
        try:
            yield f"""
                <div class="flex flex-row bg-gray-400 py-2 px-2 text-left rounded relative">
                    <p class="text-left">
                    Team Index
                     <span class="bg-gray-50 ml-10 py-1 px-2 border rounded-full">{len(e.get('rows', []))}<span>
                      
                    </p>   
                   <a href="#new-worker" uk-toggle class="absolute right-0">Employ  .</a>
                </div>"""
            yield '<ul class="mx-2 h-96 overflow-y-auto">'
        
            for employee in e.get('rows', []):
                yield f"""<li class="mt-2">        
                            <div
                                class="p-2 max-w-sm mx-auto bg-white rounded-lg shadow-lg flex items-center space-x-4 cursor-pointer"
                                hx-get="/team/{employee.get('id')}"
                                hx-target="#dash-content-pane"
                                hx-trigger="click"
                            >
                            <div class="shrink-0">
                                <img class="h-12 w-12 rounded-full" src="{employee.get('value').get('imgurl')}" alt="P">
                                <span class="text-xs"> {employee.get('id')}</span>
                            </div>
                            <div>
                                <div class="text-md font-medium text-gray-800"> {employee.get('value').get('name')} </div>
                                <span class="uk-badge">{employee.get('value').get('occupation')}</span>
                                
                            </div></div>
                            </li> """
            yield """</ul></div>

            <!-- This is the modal -->
                        <div id="new-worker" uk-modal>
                            <div class="uk-modal-dialog uk-modal-body">
                                <h2 class="uk-modal-title">Headline</h2>
                                <form>

                                    <div class="uk-margin">
                                        <input class="uk-input uk-form-width-large" type="text" placeholder="Large" aria-label="Large">
                                    </div>

                                    <div class="uk-margin">
                                        <input class="uk-input uk-form-width-medium" type="text" placeholder="Medium" aria-label="Medium">
                                    </div>

                                    <div class="uk-margin">
                                        <input class="uk-input uk-form-width-small" type="text" placeholder="Small" aria-label="Small">
                                    </div>

                                    <div class="uk-margin">
                                        <input class="uk-input uk-form-width-xsmall" type="text" placeholder="X-Small" aria-label="X-Small">
                                    </div>

                                </form>

                                 <FormKit type="form" id="employee-identity-form" @submit="saveWorkerData" >
            <n-grid x-gap="12" :cols="2">
                <n-gi  id="employee-personal">
                    <div class="light-green">                   
                        
                        <FormKit 
                            type="text" 
                            label="Employee Full Name" 
                            v-model="store.newWorker.name"
                            placeholder="John Brown"
                            validation="required|length:3"
                            help="Enter employee full name."
                            />
                        <FormKit 
                            type="text" 
                            label="Employee Alias Name" 
                            v-model="store.newWorker.oc"
                            placeholder="Brownie"
                            validation="required|length:3"
                            help="Enter employee alias name."
                            />
                        <FormKit 
                            type="select" 
                            label="Sex" 
                            v-model="store.newWorker.sex"
                            placeholder="Man Woman or Machine ?"
                            :options="{default:'Sex', male:'Male',female:'Female',robot:'Robot',other:'Other'}"
                            validation="required"
                            help="How many time per day."
                            />
                            <FormKit
                            type="date"
                            label="D.O.B"
                            v-model="store.newWorker.dob"
                            validation="date_before:2008-01-01"                    
                            validation-visibility="live"
                            help="Enter employees date of birth"
                        />
                        <FormKit 
                            type="number" 
                            label="Height" 
                            v-model="store.newWorker.height"
                            placeholder="102 cm"                   
                            help="How tall is the Employee."
                            /> 
   
                    </div>
                </n-gi>
                <n-gi id="employee-identity">
                <div class="green">
                    <FormKit 
                        type="text" 
                        label="Identity" 
                        v-model="store.newWorker.identity"
                        placeholder="PP000000000"                   
                        validation="required"
                        help="Employee's National Identification."
                        />
                    <FormKit 
                        type="select" 
                        label="Id Type" 
                        v-model="store.newWorker.id_type"
                        placeholder="Passport"
                        :options="[{'label':'Id', value : 'default'},{'label':'Drivers  Lic.', value:'drivers'},{'label':'Passport', value:'passport'},{'label':'National', value:'national'}]"
                        validation="required"
                        help="Type of identification."
                        />
                        <FormKit 
                        type="text" 
                        label="T.R.N" 
                        v-model="store.newWorker.trn"
                        placeholder="TRN"                    
                        validation="required"
                        help="Tax Payer Registration Number."
                        />
                        <FormKit 
                        type="select" 
                        label="Employee Occupation" 
                        v-model="store.newWorker.occupation"
                        placeholder="Labourer"
                        :options="jobRoles"
                        validation="required|length:3"
                        help="Select one from the list."
                        />
                        <FormKit 
                        type="select" 
                        label="Rating" 
                        v-model="store.newWorker.rating"
                        :options="[1,2,3,4,5]"
                        placeholder="3 stars"                   
                        :help="`How good a ${store.newWorker.occupation} is the Employee.`"
                        />   
                    </div>
                </n-gi>
            </n-grid>
            <n-divider title-placement="left">
                Contact Information
            </n-divider>
            <n-grid x-gap="12" :cols="2">
                <n-gi  id="employee-contact">
                    
                    <FormKit
                                type="text"
                                label="Phone"
                                v-model="store.newWorker.contact.tel"
                                placeholder="xxx-xxx-xxxx"
                                :validation="[ ['matches', /^\d{3}-\d{3}-\d{4}$/]]"
                                validation-visibility="live"
                                :validation-messages="{
                                    matches: 'Phone number must be formatted: xxx-xxx-xxxx',
                                }"
                        />
                        <FormKit
                                type="text"
                                label="Mobile"
                                v-model="store.newWorker.contact.mobile"
                                placeholder="xxx-xxx-xxxx"
                                :validation="[ ['matches', /^\d{3}-\d{3}-\d{4}$/]]"
                                validation-visibility="live"
                                :validation-messages="{
                                    matches: 'Mobile number must be formatted: xxx-xxx-xxxx',
                                }"
                        />
        
                </n-gi>
                <n-gi  id="employee-contact-ii"> 
           
                    <FormKit
                        label="Email address"
                        v-model="store.newWorker.contact.email"
                        validation="email"
                    />
                    <FormKit
                            type="text"
                            label="WatsApp Contact"
                            v-model="store.newWorker.contact.watsapp"
                            placeholder="xxx-xxx-xxxx"
                            :validation="[['matches', /^\d{3}-\d{3}-\d{4}$/]]"
                            validation-visibility="live"
                            :validation-messages="{
                                matches: 'WatApp contact must be formatted: xxx-xxx-xxxx',
                            }"
                    />
  
 
                </n-gi>
            </n-grid>
            <n-divider title-placement="left">
                Address Information
            </n-divider>
            <n-grid x-gap="12" :cols="2">
                <n-gi >
                <div>
                    <FormKit 
                            type="text" 
                            label="Lot" 
                            v-model="store.newWorker.address.lot"
                            placeholder="4b"
                            help="Employee lot number."
                            />
                    <FormKit 
                            type="text" 
                            label="Street" 
                            v-model="store.newWorker.address.street"
                            placeholder="Some Street"
                            help="Employee lot street name."
                            />
           
                    </div>

                </n-gi>
                <n-gi >
                   <div>
                    <FormKit 
                            type="text" 
                            label="Town" 
                            v-model="store.newWorker.address.town"
                            placeholder="Some Town"
                            help="The town that the Employee resides in."
                            />
                    <FormKit 
                            type="text" 
                            label="Parish or City" 
                            v-model="store.newWorker.address.city_parish"
                            placeholder="Kington"
                            help="The Parish that the Employee resides in."
                            />
                    
                   </div>

                </n-gi>
            </n-grid>
            <n-divider title-placement="left">
                Banking Information
            </n-divider>
            <n-grid x-gap="12" :cols="2">
                <n-gi >
                    <div>
                    
                        <FormKit 
                                type="text" 
                                label="Bank Name" 
                                v-model="store.newWorker.account.bank.name"
                                placeholder="NCB"
                                help="Employee bank Name."
                                />
                        <FormKit 
                                type="text" 
                                label="Branch" 
                                v-model="store.newWorker.account.bank.branch"
                                placeholder="MAYPEN"
                                help="Bank branch location."
                                />
                    </div>
                </n-gi>
                <n-gi >
                    <FormKit 
                            type="text" 
                            label="Account No." 
                            v-model="store.newWorker.account.bank.account"
                            placeholder="xxxxxxxxxx"
                            help="Employee Bank Account Number."
                            />
                    <FormKit 
                            type="select" 
                            label="Account Type" 
                            v-model="store.newWorker.account.bank.account_type"
                            :options="{savings: 'Savings', current: 'Current'}"
                            placeholder="Savings"
                            help="The type of Account."
                            />
                </n-gi>
            </n-grid>
            <n-divider title-placement="left">
                Next of Kin Information
            </n-divider>
            <n-grid x-gap="12" :cols="2">
                <n-gi >
                            
                    <FormKit 
                            type="text" 
                            label="Name" 
                            v-model="store.newWorker.nok.name"
                            placeholder="Jane Brown"
                            help="Ralative's full name."
                            />
                    <FormKit 
                            type="text" 
                            label="Relation" 
                            v-model="store.newWorker.nok.relation"
                            placeholder="Mother"
                            help="How is the employee related to this person."
                            />

                </n-gi>
                <n-gi >
                    <FormKit
                        type="text"
                        label="Phone"
                        v-model="store.newWorker.nok.contact.tel"
                        placeholder="xxx-xxx-xxxx"
                        :validation="[ ['matches', /^\d{3}-\d{3}-\d{4}$/]]"
                       
                        :validation-messages="{
                            matches: 'Phone number must be formatted: xxx-xxx-xxxx',
                        }"
                        help="Relative's Home or Work number."
                />
                <FormKit
                        type="text"
                        label="Mobile"
                        v-model="store.newWorker.nok.contact.mobile"
                        placeholder="xxx-xxx-xxxx"
                        :validation="[ ['matches', /^\d{3}-\d{3}-\d{4}$/]]"
                        
                        :validation-messages="{
                            matches: 'Mobile number must be formatted: xxx-xxx-xxxx',
                        }"
                        help="Relative's Mobile number."
                />
       
                </n-gi>
            </n-grid>    

</FormKit>
                                
                                <p class="uk-text-right">
                                    <button class="uk-button uk-button-default uk-modal-close" type="button">Cancel</button>
                                    <button class="uk-button uk-button-primary" type="button">Save</button>
                                </p>
                            </div>
                        </div>
            
            """
        except Exception as e:
            yield f"""<div class="uk-alert-warning" uk-alert>
                            <a href class="uk-alert-close" uk-close></a>
                            <p>{str(e)}</p>
                        </div>                       
                       
                        
                    """
            
        finally:
            del(e)







