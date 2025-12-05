from email.mime.text import MIMEText


def send_match_email(to_email, user_name, match_name):
    if not to_email:
        return

    subject = "💕 You have a match on LoveDove!"
    body = f"Hi {user_name},\n\nGreat news! {match_name} likes you back! You're both in love! 💕\n\nBest regards,\nLoveDove Team"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = "noreply@lovedove.com"
    msg["To"] = to_email

    # For demo purposes, just print the email instead of actually sending
    print(f"EMAIL TO: {to_email}")
    print(f"SUBJECT: {subject}")
    print(f"BODY: {body}")
    print("---")
