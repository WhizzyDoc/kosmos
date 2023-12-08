from django.conf import Settings
from django.core.mail import send_mail


def send_password_email(receiver, name, new_password):
    subject = f"Password Reset Request"
    message = ''
    from_email = 'encrane04@gmail.com'  # Sender's email
    recipient_list = [receiver]  # List of recipient emails
    html_message = f"""
    <div style="text-align:left; font-family: 'Lucida Sans', 'Lucida Sans Regular', 'Lucida Grande', 'Lucida Sans Unicode', Geneva, Verdana, sans-serif;">
    <h4>Dear {name},<h4><br><br>
    <p>You have requested a password reset. your new temporary password is <span style="color:blue;font-weight:600">{new_password}</span></p>
    <p>Kindly change your password after logging in.</p><br><br>
    <h4>Best Regards,<h4>
    <h4>KosmosHR.</h4>
    </div>
    """
    fail_silently = False
    send_mail(subject, message, from_email, recipient_list, fail_silently, html_message=html_message)

def confirmation_email(receiver, name):
    subject = f"KosmosHR Confirm Email"
    message = ''
    from_email = 'encrane04@gmail.com'  # Sender's email
    recipient_list = [receiver]  # List of recipient emails
    html_message = f"""
    <div style="text-align:center; font-family: 'Lucida Sans', 'Lucida Sans Regular', 'Lucida Grande', 'Lucida Sans Unicode', Geneva, Verdana, sans-serif;">
    <h4>Dear {name},<h4><br><br>
    <p>This is to confirm that you have registered an account on <b>KosmosHR</b>.</p>
    <br><br>
    <p>We hope that you enjoy your experience with us.</p><br><br>
    <h4>Best Regards,<h4>
    <h4>KosmosHR.</h4>
    </div>
    """
    fail_silently = False
    send_mail(subject, message, from_email, recipient_list, fail_silently, html_message=html_message)
   
def send_new_employee_email(receiver, name, username, password):
    subject = f"KosmosHR Employee Onboarding"
    message = ''
    from_email = 'encrane04@gmail.com'  # Sender's email
    recipient_list = [receiver]  # List of recipient emails
    html_message = f"""
    <div style="text-align:center; font-family: 'Lucida Sans', 'Lucida Sans Regular', 'Lucida Grande', 'Lucida Sans Unicode', Geneva, Verdana, sans-serif;">
    <h4>Dear {name},<h4><br><br>
    <p>We are happy to inform you that you have been successfuly onboarded as a new employee at KosmosHR.</p>
    <p>
    Your login details are as follows:<br>
    <span style="font-weight:600">Username:</span> {username}<br>
    <span style="font-weight:600">Password:</span> {password}<br>
    </p><br><br>
    <p>Kindly change your password after logging in.</p><br><br>
    <h4>Best Regards,<h4>
    <h4>KosmosHR.</h4>
    </div>
    """
    fail_silently = False
    send_mail(subject, message, from_email, recipient_list, fail_silently, html_message=html_message)
