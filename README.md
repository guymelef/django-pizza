# Project 3

Web Programming with Python and JavaScript

## PIZZA
A Django web app for ordering pizza. Live at https://pizza4cs50w.herokuapp.com/

### DESCRIPTION
This Django project is composed of three apps:

- **orders** : Where menu items are shown
- **accounts** : To separate user account views
- **cart** : For updating cart items and processing orders

Admin page is located at `i/am/an/admin`.
As a *personal touch*, **Stripe** API is implemented as a payment option. Admin can also mark orders as paid, complete, etc by loggin into the admin page.