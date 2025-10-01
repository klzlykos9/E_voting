from django.shortcuts import render, redirect, reverse
from .email_backend import EmailBackend
from django.contrib import messages
from .forms import CustomUserForm
from voting.forms import VoterForm
from django.contrib.auth import login, logout
# Create your views here.


def account_login(request):
    if request.user.is_authenticated:
        if request.user.user_type == '1':
            return redirect(reverse("adminDashboard"))
        else:
            return redirect(reverse("voterDashboard"))

    context = {}
    if request.method == 'POST':
        user = EmailBackend.authenticate(request, username=request.POST.get(
            'email'), password=request.POST.get('password'))
        if user != None:
            login(request, user)
            if user.user_type == '1':
                return redirect(reverse("adminDashboard"))
            else:
                return redirect(reverse("voterDashboard"))
        else:
            messages.error(request, "Invalid details")
            return redirect("/")

    return render(request, "voting/login.html", context)



import os
import uuid
from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
import trainer
import threading
def account_register(request):
    userForm = CustomUserForm(request.POST or None, request.FILES or None)
    voterForm = VoterForm(request.POST or None, request.FILES or None)
    
    context = {
        'form1': userForm,
        'form2': voterForm
    }
    
    if request.method == 'POST':

        # Collect all face images from the request
        face_images = []
        for i in range(1, 11):
            image_key = f'face_image_{i}'
            if image_key in request.FILES:
                face_images.append(request.FILES[image_key])
        
        # Validate image count
        if len(face_images) != 10:
            messages.error(request, "Please upload exactly 10 face images")
            return render(request, "voting/reg.html", context)
        
        if userForm.is_valid() and voterForm.is_valid():
            # Create a unique identifier for the user's face image folder
            unique_folder_name = userForm.cleaned_data['last_name'] + " " + userForm.cleaned_data['first_name'] 
            user_face_folder = os.path.join(settings.BASE_DIR, 'user_faces', unique_folder_name)
            
            # Create the user folder
            os.makedirs(user_face_folder, exist_ok=True)
            
            # Save the user
            user = userForm.save(commit=False)
            voter = voterForm.save(commit=False)
            
            # Save the user first
            user.save()
            
            # Link voter to the user
            voter.admin = user
            voter.save()
            
            # Save face images
            try:
                for i, image in enumerate(face_images, 1):
                    # Generate a unique filename for each image
                    image_filename = f'face_image_{i}.jpg'
                    image_path = os.path.join(user_face_folder, image_filename)
                    
                    # Save the image
                    with open(image_path, 'wb+') as destination:
                        for chunk in image.chunks():
                            destination.write(chunk)
                
                messages.success(request, "Account created successfully. You can now login!")
                threading.Thread(target=trainer.encode).start()
                return redirect(reverse('account_login'))
            
            except Exception as e:
                # Rollback user creation if image saving fails
                user.delete()
                voter.delete()
                messages.error(request, f"Error saving images: {str(e)}")
                return render(request, "voting/reg.html", context)
        
        else:
            messages.error(request, "Provided data failed validation")
    
    return render(request, "voting/reg.html", context)

def account_logout(request):
    user = request.user
    if user.is_authenticated:
        logout(request)
        messages.success(request, "Thank you for visiting us!")
    else:
        messages.error(
            request, "You need to be logged in to perform this action")

    return redirect(reverse("account_login"))
