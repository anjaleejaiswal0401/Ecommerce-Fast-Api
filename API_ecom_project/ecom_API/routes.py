from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi_login import LoginManager
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter, Request, Form, status, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from pathlib import Path
from fastapi import FastAPI
from fastapi import APIRouter
from ecom_API.pydantic_models import *
from . models import *
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from fastapi_login.exceptions import InvalidCredentialsException
from starlette.middleware.sessions import SessionMiddleware
import typing
import re

router = APIRouter()


def flash(request: Request, message: typing.Any, category: str = "") -> None:
    if "_messages" not in request.session:
        request.session["_messages"] = []
    request.session["_messages"].append(
        {"message": message, "category": category})


def get_flashed_messages(request: Request):
    print(request.session)
    return request.session.pop("_messages") if "_messages" in request.session else []


BASE_DIR = Path(__file__).resolve().parent

templates = Jinja2Templates(directory="ecom_API/templates")
templates.env.globals['get_flashed_messages'] = get_flashed_messages
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET = 'your-secret-key'
manager = LoginManager(SECRET, token_url='/auth/token')


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


@router.get("/registration/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("registration.html", {"request": request, })


@router.post('/registration/',)
async def create_user(request: Request, email: EmailStr = Form(...),
                      name: str = Form(...),
                      phone: str = Form(...),
                      password: str = Form(...)):
    reg_pass = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$"
    pat_pass = re.compile(reg_pass)
    mat_pass = re.search(pat_pass, password)

    reg_name = re.compile('^[A-Za-z]+$')
    mat_name = re.search(reg_name, name)

    if await Create_user.filter(email=email).exists():
        flash(request, "Email already exists", "danger")
        return RedirectResponse("/registration/", status_code=status.HTTP_302_FOUND)
    elif await Create_user.filter(phone=phone).exists():
        flash(request, "Phone number already exists", "danger")
        return RedirectResponse("/registration/", status_code=status.HTTP_302_FOUND)
    else:
        if not mat_name:
            flash(request, "Your name can be in latters only ", "danger")
            return RedirectResponse("/registration/", status_code=status.HTTP_302_FOUND)
        elif len(phone) != 10:
            flash(request, "Please enter 10 digit number", "danger")
            return RedirectResponse("/registration/", status_code=status.HTTP_302_FOUND)
        elif not mat_pass:
            flash(request, "Your password lenth must be in 6 to 20 and must contain atleast one uppercase, one lower case, one special character, one number ", "danger")
            return RedirectResponse("/registration/", status_code=status.HTTP_302_FOUND)
        else:
            user_obj = await Create_user.create(email=email, name=name,
                                                phone=phone, password=get_password_hash(password))
            print(user_obj)
            return RedirectResponse("/login/", status_code=status.HTTP_302_FOUND)


@router.get("/login/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, })


@manager.user_loader()
async def load_user(email: str):
    if await Create_user.exists(email=email):
        newapi1 = await Create_user.get(email=email)
        return newapi1


@router.post('/login/', )
async def login(request: Request, email: str = Form(...),
                password: str = Form(...)):

    email = email
    user = await load_user(email)

    if not Create_user:
        flash(request, "User not exsist", "danger")
        return RedirectResponse("/login/", status_code=status.HTTP_302_FOUND)
    elif not verify_password(password, user.password):
        flash(request, "Failed to login", "danger")
        return RedirectResponse("/login/", status_code=status.HTTP_302_FOUND)
    else:
        request.session["user_id"] = user.id
        request.session["user_name"] = user.name
        request.session["user_phone"] = user.phone
        request.session["user_email"] = user.email

        print(request.session["user_id"])

        print(request.session["user_name"])
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)


@router.get('/logout/', )
async def logout(request: Request,):
    request.session.clear()
    return RedirectResponse("/login/", status_code=status.HTTP_302_FOUND)


@router.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    addp = await Add_products.all()
    return templates.TemplateResponse("index.html", {"request": request, 'addp': addp})


@router.get("/category/", response_class=HTMLResponse)
async def read_item(request: Request):
    ct = await Category.all()
    sct = await SubCategory.all()
    addp = await Add_products.all()
    return templates.TemplateResponse("category.html", {"request": request, 'ct': ct, 'sct': sct, 'addp': addp})


@router.get("/product/{slug:str}/", response_class=HTMLResponse)
async def read_item(request: Request, slug: str):
    addp = await Add_products.get(slug=slug).select_related("category")
    product = await Add_products.filter(slug=slug)
    return templates.TemplateResponse("single-product.html", {"request": request, "addp": addp, "product": product})


@router.get("/cart/", response_class=HTMLResponse)
async def read_item(request: Request):
    add_to_cart = await Addtocart.all().select_related("product_d", "user")
    return templates.TemplateResponse("cart.html", {"request": request, "add_to_cart": add_to_cart})


# @router.get("/cart/", response_class=HTMLResponse)
# async def read_item(request: Request):
#     add_to_cart = await ADDincart.all()
#     return templates.TemplateResponse("cart.html", {"request": request, "add_to_cart": add_to_cart})


@router.post('/addtocart/',)
async def create_cart(request: Request, product_d_id: int = Form(...),):

    user_id = request.session["user_id"]
    if await Addtocart.filter(product_d_id=product_d_id).exists():
        return RedirectResponse("/cart/", status_code=status.HTTP_302_FOUND)
    else:
        cart_obj = await Addtocart.create(user_id=user_id, product_d_id=product_d_id)
    return RedirectResponse("/cart/", status_code=status.HTTP_302_FOUND)


@router.post('/order/',)
async def create_order(request: Request, shipping: float = Form(...),
                       subtotal: float = Form(...),
                       total: float = Form(...),
                       ):

    orderuser_id = request.session["user_id"]
    sd = await Order.get(orderuser_id=orderuser_id).delete()
    if await Order.create(orderuser_id=orderuser_id, shipping=shipping,
                          subtotal=subtotal, total=total):
        return RedirectResponse("/checkout/", status_code=status.HTTP_302_FOUND)


@router.post('/billing/',)
async def create_bill(request: Request, billingorder_id: int = Form(...),
                      name: str = Form(...), address: str = Form(...), email: EmailStr = Form(...),
                      city: str = Form(...), pincode: str = Form(...),
                      phone: str = Form(...), state: str = Form(...),
                      ):
    orderuser_id = request.session["user_id"]
    add = await Addtocart.all().select_related("product_d", "user")
    if await Billing.create(name=name, phone=phone, billingorder_id=billingorder_id,
                            email=email, address=address, city=city, orderuser_id=orderuser_id, pincode=pincode, state=state):
        return RedirectResponse("/confirmation/", status_code=status.HTTP_302_FOUND)


@router.get("/checkout/", response_class=HTMLResponse)
async def read_item(request: Request):
    totals = await Order.all()
    users = await Create_user.all()
    return templates.TemplateResponse("checkout.html", {"request": request, "totals": totals, "users": users})


@router.post('/confirm/',)
async def create_bill(request: Request,
                      name: str = Form(...), address: str = Form(...), email: EmailStr = Form(...),
                      city: str = Form(...), pincode: str = Form(...), state: str = Form(...),
                      phone: str = Form(...), subtotal: float = Form(...), total: float = Form(...),
                      shipping: float = Form(...), ordernumber: str = Form(...),):
    orderuser_id = request.session["user_id"]
    add = await Addtocart.all().select_related("user")

    deletecart = await Addtocart.get(user_id=orderuser_id).delete()
    deleteorder = await Order.get(orderuser_id=orderuser_id).delete()
    if await Orderhistory.create(name=name, phone=phone, ordernumber=ordernumber,
                                 email=email, address=address, city=city, orderuser_id=orderuser_id, pincode=pincode, state=state, subtotal=subtotal, total=total, shipping=shipping):

        return RedirectResponse("/tracking/", status_code=status.HTTP_302_FOUND)


@router.get("/delete_cartitem/{id}")
async def delete_cartproducts(request: Request, id: int):
    delete_products = await Addtocart.get(id=id).delete()
    # await delete_products.delete()
    return RedirectResponse("/cart/", status_code=status.HTTP_302_FOUND)


@router.get("/confirmation/", response_class=HTMLResponse)
async def read_item(request: Request):
    totals = await Order.all()
    billing = await Billing.all()
    return templates.TemplateResponse("confirmation.html", {"request": request, "totals": totals, "billing": billing})


@router.get("/tracking/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("tracking.html", {"request": request, })


@router.get("/profiledetail/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("profile.html", {"request": request, })


@router.post('/anjalee/',)
async def create_child(request: Request,
                       name: str = Form(...), value: int = Form(...), parent_id: int = Form(...),):
    child = await Child.create(name=name, value=value, parent_id=parent_id)
    return child