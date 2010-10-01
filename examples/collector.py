from django.dispatch import Signal

#our signal
collect_reviews = Signal(providing_args=["product"])

#our collector
def get_reviews(product):
    reviews = list()
    def _scores():
        for review in reviews:
            yield review['score']
    
    for listener, value in collect_reviews.send(sender=None, product=product):
        if value:
            reviews.extend(value)
    average = sum(_scores())/len(reviews)
    return reviews, average

def always_give_bad_review(product, **kwargs):
    return [{'score':0, 'message':'Worse product ever', 'author':'James Smith'}]

collect_reviews.connect(always_give_bad_review)



from patchboard.circuitbreaker import circuit_breaker
import urllib2
import simplejson

#this listener hits the wire, so protect it with a circuit_breaker
def give_reviews_from_wire(product, **kwargs):
    response = urllib2.urlopen('http://www.somesite.com/api?product=%s' % product.sku)
    return simplejson.loads(response.read())

collect_reviews.connect(circuit_breaker(give_reviews_from_wire, threshold=5, timeout=10, default=lambda: None))

