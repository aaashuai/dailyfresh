from django.shortcuts import render, redirect
from hashlib import sha1
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from .models import UserInfo
from . import user_decorater
from df_goods.models import GoodsInfo
from df_order.models import Order
from django.core.paginator import Paginator

# Create your views here.
def register(request):
    return render(request, 'df_user/register.html')
def register_handle(request):
    # 接收用户输入
    post = request.POST
    uname = post.get('user_name')
    upwd = post.get('pwd')
    upwd2 = post.get('cpwd')
    uemail = post.get('email')
    # 判断两个密码是否一致
    if upwd != upwd2:
        return redirect('/user/register')
    # 密码加密
    s1 = sha1()
    s1.update(upwd.encode('utf-8'))
    upwd3 = s1.hexdigest()
    # 创建对象
    user = UserInfo()
    user.uname = uname
    user.upwd = upwd3
    user.uemail = uemail
    user.save()#存到数据库

    #注册成功, 转到登录页面
    return redirect('/user/login/')

def checkuserid(request):
    username = request.POST.get("uname")
    usercount = UserInfo.objects.filter(uname = username).count()
    return JsonResponse({"count":usercount})

def login(request):
    uname = request.COOKIES.get('uname','')
    content = {"title": "用户登录", 'uname_error': 0, 'upwd_error': 0, 'uname':uname, 'namevalue': uname}
    return render(request, 'df_user/login.html', content)

def logout(request):
    request.session.flush()
    return redirect('/goods')

def login_handle(request):
    post = request.POST
    uname = post.get("username")
    upwd = post.get("pwd")
    ucheck = post.get("checkbox", 0)
    content = {"title": "用户登录", 'uname_error': 0, 'upwd_error': 0, 'ucheck': 0, 'namevalue': uname, 'pwdvalue': upwd}
    users = UserInfo.objects.filter(uname=uname)
    if len(users) == 1:
        # 密码加密验证
        s1 = sha1()
        s1.update(upwd.encode("utf-8"))
        if s1.hexdigest() == users[0].upwd:
            url = request.COOKIES.get('url','/goods')
            #密码验证成功， 转到info界面， 判断是否需要存cookie
            red = HttpResponseRedirect(url)
            if ucheck:
                red.set_cookie('uname',uname)
            else:
                red.set_cookie('uname','',max_age=-1)
            request.session['userid'] = users[0].id #　存id是以后查这个用户的时候可以根据这个id去查
            request.session['uname'] = uname #用到uname的地方很多, 每次都在uid中拿的话效率太低
            return red
        else:
            content['upwd_error'] = 1
            return render(request, 'df_user/login.html', content)
    else:
        content['uname_error'] = 1
        return render(request, 'df_user/login.html', content)

    return render(request, 'df_user/login.html', content)
@user_decorater.login
def info(request):
    lasted_view = request.COOKIES.get('goods_ids', '')
    views_list = []
    if lasted_view != '':
        good_list = lasted_view.split(',')
        # good_list = map(lambda x: int(x), good_list)
        for each in good_list:
            good_info = GoodsInfo.objects.get(id=int(each))
            views_list.append(good_info)

    uid = request.session.get('userid')
    uname = request.session.get('uname')
    user = UserInfo.objects.get(id=uid)
    content = {'title':'用户中心',
               'user_page':1,
               'uname':uname,
               'uphone':user.uphone,
               'uaddress':user.uaddress,
               'good_info':views_list}
    return render(request, 'df_user/user_center_info.html', content)

@user_decorater.login
def order(request, pageNum):
    user_id = request.session.get("userid")
    orders = Order.objects.filter(order_owner_id=user_id).order_by('-order_date').order_by('Ispay')
    paginator = Paginator(orders, 2)
    page = paginator.page(int(pageNum))

    content = {'title':'全部订单',
               'user_page':1,
               'orders':orders,
               'paginator':paginator,
               'page':page}
    return render(request, 'df_user/user_center_order.html', content)

@user_decorater.login
def site(request):
    user = UserInfo.objects.get(id=request.session.get('userid'))
    if request.method == 'POST':
        post = request.POST
        user.urecive = post.get('reciver', 'xxx')
        user.uaddress = post.get('detial_address', 'xxx省 xxx市 xxx街道')
        user.uphone = post.get('phone_num', 'xxx xxx xxxxx')
        user.upost = post.get('stamp_no')
        user.save()
        # phone_num = phone_num[0:3] + 'xxxx' + phone_num[7:11]
    content = {'title':'用户中心', 'user':user, 'user_page':1}
    return render(request, 'df_user/user_center_site.html', content)

# def site_addinfo(request):
#
#     # post = request.POST
#     # user = UserInfo.objects.get(id=request.session.get('userid'))
#     # user.urecive = post.get('ureciver', 'xxx')
#     # user.uaddress = post.get('uaddress', 'xxx省 xxx市 xxx街道')
#     # user.uphone = post.get('uphone', 'xxx xxx xxxxx')
#     # user.upost = post.get('ustamp')
#     # user.save()
#     content = {'title': '用户中心'}
#     return JsonResponse({"status":"success"})