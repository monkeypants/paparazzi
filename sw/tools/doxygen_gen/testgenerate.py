import unittest
import generate

class TestFoo(unittest.TestCase):
    def test_foo(self):
        assert 1>0

# get_paparazzi_home
#    - if PAPARAZZI_HOME set, return it
#    - for various cwd's
#      - if PAPARAZZI_HOME not set
#        - return a sensible guess
#        - raise a sensible warning
#
# use logging

if __name__ == "__main__":
    unittest.main()
