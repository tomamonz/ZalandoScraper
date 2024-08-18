from flask import Blueprint, session, redirect, url_for, request, render_template, jsonify
import google_auth_oauthlib.flow
import google.oauth2.credentials
import googleapiclient.discovery
import os
import json
from .zalando_scraper import fetch_zalando_page_content, check_sizes_in_page_source

main = Blueprint('main', __name__)



# Main page route
@main.route('/')
def index():
    # Check if the user is logged in
    if 'credentials' not in session:
        return render_template('index.html')
    
    # Fetch the profile information
    credentials = google.oauth2.credentials.Credentials(**session['credentials'])
    service = googleapiclient.discovery.build('people', 'v1', credentials=credentials)
    profile_info = service.people().get(resourceName='people/me', personFields='names,emailAddresses').execute()

    # Extract and display the user's name and email
    name = profile_info['names'][0]['displayName']
    email = profile_info['emailAddresses'][0]['value']

    return render_template('confirmation.html', name=name, email=email)

@main.route('/confirmation')
def confirmation():
    # Assuming this route is present for the confirmation page
    return render_template('confirmation.html')

@main.route('/check_sizes')
def check_sizes():
    cookies = request.cookies
    # Fetch Zalando page content using Selenium
    page_content = fetch_zalando_page_content(cookies)
    print(page_content)
    # Define sizes to check
    defined_sizes = [42.5, 44]

    # Check sizes in the page source
    size_stock_status = check_sizes_in_page_source(page_content, defined_sizes)

    # Render the results in the results.html template
    return render_template('results.html', size_stock_status=size_stock_status)

@main.route('/check_sizes_ajax')
def check_sizes_ajax():
    try:    
        cookies = request.cookies
        # Fetch Zalando page content using Selenium
        print("Cookies in Flask session:")
        for name, value in cookies.items():
            print(f"Name: {name}, Value: {value}")
        page_content = fetch_zalando_page_content(cookies)

        # Define sizes to check
        defined_sizes = [42.5, 43, 44]

        # Check sizes in the page source
        size_stock_status = check_sizes_in_page_source(page_content, defined_sizes)

        # Return the results as JSON
        return render_template('results.html', size_stock_status=size_stock_status)
    except Exception as e:
        return render_template('results.html', size_stock_status=str(e))