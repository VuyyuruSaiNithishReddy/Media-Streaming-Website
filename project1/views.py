import os
from django.conf import settings
from project1.forms import DocumentForm
from django.shortcuts import render , redirect
from .models import Movie ,Document
from django.contrib import messages
from django.contrib.auth.models import User , auth
from django.core.mail import send_mail
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
from django.views.generic.edit import FormView
import math as m
import random as r
import urllib.request
import re
import pandas as pd
import numpy as np
import yaml
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# function to generate OTP 
""" function to generate otp based on the string , modified otp(def register:) based on the phone number giver by the user  
def OTPgen() : 
	string = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
	OTP = "" 
	varlen= len(string) 
	for i in range(6) : 
		OTP += string[m.floor(r.random() * varlen)] 
  
	return (OTP)
OTP = OTPgen() """
OTP = ""
def login(request):
	if request.method=='POST':
		username = request.POST['username']
		password = request.POST['password']

		user = auth.authenticate(username=username,password=password)

		if user is not None:
			auth.login(request,user)
			return redirect('home')
		else:
			messages.info(request,'invalid credentials')
			return redirect('login')

	else:
		return render(request,'login.html')

def register(request):
	if request.method == 'POST':
		first_name = request.POST['first_name']
		last_name = request.POST['last_name']
		username = request.POST['username']
		password1 = request.POST['password1']
		password2 = request.POST['password2']
		email = request.POST['email']
		phonenum = request.POST['phonenum']
		if password1==password2:
			if User.objects.filter(username=username).exists():
				messages.success(request,'Username taken')
				print('username taken')
				return redirect('register')
			elif User.objects.filter(email=email).exists():
				messages.success(request,'email taken')
				print('email taken')
				return redirect('register')
			else:
				#OTP CHANGED
				ot = ""
				varlen= len(phonenum)
				for i in range(4) :
					ot += phonenum[m.floor(r.random() * varlen)]
				global OTP
				OTP = ot
				print('mail sent to :'+ email)
				conf = yaml.load(open('project1/credentials.yml'), Loader=yaml.FullLoader)
				sender_email = conf['user']['email']
				send_mail(
					subject="Your OTP Password in mywebapp",
					message="Your OTP password is : " + str(ot),
					from_email=sender_email,
					recipient_list=[email]
				)
				print("OTP sent to mail: "+ ot)
				request.session['username'] = username
				request.session['password1'] = password1
				request.session['email'] = email
				request.session['first_name'] = first_name
				#request.session['last_name'] = last_name
				messages.success(request,'OTP sent to '+email)
				return render(request,'otp.html')
		else:
			messages.success(request, 'password not matching')
			print('password not matching')
			return redirect('register')
		
	else:
		return render(request,'register.html')

#OTP
def otp(request):
	code = request.POST.get('text')
	print(code,OTP)
	if code == OTP:
		username = request.session.get('username')
		password1 = request.session.get('password1')
		email = request.session.get('email')
		first_name = request.session.get('first_name')
		#last_name = request.session('last_name')
		user = User.objects.create_user(username=username,password=password1,email=email,first_name=first_name)#,last_name=last_name
		user = request.POST.get('user')
		#user.save();
		messages.success(request, 'Account Created Login to continue.')
		print('user created')
		return render(request,'login.html')
	else:
		messages.success(request, 'OTP not matching')
		return render(request,'otp.html') 


# home
def home(request):
	movielist = Movie.objects.all()
	path = settings.MEDIA_ROOT
	img_lis = os.listdir(path + '/coverpics')
	#contex = {'image' : img_lis , 'movie':movielist}
	mylist=zip(movielist,img_lis)
	return render(request,"home.html",{'mylist':mylist})

""" def movies(request):

	path = settings.MEDIA_ROOT
	img_list = os.listdir(path + '/UserUploads')
	context = {'images' : img_list}
	return render(request,"movies.html",context) """


#logout
def logout(request):
	auth.logout(request)
	return redirect('/')

def model_form_upload(request):
	if request.method == 'POST':
		form = DocumentForm(request.POST, request.FILES)
		if form.is_valid():
			form.save();
			return redirect('home')
	else:
		form = DocumentForm()
	return render(request, 'model_form_upload.html', {
		'form': form
	})

#recomondations based on the user search
def recommendation(request):
		
	###### helper functions. Use them when needed #######
	def get_title_from_index(index):
		return df[df.index == index]["title"].values[0]

	def get_index_from_title(title):
		return df[df.title == title]["index"].values[0]
	##################################################

	##Step 1: Read CSV File
	df = pd.read_csv("movie_dataset.csv")

	#print(df.columns)
	##Step 2: Select Features

	features = ['keywords','cast','genres','director']
	##Step 3: Create a column in DF which combines all selected features
	for feature in features:
		df[feature] = df[feature].fillna('')

	def combine_features(row):
		try:
			return row['keywords'] +" "+row['cast']+" "+row["genres"]+" "+row["director"]
		except:
			print("Error: ", row)	

	df["combined_features"] = df.apply(combine_features,axis=1)

	#print("Combined Features:", df["combined_features"].head())

	##Step 4: Create count matrix from this new combined column
	cv = CountVectorizer()

	count_matrix = cv.fit_transform(df["combined_features"])

	##Step 5: Compute the Cosine Similarity based on the count_matrix
	cosine_sim = cosine_similarity(count_matrix)
	movie_user_likes = "Avatar"

	movie_user_likes = request.POST['moviename']
	

	## Step 6: Get index of this movie from its title
	movie_index = get_index_from_title(movie_user_likes)


	similar_movies =  list(enumerate(cosine_sim[movie_index]))

	## Step 7: Get a list of similar movies in descending order of similarity score
	sorted_similar_movies = sorted(similar_movies,key=lambda x:x[1],reverse=True)

	## Step 8: Print titles of first 5 movies
	i=0
	temp=""
	rname=[]
	for element in sorted_similar_movies:
			temp=get_title_from_index(element[0])
			i=i+1
			rname.append(temp)
			if i>5:
				break
	links=[]
	
	for search_keyword in rname:
		search_keyword = search_keyword.replace(' ', '+')
		html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + search_keyword +"+trailer")
		video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
		links.append("https://www.youtube.com/embed/"+ video_ids[0])
	
	mlinks = zip(rname, links)
	context = {
            'mlinks': mlinks,
        }
	#return render(request, 'template.html', context)
	return render(request,"recommendation.html",context)
#requesting a movie	
def mvoierequest(request):
	mreq = request.POST['mname']
	email='sainithish.vuyyuru@gmail.com'
	send_mail(
				subject="request from users",
				message="requested a movie " + mreq,
				from_email='121710308059@gitam.in',
				recipient_list=[email]
			)
	return redirect('home')

def dblist(request):
	def get_title_from_index(index):
		return df[df.index == index]["title"].values[0]

	def get_index_from_title(title):
		return df[df.title == title]["index"].values[0]
	##################################################

	##Step 1: Read CSV File
	df = pd.read_csv("movie_dataset.csv")

	#print(df.columns)
	##Step 2: Select Features

	features = ['keywords','cast','genres','director']
	##Step 3: Create a column in DF which combines all selected features
	for feature in features:
		df[feature] = df[feature].fillna('')

	def combine_features(row):
		try:
			return row['keywords'] +" "+row['cast']+" "+row["genres"]+" "+row["director"]
		except:
			print("Error: ", row)	

	df["combined_features"] = df.apply(combine_features,axis=1)

	#print("Combined Features:", df["combined_features"].head())

	##Step 4: Create count matrix from this new combined column
	cv = CountVectorizer()

	count_matrix = cv.fit_transform(df["combined_features"])

	##Step 5: Compute the Cosine Similarity based on the count_matrix
	cosine_sim = cosine_similarity(count_matrix)
	movie_user_likes = "Avatar"

	

	## Step 6: Get index of this movie from its title
	movie_index = get_index_from_title(movie_user_likes)


	similar_movies =  list(enumerate(cosine_sim[movie_index]))

	## Step 7: Get a list of similar movies in descending order of similarity score
	sorted_similar_movies = sorted(similar_movies,key=lambda x:x[1],reverse=True)

	## Step 8: Print titles of first 5 movies
	i=0
	temp=""
	dbname =[]
	for element in sorted_similar_movies:
			temp=get_title_from_index(element[0])
			i=i+1
			dbname.append(temp)
	db_name = {
            'dbname': dbname,
        }
	return render(request,"dblist.html",db_name)