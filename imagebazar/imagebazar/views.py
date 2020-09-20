from django.http import HttpResponse
from django.shortcuts import render, redirect
from myapp.models import Category, Image
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
import requests as requests
import urllib.request as url
from io import BytesIO
from io import StringIO
from PIL import Image as IM


def show_about_page(request):
    return render(request, "about.html")


def show_home_page(request):
    cats = Category.objects.all()
    images = Image.objects.all()
    context = {
        'images': images,
        'cats': cats
    }
    return render(request, "home.html", context)


def show_category(request, cid):
    cats = Category.objects.all()
    category = Category.objects.get(pk=cid)
    images = Image.objects.filter(cat=category)
    context = {
        'images': images,
        'cats': cats
    }
    return render(request, "home.html", context)


def search(request):
    query = request.GET['query']
    r = requests.get((
        "https://api.unsplash.com/search/photos?query={}&page=1&per_page=30&client_id=tGXMmv5bb-DHAXbm3rzLwtk84UtHgnJpXq8PqR_SpKQ").format(query))
    data = r.json()
    # print(data)
    # print(data.keys())
    # print(data['total'])
    # print(data['updated_at']) ['cover_photo']
    list_images = []
    for img in data['results']:
        img_url = img['urls']['regular']
        # response = requests.get(img_url)
        list_images.append(img_url)

    # print(img_url)
    if len(query) > 78:
        images = Image.objects.none()
    if query:
        # cats = Category.objects.all()
        category = Category.objects.filter(description__icontains=query)
        # print(cats)
        images = Image.objects.filter(cat=category.first())
        if category:
            return render(request, "search.html", {'images': images, 'list_images': list_images})
        elif not category and list_images:
            return render(request, "search.html", {'list_images': list_images})
        else:
            messages.error(request, "No match found for given query")
            return redirect("/")

    else:
        return redirect('/')


def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        lname = request.POST['lname']
        fname = request.POST['fname']
        email = request.POST['email']
        password1 = request.POST['Password1']
        password2 = request.POST['Password2']
        # Check for errornous inputs
        if len(username) > 10:
            messages.error(request, "username must be under 10 characters")
            return redirect('/')
        if not username.isalnum():
            messages.error(
                request, "username must contain letters or numbers")
            return redirect('/')
        if password1 != password2:
            messages.error(request, "Both passwords don't match")
            return redirect('/')
        # Create the user
        myuser = User.objects.create_user(username, email, password1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.save()
        messages.success(
            request, "Your imagemarket account has been created succesfully")
        return redirect('/')
    else:
        return HttpResponse("404 Not Found")


def userlogin(request):
    if request.method == 'POST':
        loginusername = request.POST['loginusername']
        loginpass = request.POST['loginpass']

        user = authenticate(username=loginusername, password=loginpass)

        if user is not None:
            login(request, user)
            messages.success(request, 'Logged-in successfully')
            return redirect('/')
        else:
            messages.error(request, "Invalid credentials, Please Try again")
            return redirect('/')
    else:
        return HttpResponse("404 Not Found")


def userlogout(request):
    logout(request)
    messages.success(request, "Logged-out Successfully ")
    return redirect('/')
