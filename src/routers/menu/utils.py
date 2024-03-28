import io
import logging
import datetime
from operator import itemgetter
from src.constants.logger import CONSOLE_LOGGER_NAME
from fastapi import UploadFile
from fastapi.responses import StreamingResponse
from src.exceptions.error_response_exception import ErrorResponseException
from src.constants.error_code import get_error_code
from src.constants.image import ALLOWED_EXTENSION_IMAGE
from src.schemas.order import (
    CreateMenuSchema,
    CreateOrderSchema,
    AddNewItemSchema,
    AddNewItemByOrderIDSchema,
    CreateItemSchema,
    UpdateOrderStatusSchema,
    TotalBillSchema, BillDetailSchema,
    FoodDetailSchema, TotalFoodSchema
    
)
from src.schemas.food import (
    food_schema,
    AddNewItemSchemaV3,
    ItemV3
    
)
from src.models.order import Menu, Order, ItemOrder, UserOrder, Item
from src.models.users import User
from src.models.food import Food
from src.core.templates.fastapi_minio import minio_client
from uuid import uuid4
import cloudinary
import cloudinary.uploader
from bson import ObjectId

cloudinary.config(
    cloud_name="dsij6mntp",
    api_key="189381149557242",
    api_secret="f1Wq2eqAXeZqmI9ubM9cAc989mo",
)
logger = logging.getLogger(CONSOLE_LOGGER_NAME)


async def upload_img_v1(img: UploadFile) -> str:
    if img:
        print(f"img.file: {img.file}")
        file_extension = img.filename.split(".")[-1]
        if file_extension not in ALLOWED_EXTENSION_IMAGE:
            raise ErrorResponseException(**get_error_code(4000102))
        upload_result = cloudinary.uploader.upload(img.file, folder="scc-doi")
        print("pass step upload")
        if not upload_result:
            raise ErrorResponseException(**get_error_code(5000101))
        print(f"upload_result: {upload_result}")
    return upload_result


async def upload_img(img: UploadFile) -> str:
    file_name = ""
    if img:
        file_extension = img.filename.split(".")[-1]
        if file_extension not in ALLOWED_EXTENSION_IMAGE:
            raise ErrorResponseException(**get_error_code(4000102))
        file_name = str(uuid4()) + "." + file_extension
        upload_file = io.BytesIO(await img.read())
        upload_response = await minio_client.put_object(
            f"/menu/{file_name}", data=upload_file
        )
        if not upload_response:
            raise ErrorResponseException(**get_error_code(5000101))
    return file_name


async def create_new_menu(request_data: CreateMenuSchema, image: UploadFile):
    img_url = await upload_img(image)
    new_menu = Menu(
        title=request_data.title.lower(), link=request_data.link, image_name=img_url
    )
    try:
        exist_menu = await Menu.find_one({"title":request_data.title.lower()})
        if exist_menu:
            raise ValueError("menu already exist")
        await new_menu.insert()
    except Exception as e:
        logger.error(f"Error when create new menu: {e}")
        raise ErrorResponseException(**get_error_code(4000105))

    return new_menu.model_dump()


async def create_new_order(request_data: CreateOrderSchema, current_user: str):
    current_menu = await Menu.find_one({"title": request_data.menu})
    if not current_menu:
        raise ErrorResponseException(**get_error_code(4000107))

    # item_list_as_dict = [item.model_dump() for item in request_data.item_list]

    new_order = Order(
        created_by=current_user,
        status="active",
        title=request_data.title,
        description=request_data.description,
        namesAllowed=request_data.namesAllowed,
        menu=request_data.menu,
        area=request_data.area,
        share=True,
        order_date=request_data.order_date,
        created_at=datetime.datetime.now(),
        item_list=[],
        tags=request_data.tags,
    )

    try:
        await new_order.insert()
        #----------------------[save allowed user to order]------------
        current_allowed_name = request_data.namesAllowed
        for name in current_allowed_name:
            current = await UserOrder.find_one({"username" : name})
            if current is not None:
                cur_order_list = current.allow_order_id_list
                cur_order_list.append(str(new_order.id))
                await current.set({"allow_order_id_list" : cur_order_list})
                await current.save()

            else:
                new_allow_list: list[str] = []
                new_allow_list.append(str(new_order.id))
                
                new_allow_name = UserOrder(username=name, allow_order_id_list=new_allow_list)

                await new_allow_name.insert()


        #-------------------------------------------------------------

        #---------------------[save item to db]-------------------
        # current_item_list = request_data.item_list
        # if current_item_list:
        #     for item in current_item_list:
        #         newitem_db = ItemOrder(
        #             created_at=datetime.datetime.now(),
        #             created_by=current_user,
        #             order_id=str(new_order.id),
        #             food=item.food,
        #             order_for=item.order_for,
        #             price=item.price,
        #             quantity=item.quantity
        #         )
        
        #     await newitem_db.insert()
    #---------------------------------------------------------
    except Exception as e:
        logger.error(f"Error when create order: {e}")
        raise ErrorResponseException(**get_error_code(4000109))

    return new_order.model_dump()


async def get_order():
    result = Order.find_all()

    return_data = []
    async for data in result:
        return_data.append(data.model_dump())
    return return_data


async def get_menu():
    result = Menu.find_all()

    return_data = []
    async for data in result:
        return_data.append(data.model_dump())
    return return_data


async def get_image_of_menu(request_data: str):
    if not request_data:
        file_object = io.open("src/data/default_logo.png", "rb", 0)
        file_extension = "png"
        return StreamingResponse(
            file_object,
            headers={
                "Content-Disposition": "inline",
                "Content-type": f"image/{file_extension}",
                "Cache-Control": "max-age=290304000, public",
            },
        )
    file_extension = request_data.split(".")[-1]
    if file_extension not in ALLOWED_EXTENSION_IMAGE:
        raise ErrorResponseException(**get_error_code(4000102))
    minio_url = await minio_client.get_url(f"/menu/{request_data}")
    if not minio_url:
        raise ErrorResponseException(**get_error_code(5000102))
    return minio_url


async def add_new_item_to_order(request_data: AddNewItemSchema):
    current_order = await Order.find_one(
        {
            "title": request_data.order.title,
            "description": request_data.order.description,
            "namesAllowed": request_data.order.namesAllowed,
            "menu": request_data.order.menu,
            "area": request_data.order.area,
            "share": request_data.order.share,
            "tags": request_data.order.tags,
        }
    )

    if not current_order:
        raise ErrorResponseException(**get_error_code(4000111))

    current_item_list = current_order.item_list

    for item in request_data.new_item:
        current_item_list.append(item.model_dump())

    await current_order.update({"$set": {"item_list": current_item_list}})
    await current_order.save()


    return current_order.model_dump()


async def add_new_item_to_order_by_id(request_data: AddNewItemByOrderIDSchema, current_user : str):
    current_order = await Order.find_one(
        {
            "_id" : ObjectId(request_data.order_id)
        }

    )

    if not current_order:
        raise ErrorResponseException(**get_error_code(4000111))
    
    if current_order.status=="expired" or current_order.status=="closed":
        raise ErrorResponseException("cannot add item for closed Order topic")
    

    
    current_item_list = current_order.item_list
    if len(request_data.new_item)!=0:
        for item in request_data.new_item:

            check_exist = await ItemOrder.find_one({"order_id" : request_data.order_id,
                                                    "order_for": item.order_for,
                                                    "food" : item.food,
                                                    "note" : item.note
                                                    })

            if check_exist:
                pos = [data.item_detail_id for data in current_item_list].index(str(check_exist.id))
                current_item_list[pos].quantity = current_item_list[pos].quantity + item.quantity
                await check_exist.set({"quantity" : check_exist.quantity + item.quantity})
                continue             


            newitem_db = ItemOrder(
                created_at=datetime.datetime.now(),
                created_by=current_user,
                food_id=item.food_id,
                order_id=request_data.order_id,
                food=item.food,
                order_for=item.order_for,
                price=item.price,
                quantity=item.quantity,
                note=item.note
                )
        
        
            await newitem_db.insert()
            item.item_detail_id = str(newitem_db.id)
            current_item_list.append(item.model_dump())

    # current_order.update({"$set": {"item_list": current_item_list}})
    await current_order.set({"item_list": current_item_list})
    await current_order.save()
    #---

    return current_order.model_dump()


#--------------[update filter]--------------------

async def get_order_v2(current_user : str, current_area : int):
    return_data = []
    con1 = Order.find({"namesAllowed" : [], "area" : current_area, "created_by" : {"$ne": current_user}, "share": True})
    #, "created_by" : {"$ne": current_user}
    con2 = Order.find({"created_by" : current_user})
    # { field1: { $elemMatch: { one: 1 } } }

    if con1 is not None:
        async for data in con1:
            return_data.append(data.model_dump())

    if con2 is not None:
        async for data in con2:
            return_data.append(data.model_dump())

    order_list = await UserOrder.find_one({"username" : current_user})
    if order_list:
        alist = order_list.allow_order_id_list
        for order_id in alist:
            con3 = await Order.find_one({"_id" : ObjectId(order_id), "share" : True})
            if con3:
                return_data.append(con3.model_dump())
                
    sorted_result = sorted(return_data, key=itemgetter('created_at'), reverse=True)
                
    return sorted_result

    # if order_list:
    #     list_order_id = order_list.allow_order_id_list
    #     # list_con3 = Order.aggregate([])
    #     # print([ObjectId(order_id) for order_id in list_order_id])
    #     list_con3 = Order.aggregate([
    #         {
    #             '$match': {
    #                 "id" : {"$in" : [ObjectId(order_id) for order_id in list_order_id]}
    #                 },
    #         }
    #     ])
    #     async for con3 in list_con3:
    #         print(con3)
    #     return []
    
#-------------------------------------------------



#----------[add new food]--------------------
async def add_new_food(request_data : food_schema, img : UploadFile):
    img_url = await upload_img(img)
    new_food = Food(
        food_name= request_data.food_name,
        price=request_data.price,
        ingredients= request_data.ingredients,
        menu_title=request_data.menu_title,
        image_url=img_url
    )
    try:
        exist_menu = await Menu.find_one({"title" : request_data.menu_title})
        if not exist_menu:
            raise ValueError("Menu not exist !")
        exist_food = await Food.find_one({"food_name" : request_data.food_name,
                                          "menu_title" : request_data.menu_title})
        if exist_food:
            raise ValueError("food already exist !")
        await new_food.insert()

    except Exception as e:
        logger.error(f"Error when add a new food {e}:")
        raise ErrorResponseException(**get_error_code(4000105))

    
    return new_food.model_dump()
#--------------------------------------------


#----------[Get All Food]--------------------
async def get_all_food():
    result = Food.find_all()
    return_data = []
    async for data in result:
        return_data.append(data.model_dump())

    return return_data
#--------------------------------------------


#----------[Get Food By Order ID]-----------------------------

# async def get_food_by_menu_from_order(order_id : str):
#     try:
#         return_data = []
#         current_order = await Order.find_one({"_id" : ObjectId(order_id)})
#         print(current_order)
#         if current_order:
#             current_menu = await Menu.find_one({"title" : current_order.menu})
#             print(current_menu)
#             if current_menu:
#                 result = Food.find({"menu_id" : str(current_menu.id)})
#                 async for data in result:
#                     print(data)
#                     return_data.append(data.model_dump())




#     except Exception as e:
#         logger.error(f"fail at get food by menu from order {e} :")
#         raise ErrorResponseException(**get_error_code(4000105))
#     return return_data

#---------------------------------------------------------


#------------------------[get order by - order's owner & order's participants]--------------------------\
async def get_my_order(current_user : str):
    result= []
    order_list = Order.find({"created_by" : current_user})
    async for data in order_list:
        result.append(data.model_dump())

    order_list2 = Order.find({"created_by" : {"$ne": current_user}})
    async for data in order_list2:
        dup_list = []
        item_list : Item = []
        item_list = data.item_list
        for item_data in item_list:
            if item_data.created_by == current_user:
                result.append(data.model_dump())
                break

    sorted_result = sorted(result, key=itemgetter('created_at'), reverse=True)


    return sorted_result

#------------------------[get order by - order's owner & order's participants]--------------------------\
async def get_my_order_expired(current_user : str):
    result= []
    order_list = Order.find({"created_by" : current_user, "status" : "expired"})
    async for data in order_list:
        result.append(data.model_dump())

    order_list2 = Order.find({"created_by" : {"$ne": current_user}, "status" : "expired"})
    async for data in order_list2:
        dup_list = []
        item_list : Item = []
        item_list = data.item_list
        for item_data in item_list:
            if item_data.created_by == current_user:
                result.append(data.model_dump())
                break

    sorted_result = sorted(result, key=itemgetter('created_at'), reverse=True)


    return sorted_result


async def get_order_created(current_user : str):
    result= []
    order_list = Order.find({"created_by" : current_user})
    async for data in order_list:
        result.append(data.model_dump())
    sorted_result = sorted(result, key=itemgetter('created_at'), reverse=True)


    return sorted_result


async def get_order_joined(current_user : str):
    result = []
    order_list2 = Order.find({"created_by" : {"$ne": current_user}})
    async for data in order_list2:
        dup_list = []
        item_list : Item = []
        item_list = data.item_list
        for item_data in item_list:
            if item_data.created_by == current_user:
                result.append(data.model_dump())
                break
    sorted_result = sorted(result, key=itemgetter('created_at'), reverse=True)


    return sorted_result


#-------------------------------------------------------------------------------------------------------/

#---------------[get food by menu title]---------------------
async def get_food_by_menu_title(request_title: str):
    return_data = []
    result = Food.find({"menu_title" : request_title})
    if result:
        async for data in result:
            return_data.append(data.model_dump())
    return return_data


#------------------------------------------------------------


#--------[add new Item v3 (with food update)]----------------   

async def add_new_item_v3(current_user : str, request_data : AddNewItemSchemaV3):
    item_list = []
    food_list = request_data.new_items
    for data in food_list:
        current_item : ItemV3 = data
        item_info = await Food.find_one({"_id" : ObjectId(current_item.food_id)})
        new_item_list = CreateItemSchema(order_for=current_item.order_for,
                                        item_detail_id="",
                                        food_id=current_item.food_id,
                                        created_by=current_user,
                                        food=item_info.food_name,
                                        price=item_info.price,
                                        quantity=current_item.quantity,
                                        note=current_item.note)
        item_list.append(new_item_list)

    request_data_2_template = AddNewItemByOrderIDSchema(
        order_id=request_data.order_id,
        new_item=item_list
    )

    result = await add_new_item_to_order_by_id(request_data_2_template, current_user)
    return result
    
#-------------------------------------------------------------


#-------------------[Delete Item By Id]-------------------
async def do_delete_item_by_id(item_id : str, current_user : str):
    current_item = await ItemOrder.find_one(ItemOrder.id == ObjectId(item_id))
    if not current_item:
        raise Exception("Item not Found !")
    
    if current_item.created_by != current_user:
        raise Exception("not Item's orderer !")
    
    item_in_order = await Order.find_one(Order.id == ObjectId(current_item.order_id))
    if item_in_order.status != "active":
        raise Exception("Order's topic closed")
    order_item_list = item_in_order.item_list

    pos = [data.item_detail_id for data in order_item_list].index(item_id)
    order_item_list.pop(pos)

  

    item_in_order.item_list = order_item_list
    await item_in_order.save()

    await current_item.delete()

#---------------------------------------------------------
    
#----------------------[Do delete order v2]-----------------------\
async def do_delete_order_by_id_v2(order_id : str, current_user : str):
    current_order = await Order.find_one(Order.id == ObjectId(order_id))
    if not current_order:
        raise Exception("order not found")
    if current_order.created_by != current_user:
        raise Exception("nor order topic's author")
    order_item_list = current_order.item_list
    for data in order_item_list:
        delete_item = await ItemOrder.find_one(ItemOrder.id == ObjectId(data.item_detail_id))
        if delete_item:
            await delete_item.delete()
    await current_order.delete()
#-----------------------------------------------------------------/


#-------------[Do get order by id]----------------------------

async def do_get_order_by_id(order_id : str):
    result = await Order.find_one({"_id" : ObjectId(order_id)})
    return result.model_dump()

#-------------------------------------------------------------


#-------------[Do get food by order id]----------------------------

async def do_get_food_by_order_id(order_id : str):
    result = []
    current_order = await Order.find_one({"_id" : ObjectId(order_id)})
    foods = Food.find({"menu_title" : current_order.menu})
    async for data in foods:
        result.append(data.model_dump())

    return result


#-------------------------------------------------------------

#------------[Get user Image By Order_id]-------------------
async def get_user_image_by_order_id(order_id : str):
    try:
        current_order  = await Order.find_one({"_id" : ObjectId(order_id)})
        if not current_order:
            raise Exception("order not found !")
        result_user =  await User.find_one({"username" : current_order.created_by})

        if not current_order:
            raise Exception("User not found !")
        
        result_img = ""
        
        if result_user.img_url != "":

            result_img = await get_image_of_menu(result_user.img_url)
        return result_img
    except Exception as e:
        logger.error(e)
        raise Exception(e)
        
#----------------------------------------------------------

#--------------------------------[CHANGE ORDER STATUS]---------------------------
async def update_order_status(request_data : UpdateOrderStatusSchema, current_user : str):
    current_order = await Order.find_one({"_id" : ObjectId(request_data.order_id)})

    if current_user != current_order.created_by:
        raise Exception("Not Order's author")

    if not current_order:
        raise Exception("Order not found !")

    status_list = ["active", "closed", "expired"]
    
    match current_order.status:
        case "active":
            await current_order.set({"status" : "closed"})
            await current_order.save()
        case "closed":
            await current_order.set({"status" : "active"})
            await current_order.save()
        case "expired":
            await current_order.set({"order_date" : datetime.datetime.now()+datetime.timedelta(minutes=30)})
            await current_order.set({"status" : "active"})
            await current_order.save()
        case _:
            raise Exception("status code invalid !")


    # if (request_data.status != "active" and request_data.status != "closed" and request_data.status != "expired"):
    # if request_data.status not in status_list:
    #     raise Exception("status code invalid !")
    
    # if (request_data.status == "active" and current_order.status == "expired"):
    #     await current_order.set({"order_date" : datetime.datetime.now()+datetime.timedelta(minutes=30)})
    
    return current_order.status
#----------------------------------------------------------------------------

#-------------------------------[set expired Order]-----------------------------------------------
async def set_expired_order():
    expired_order = Order.find({"status" : "active" ,"order_date": {"$lt": datetime.datetime.now()}})
    await expired_order.update_many({}, {"$set" : {"status" : "expired"}})
#--------------------------------------------------------------------------------------------------


#-------------------------[get total bill by order id]-----------------------------\
async def do_get_total_bill_order_by_order_id(order_id : str):
    current_order = await Order.find_one(Order.id == ObjectId(order_id))
    if not current_order:
        raise Exception("current order not found !")
    
    result = TotalBillSchema(info=[], total_price=0)
    for item in current_order.item_list:
        current_item = BillDetailSchema(username=item.created_by,
                                        foodname=item.food,
                                        quantity=item.quantity,
                                        final_price=item.price * item.quantity
                                        )
        result.info.append(current_item)
        result.total_price = result.total_price + current_item.final_price

    return result

#----------------------------------------------------------------------------------/

#-------------------------[get total Food bill by order id]-----------------------------\
async def do_get_food_bill_order_by_order_id(order_id : str):
    all_item = ItemOrder.find(ItemOrder.order_id==order_id)
    if not all_item:
        raise Exception("current order not found !")
    
    result = TotalFoodSchema(info=[], total_price=0)
    dupfood= []
    async for data in all_item:
        if data.food not in dupfood:
            result.info.append(FoodDetailSchema(
                food_name=data.food,
                price=data.price,
                quantity=data.quantity,
                note=[data.note],
                final_price=data.price*data.quantity
            ))
            result.total_price = result.total_price + (data.price*data.quantity)
            dupfood.append(data.food)
        else:
            pos = [x.food_name for x in result.info].index(data.food)
            result.info[pos].quantity = result.info[pos].quantity + data.quantity
            if data.note != "":
                result.info[pos].note.append(data.note)
            result.info[pos].final_price = result.info[pos].final_price + result.info[pos].price * data.quantity
            result.total_price = result.total_price + (result.info[pos].price * data.quantity)

    return result
#---------------------------------------------------------------------------------------/



#-------------------------[get total bill by order id]-----------------------------\
async def do_get_personal_bill_order_by_order_id_and_username(order_id : str, username : str):
    current_order = await Order.find_one(Order.id == ObjectId(order_id), Order.created_by == username)

    if not current_order:
        raise Exception("current order not found !")
    
    result = TotalBillSchema(info=[], total_price=0)
    for item in current_order.item_list:
        current_item = BillDetailSchema(username=item.created_by,
                                        foodname=item.food,
                                        quantity=item.quantity,
                                        final_price=item.price * item.quantity
                                        )
        result.info.append(current_item)
        result.total_price = result.total_price + current_item.final_price

    return result

#----------------------------------------------------------------------------------/
