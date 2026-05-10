import re

def is_strong_password(password):
    return (
        len(password) >= 8 and
        re.search(r'[A-Za-z]', password) and
        re.search(r'\d', password) and
        re.search(r'[!@#$%^&*(),.?":{}|<>_\-]', password)
    )

#security checklist:
#csrf protection with wtforms
#strongpassword check function 
#rate limiting
#authentication login with flask login
#password security with werkzeug (salted hash)
#route protection via login_required
#sql injection prevention via SQLAlchemy ORM
