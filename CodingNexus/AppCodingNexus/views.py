from django.shortcuts import render, redirect
import pyrebase, logging
from django.contrib import messages

# Firebase configuration
config = {
    "apiKey": "AIzaSyAqy5Qbf7c6eOyB65AVYqbagVh7dbeWlNM",
    "authDomain": "coding-nexus-a0713.firebaseapp.com",
    "databaseURL": "https://coding-nexus-a0713-default-rtdb.asia-southeast1.firebasedatabase.app",
    "projectId": "coding-nexus-a0713",
    "storageBucket": "coding-nexus-a0713.appspot.com",
    "messagingSenderId": "757069789705",
    "appId": "1:757069789705:web:0e0182530be7d353e156d8",
}

firebase = pyrebase.initialize_app(config)
authe = firebase.auth()
database = firebase.database()

def home(request):
    if 'uid' in request.session:
        # User is logged in
        return render(request, 'index.html', {'logged_in': True})
    else:
        # User is not logged in
        return render(request, 'index.html', {'logged_in': False})

def user_login(request):
    return render(request, 'login.html')

def user_register(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            # Create user using Firebase Authentication
            user = authe.create_user_with_email_and_password(email, password)
            uid = user['localId']  # Get the user ID

            # Store user email in Firebase Realtime Database
            data = {
                "email": email,
            }
            database.child("users").child(uid).set(data)

            # Redirect to login page after successful registration
            messages.success(request, 'Account created successfully! Please login.')
            return redirect('login')
        
        except Exception as e:
            error_message = str(e)
            
            # Check if the error is due to a weak password or other specific issues
            if "WEAK_PASSWORD" in error_message:
                user_friendly_message = "Your password must be at least 6 characters long."
            elif "EMAIL_EXISTS" in error_message:
                user_friendly_message = "An account with this email already exists."
            elif "INVALID_EMAIL" in error_message:
                user_friendly_message = "The email address is not valid."
            else:
                user_friendly_message = "An error occurred. Please try again."
            
            # Log the detailed error for developers
            logging.error(f"Error during registration: {error_message}")
            
            # Display user-friendly error message
            messages.error(request, user_friendly_message)
            return render(request, 'register.html')

    return render(request, 'register.html')

def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            # Log in user using Firebase Authentication
            user = authe.sign_in_with_email_and_password(email, password)
            session_id = user['idToken']  # Firebase session token
            request.session['uid'] = str(session_id)  # Store the session token
            
            return redirect('home')  # Redirect to the home page upon successful login

        except Exception as e:
            # Handle login error and display a user-friendly error message
            error_message = str(e)  # Firebase returns error details, we can log this if necessary
            messages.error(request, "Invalid email or password. Please try again.")  # Display error to the user
            return render(request, 'login.html')

    return render(request, 'login.html')  # Render the login page if GET request or form submission fails

# Optional logout function to destroy the session
def user_logout(request):
    try:
        del request.session['uid']  # Delete session
        messages.success(request, 'Logged out successfully!')
    except KeyError:
        pass
    return redirect('login')