from django.shortcuts import render
from django.http import HttpResponse
import math
from django.views.decorators.csrf import csrf_protect

# Create your views here.
def home_view(request,*args, **kwargs):
    return HttpResponse(show_view(request))

class Goods():
    def __init__(self,width=1,height=1,lenght=1,number=1,stackable=False,is_pallet=False) -> None:
        self.x = width
        self.y = height
        self.z = lenght
        self.number = number
        self.stackable = stackable
        self.is_pallet= is_pallet

    @property
    def x(self):
        return self._x
    
    @x.setter
    def x(self,value):
        if value <= 0 or '':
            raise ValueError("Méret nem lehet 0 vagy annál kisebb")
        self._x=value
        
    @property
    def y(self):
        return self._y
    
    @y.setter
    def y(self,value):
        if value <= 0 or '':
            raise ValueError("Méret nem lehet 0 vagy annál kisebb")
        self._y=value
        
    @property
    def z(self):
        return self._z
    
    @z.setter
    def z(self,value):
        if value <= 0 or '':
            raise ValueError("Méret nem lehet 0 vagy annál kisebb")
        self._z=value
        
    @property
    def number(self):
        return self._number
    
    @number.setter
    def number(self,value):
        if value <= 0 or '':
            raise ValueError("Mennyiség nem lehet 0 vagy annál kisebb")
        self._number=value

class Storage_loader():
    def __init__(self,x,y,z,goods_object) -> None:
        self.goods=goods_object
        self._storage_x = x
        self._storage_y = y
        self._storage_z = z
        self.goods_list = [self.goods.x,self.goods.y,self.goods.z]

    @property
    def storage_x(self):
        return self._storage_x
    
    @storage_x.setter
    def storage_x(self,value):
        if value <= 0 or '':
            raise ValueError("Méret nem lehet 0 vagy annál kisebb")
        self._storage_x=value
        
    @property
    def storage_y(self):
        return self._storage_y
    
    @storage_y.setter
    def storage_y(self,value):
        if value <= 0 or '':
            raise ValueError("Méret nem lehet 0 vagy annál kisebb")
        self._storage_y=value
        
    @property
    def storage_z(self):
        return self._storage_z
    
    @storage_z.setter
    def storage_z(self,value):
        if value <= 0 or '':
            raise ValueError("Méret nem lehet 0 vagy annál kisebb")
        self._storage_z=value

    def validate_dimension(self):
        for i in self.goods_list:
            if i > self.storage_x or i > self.storage_y or i > self.storage_z:
                return False
        return True       

    def __calculate_non_stackable(self):
        goods_fit_in_x_space = [self.storage_x//self.goods.x,self.storage_x//self.goods.y,self.storage_x//self.goods.z]
        raw_results=[]
        for i in range(len(self.goods_list)):
            remove_dim=self.goods_list[i]
            self.goods_list.pop(i)
            for j in range(len(self.goods_list)):
                if j%2==0:
                    raw_results.append([remove_dim,goods_fit_in_x_space[i],self.goods_list[j+1]])
                else:
                    raw_results.append([remove_dim,goods_fit_in_x_space[i],self.goods_list[j-1]])
            self.goods_list.insert(i,remove_dim)
        result=[]
        for item in raw_results:
            result.append(math.ceil(self.goods.number/item[1])*item[2])
        return min(result)
         
    def __calculate_pallet_non_stackable(self):
        self.goods_list.pop(1)
        goods_fit_in_x_space = [self.storage_x//self.goods.x,self.storage_x//self.goods.z]
        raw_results=[]
        for i in range(len(self.goods_list)):
            if i%2==0:
                raw_results.append([self.goods_list[i],goods_fit_in_x_space[i],self.goods_list[i+1]])
            else:    
                raw_results.append([self.goods_list[i],goods_fit_in_x_space[i],self.goods_list[i-1]])
        result=[]
        for item in raw_results:
            result.append(math.ceil(self.goods.number/item[1])*item[2])
        return min(result)
    
    def __calculate_pallet_stackable(self):
        item_height=self.goods_list[1]
        self.goods_list.pop(1)

        goods_fit_in_height_space = []
        for index in range(len(self.goods_list)):
            number_of_fit_in_width = self.storage_x//self.goods_list[index]
            removed_dim=self.goods_list[index]
            self.goods_list.remove(removed_dim)
            goods_fit_in_height_space.append([removed_dim,number_of_fit_in_width,item_height,self.storage_z//item_height,self.goods_list[0]])
            self.goods_list.insert(index,removed_dim)

        raw_results=[]
        result=[]
        for item in goods_fit_in_height_space:
            raw_results.append([item[1]*item[3],item[4]])
            result.append(math.ceil(self.goods.number/(item[1]*item[3]))*item[4])
        
        return min(result)

    def __calculate_stackable(self):
        goods_fit_in_height_space = []
        for index in range(len(self.goods_list)):
            number_of_fit_in_width = self.storage_x//self.goods_list[index]
            removed_dim=self.goods_list[index]
            self.goods_list.remove(removed_dim)
            for i in range(2):
                if i%2==0:
                    goods_fit_in_height_space.append([removed_dim,number_of_fit_in_width,self.goods_list[i],self.storage_z//self.goods_list[i],self.goods_list[i+1]])
                else:
                    goods_fit_in_height_space.append([removed_dim,number_of_fit_in_width,self.goods_list[i],self.storage_z//self.goods_list[i],self.goods_list[i-1]])
            self.goods_list.insert(index,removed_dim)

        raw_results=[]
        result=[]
        for item in goods_fit_in_height_space:
            raw_results.append([item[1]*item[3],item[4]])
            result.append(math.ceil(self.goods.number/(item[1]*item[3]))*item[4])
        
        return min(result)
    
    def calculate(self):
        if self.goods.stackable and self.goods.is_pallet:  # 1 1
            return self.__calculate_pallet_stackable()
        elif self.goods.stackable and not self.goods.is_pallet: # 1 0
            return self.__calculate_stackable()
        elif not self.goods.stackable and self.goods.is_pallet: # 0 1
            return self.__calculate_pallet_non_stackable()
        else:
            return self.__calculate_non_stackable()
        
def convert_to_m(value,unit):
    if unit == 'cm':
        value/=100
    return value

def show_view(request):
    result = None
    load_percent = None
    if request.method == 'POST':
        is_pallet= False
        is_stackable = False
        if request.POST.get('pallet') == 'on':
            is_pallet= True
        if request.POST.get('stackable') == 'on':
            is_stackable = True
        try:
            goods=Goods()
            goods.x = convert_to_m(float(request.POST.get('item_width')),request.POST.get('unit_item_width'))
            goods.y = convert_to_m(float(request.POST.get('item_height')),request.POST.get('unit_item_height'))
            goods.z = convert_to_m(float(request.POST.get('item_length')),request.POST.get('unit_item_length')) 
            goods.number = int(request.POST.get('item_number'))
            goods.is_pallet = is_pallet
            goods.stackable = is_stackable
            truck = Storage_loader(convert_to_m(float(request.POST.get('storage_x')),request.POST.get('unit_storage_x'))
                                   ,convert_to_m(float(request.POST.get('storage_z')),request.POST.get('unit_storage_z'))
                                   ,convert_to_m(float(request.POST.get('storage_y')),request.POST.get('unit_storage_y'))
                                   ,goods)
            if truck.validate_dimension():
                result = round(truck.calculate(),1)
                if result > truck.storage_y:
                    result='Nem fog felférni'
                load_percent=round(((goods.x*goods.y*goods.z*goods.number)/(truck.storage_x*truck.storage_y*truck.storage_z))*100,1)
            else:
                result = 'Az áru méret nem megfelelő'
        except ValueError as e:
            return render(request,'index.html')
        return render(request,'index.html',{'result' : result,'load_percent' : load_percent, 'item_width' : goods.x, 'item_height' : goods.y, 'item_length': goods.z,
            'item_number': goods.number, 'pallet': goods.is_pallet, 'stackable' : goods.stackable,
            'storage_x' : truck.storage_x, 'storage_z' : truck.storage_y, 'storage_y' : truck.storage_z})
    else:
        return render(request,'index.html')
