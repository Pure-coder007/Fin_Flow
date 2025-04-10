import random, string
from django.core.mail import send_mail, EmailMessage
from .models  import OneTimePassword, UserAccount, User
from django.conf import settings


def generate_otp():
    otp = ""
    for i in range(6):
        otp += str(random.randint(0, 9))
    return otp


def send_otp(email):
    Subject="One time passcode for email verification"
    otp_code=generate_otp()
    print(otp_code, "OTP CODE")
    
    user=User.objects.get(email=email)
    current_site="Mysite.com"
    email_body=f" Hi {user.first_name}, thanks for signing up on {current_site}.\n Your one time passcode for email verification is {otp_code}"
    from_email=settings.DEFAULT_FROM_EMAIL
    
    OneTimePassword.objects.create(user=user, code=otp_code)
    send_email=EmailMessage(subject=Subject, body=email_body, from_email=from_email, to=[email])
    
    send_email.send(fail_silently=True)
    
    
    

def wallet_funding_success(email, amount):
    subject = "Wallet funding successful"
    
    user = User.objects.get(email=email)
    email_body = f"""
    Hi {user.first_name},
    
    You have successfully funded your Fin Flow wallet with ₦{amount:,.2f}.
    
    Thank you for using Fin Flow to manage your finances.
    
    Best regards,
    Fin Flow Team
    """
    
    from_email = settings.DEFAULT_FROM_EMAIL
    send_email = EmailMessage(
        subject=subject, 
        body=email_body, 
        from_email=from_email, 
        to=[user.email]
    )
    send_email.send(fail_silently=True)
    
    return "Email sent successfully"
