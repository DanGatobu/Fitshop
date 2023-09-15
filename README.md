# FitShop Django Web Application

FitShop is a web application built with Django, designed to offer users an easy and convenient way to shop for fitness products. The application integrates with Firebase for user authentication, real-time database, and cloud storage.

## Features

- User Registration and Authentication: Users can sign up for an account, log in, and log out. Email verification is implemented for added security.

- Product Management: Admins can add new fitness products to the platform, including details such as name, category, price, description, and images. Product details are stored in a Firebase Realtime Database.

- Product Catalog: Users can browse through a catalog of fitness products, view product details, and add items to their shopping cart.

- Shopping Cart: Users can add and remove items from their shopping cart, update quantities, and proceed to checkout.

- Checkout and Payment: Integration with PayPal for secure payment processing. Users can review their cart, enter shipping details, and complete the purchase.

- Product Recommendations: The application provides recommendations for similar products based on the user's selected item category.

## Technologies Used

- Django: A high-level Python web framework used for building the backend of the application.

- Firebase: Firebase is used for authentication, real-time database storage, and cloud storage for product images.

- PayPal API: Integration with PayPal's payment processing API for secure and convenient online payments.

- Pyrebase: A Python wrapper for the Firebase API, used for authentication and database operations.

## Setup

1. Clone the repository to your local machine.
2. Install the required Python packages using `pip install -r requirements.txt`.
3. Configure Firebase by creating a Firebase project and adding your Firebase configuration details to the `config` dictionary in `views.py`.
4. Run the Django development server using `python manage.py runserver`.

## Usage

- Visit the application in your web browser and explore the features.
- Admins can access the admin panel to manage products by going to `/admin`.

## Project Structure

- `views.py`: Contains the Django views for user registration, product management, shopping cart, and checkout.
- `templates/`: Directory containing HTML templates for rendering the web pages.
- `static/`: Static files, including CSS, JavaScript, and images.
- `google_service_account.json`: Firebase service account credentials for authentication.

