from datetime import date

def calculate_age(birth_date):
    """محاسبه سن بر اساس تاریخ تولد"""
    today = date.today()
    return today.year - birth_date.year - (
        (today.month, today.day) < (birth_date.month, birth_date.day)
    )


GENDER_CHOICES = (
        ('male', 'Man'),
        ('female', 'Woman'),
        ('other', 'Other')
    )