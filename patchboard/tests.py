import unittest
import datetime

from prioritizeddispatcher import RequirementsTree
from circuitbreaker import CircuitBreaker, CircuitOpen

class TestRequirementsTree(unittest.TestCase):
    def assert_tree_sortment(self, tree):
        seen = set()
        for item in tree:
            seen.add(item)
            for requirement in tree._priority_table[item]:
                try:
                    self.assertTrue(requirement in seen)
                except:
                    for key, value in tree._priority_table.iteritems():
                        print key, value
                    for item in tree.sorted_items:
                        print item
                    raise

    def test_sortment(self):
        tree = RequirementsTree()
        tree.add('d', 'd', before=['z'], after=['a'])
        tree.add('e', 'e', after=['c', 'd'])
        tree.add('f', 'f', after=['e'], before=['z'])
        tree.add('a', 'a', before=['d', 'e'])
        tree.add('b', 'b', after=['a'])
        tree.add('c', 'c')
        tree.add('z', 'z')
        self.assert_tree_sortment(tree)

    def test_another_sortment(self):
        tree = RequirementsTree()
        tree.add('clear-giftcard', 'clear-giftcard', before=['order-total'])
        tree.add('item-subtotal', 'item-subtotal')
        tree.add('order-subtotal', 'order-subtotal', after=['item-subtotal'])
        tree.add('storecredit', 'storecredit', after=['order-total'])
        tree.add('giftcard', 'giftcard', after=['order-total'])
        tree.add('item-discount', 'item-discount', before=['order-subtotal', 'taxes'], after=['item-subtotal'])
        tree.add('order-total', 'order-total', after=['order-subtotal'])
        tree.add('clear-substitution', 'clear-substitution', before=['order-total'])
        tree.add('taxes', 'taxes', before=['order-total'], after=['order-subtotal'])
        tree.add('order-discount', 'order-discount', before=['order-total', 'taxes'], after=['order-subtotal'])
        tree.add('substitution', 'substitution', after=['order-total'])
        tree.add('clear-storecredit', 'clear-storecredit', before=['order-total'])
        self.assert_tree_sortment(tree)

class TestCircuitBreaker(unittest.TestCase):
    def test_breaker(self):
        class MyBreaker(CircuitBreaker):
            def run(self):
                assert not getattr(self, 'fail', False)
        
        breaker = MyBreaker(4, 600)
        self.assertTrue(breaker.is_ready())
        breaker()
        self.assertFalse(breaker.failures)
        breaker.open_circuit()
        self.assertFalse(breaker.is_ready())
        breaker.error_expiration = datetime.datetime.now()
        breaker()
        self.assertTrue(breaker.is_ready())
        breaker.fail = True
        for i in range(3):
            try:
                breaker()
            except AssertionError:
                self.assertTrue(breaker.is_ready())
            else:
                self.fail('Should have raised an exception')
        try:
            breaker()
        except AssertionError:
            self.assertFalse(breaker.is_ready())
        else:
            self.fail('Should have raised an exception')
        try:
            breaker()
        except CircuitOpen:
            pass
        else:
            self.fail('Wrong exception?')
        breaker.error_expiration = datetime.datetime.now()
        try:
            breaker()
        except:
            pass
        self.assertFalse(breaker.is_ready()) #we failed so we're not ready yet
        breaker.fail = False
        breaker.error_expiration = datetime.datetime.now()
        breaker()
        self.assertTrue(breaker.is_ready())

def runtests():
    unittest.main()

if __name__ == '__main__':
    runtests()


