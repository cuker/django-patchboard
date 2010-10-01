from django.dispatch import Signal

collect_reviews = Signal(providing_args=["product"])

def get_reviews(product):
    reviews = list()
    for listener, value in collect_reviews.send(sender=None, product=product):
        if value:
            reviews.extend(value)
    return reviews

def always_give_bad_review(product, **kwargs):
    return [{'score':0, 'message':'Worse product ever', 'author':'James Smith'}]

collect_reviews.connect(always_give_bad_review)
