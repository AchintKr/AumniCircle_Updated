from django.core.mail import send_mail,EmailMessage
import os
from django.conf import settings
from django.urls import reverse

def send_forget_password_mail(email,token):
    subject = 'Your forget password link by support@alumnicircle'
    message = f'Hi , Please click on the link to reset your password http://127.0.0.1:8000/change-password/{token}/'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject,message,email_from,recipient_list)
    
def send_feedback(feedback):
    subject = f'A feedback Recieved on {feedback.feedback_type}'
    message = (f'{feedback.name}({feedback.user_type}):- {feedback.feedback_text}'
               f'Email id :- {feedback.email}')
    email_from = settings.EMAIL_HOST_USER   
    recipient_list = ["ankitspc007@gmail.com"]
    send_mail(subject,message,email_from,recipient_list)
     
def send_verification_email(profile):
    verification_link = f"http://127.0.0.1:8000/verify-college/{profile.id}/"
    subject = 'Verify College ID'
    recipient_list = ["kanishk.01kumar01@gmail.com"]  # Add campus ambassador's email here
    email_from = settings.EMAIL_HOST_USER

    # Email content
    message = (
        f"Please verify the college ID for {profile.idimg}. "
        f"The given registration ID is: {profile.regid}. "
        f"Click the link below to verify:\n\n{verification_link}"
    )

    # Create the email
    email = EmailMessage(subject, message, email_from, recipient_list)

    # Attach image
    if profile.idimg and profile.idimg.name != 'blank_profile.jpg':
        image_path = profile.idimg.path
        if os.path.exists(image_path):
            email.attach_file(image_path)
        else:
            print("File not found:", image_path)
    else:
        print("No custom image found, or using default image.")

    # Send the email
    email.send(fail_silently=False)
    
    
def send_reconfirmation_email(donation):
    verification_link = f"http://127.0.0.1:8000/confirm-donation/{donation.id}/"

    subject = f"New Donation Received - {donation.full_name}"
    message = (
        f"A new donation has been made by {donation.full_name}.\n\n"
        f"Details:\n"
        f"Amount: {donation.amount} INR\n"
        f"Donation Type: {donation.donation_type}\n"
        f"Transaction ID: {donation.transaction_id}\n"
        f"Phone: {donation.phone}\n"
        f"Email: {donation.email}\n"
        f"Graduation Year: {donation.graduation_year}\n\n"
        f"Please confirm this donation using the following link:\n"
        f"{verification_link}\n"
    )
    email_from =  settings.EMAIL_HOST_USER# Replace with your actual email
    recipient_list = ["kanishk.01kumar01@gmail.com"]  # Replace with the administrator's email
    try:
        send_mail(subject, message, email_from, recipient_list)
        print("Reconfirmation email sent successfully")
    except Exception as e:
        print(f"Error sending email: {e}")


def send_certificate(donation):
        subject = f"Thank You for Your Donation, {donation.full_name} !"
        message = (
            f"Dear {donation.full_name},\n\n"
            f"Thank you for your generous donation of {donation.amount} INR. "
            f"Best regards,\nThe Alumni Circle Team "
        )
        print("EMail to be send")
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [donation.email]

        email = EmailMessage(subject, message, email_from, recipient_list)
        email.send(fail_silently=False)
        
        # certificate_path = f'path_to_certificates/{self.full_name}_certificate.pdf'
        # if os.path.exists(certificate_path):
        #     email.attach_file(certificate_path)
        # else:
        #     print("Certificate file not found:", certificate_path)
