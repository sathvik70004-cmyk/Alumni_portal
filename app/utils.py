# app/utils.py

import os
from PIL import Image
from flask import current_app # To access the app configuration and paths

def save_profile_picture(form_picture, alumni_id):
    """
    Saves the uploaded picture to the static folder, resizing it first.
    Returns the filename to be stored in the database.
    """
    # 1. Generate a unique filename based on user ID
    filename_ext = 'user_' + str(alumni_id) + '.png'
    
    # 2. Define the full path where the file will be saved
    picture_path = os.path.join(current_app.root_path, 'static/images', filename_ext)
    
    # 3. Resize and save the image
    output_size = (150, 150) # Standardize image size for profile card
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    
    # Save as PNG
    i.save(picture_path)
    
    return filename_ext

# You can add a placeholder image file named 'default_user.png' 
# to your app/static/images folder for users without a photo.