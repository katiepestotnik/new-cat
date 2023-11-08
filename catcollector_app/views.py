from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils import timezone
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
# for create view
from django.contrib.auth import login
# create user form
from django.contrib.auth.forms import UserCreationForm
#authorization for view functions
from django.contrib.auth.decorators import login_required

# for author mixin for cbv
from django.contrib.auth.mixins import LoginRequiredMixin

#imports to use AWS
import uuid
import boto3
#use s3 info from .env
import os

from .models import Cat, Toy, Photo
from .forms import FeedingForm
# cats = [
#   {'name': 'Lolo', 'breed': 'tabby', 'description': 'furry little demon', 'age': 3},
#   {'name': 'Sachi', 'breed': 'calico', 'description': 'gentle and loving', 'age': 2},
# ]
# Create your views here.
def home(request):
    return render(request, 'cats/home.html')

def about(request):
    context = {
        'current_year': timezone.now().year
    }
    return render(request, 'cats/about.html', context)

# functional views
@login_required
def cats_index(request):
    #all cats
    #cats = Cat.objects.all()
    cats = Cat.objects.filter(user=request.user)
    return render(request, 'cats/index.html',{
        'cats': cats
    })
@login_required
def cats_detail(request, cat_id):
    cat = Cat.objects.get(id=cat_id)
    feeding_form = FeedingForm()
    toys = Toy
    id_list = cat.toys.all().values_list('id')
    print(id_list)
    toys_cat_doesnt_have = Toy.objects.exclude(id__in=id_list)
    return render(request, 'cats/detail.html', {
        'cat':cat,
        'feeding_form': feeding_form,
        'toys': toys_cat_doesnt_have
        })

#CBVs

class CatCreate(LoginRequiredMixin, CreateView):
  model = Cat
  fields = ['name', 'breed', 'description', 'age']
  
  # This inherited method is called when a
  # valid cat form is being submitted
  def form_valid(self, form):
    # Assign the logged in user (self.request.user)
    form.instance.user = self.request.user  # form.instance is the cat
    # Let the CreateView do its job as usual
    return super().form_valid(form)

class CatUpdate(LoginRequiredMixin, UpdateView):
    model = Cat
    fields = ['breed', 'description', 'age']

class CatDelete(LoginRequiredMixin, DeleteView):
    model = Cat
    success_url = '/cats'

class ToyList(LoginRequiredMixin, ListView):
    #toy_list is default context
    model = Toy

class ToyDetail(LoginRequiredMixin, DetailView):
    model = Toy

class ToyCreate(LoginRequiredMixin, CreateView):
    model = Toy
    fields = '__all__'

class ToyUpdate(LoginRequiredMixin, UpdateView):
    model = Toy
    fields = ['name', 'color']

class ToyDelete(LoginRequiredMixin, DeleteView):
    model = Toy
    success_url = '/toys'

#add feeding with view function
@login_required
def add_feeding(request, pk):
    #create ModelForm with data in request.Post
    form = FeedingForm(request.POST)
    #validate
    if form.is_valid():
        #make sure cat_id is assigned before goes to db
        #creates a spot in memory to allow us to save id
        new_feeding = form.save(commit=False)
        new_feeding.cat_id = pk
        new_feeding.save()
    #always redirect instead of render if changes to db
    return redirect('detail', cat_id=pk)

# assoc_toy view function
@login_required
def assoc_toy(request, pk, toy_pk):
    Cat.objects.get(id=pk).toys.add(toy_pk)
    return redirect('detail', cat_id=pk)
@login_required
def assoc_delete(request, pk, toy_pk):
    Cat.objects.get(id=pk).toys.remove(toy_pk)
    return redirect('detail', cat_id=pk)
@login_required
def add_photo(request, cat_id):
    photo_file= request.FILES.get('photo_file', None)
    if photo_file:
        # use aws sdk
        s3 = boto3.client('s3')
        #create unique key to ensure unqiue url
        key = uuid.uuid4().hex[:6] + photo_file.name[photo_file.name.rfind('.'):]
        try:
            bucket = os.environ['S3_BUCKET']
            s3.upload_fileobj(photo_file, bucket, key)
            # build full url string
            url = f"{os.environ['S3_BASE_URL']}{bucket}/{key}"
            #assign to cat
            Photo.objects.create(url=url, cat_id=cat_id)
        except Exception as e:
            print('An error occured uploading file to s3')
            print(e)
    return redirect('detail', cat_id=cat_id)

def signup(request):
    error_message = ''
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
        else:
            error_message = 'Invalid sign up - try again'
    form = UserCreationForm()
    context = {'form': form, 'error_message': error_message}
    return render(request, 'registration/signup.html', context)