import sys
import unittest
import unittest.mock
from sqlean import dbapi2 as sqlite


class Test(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite.connect(":memory:")

    def tearDown(self):
        self.conn.close()

    def test_crypto(self):
        self._assert_eq("hex(md5('abc'))", "900150983cd24fb0d6963f7d28e17f72".upper())
        self._assert_eq("encode('abcd', 'base64')", "YWJjZA==")
        self._assert_eq("decode('YWJjZA==', 'base64')", b"abcd")

    def test_define(self):
        self._assert_eq("define('sumn', '?1 * (?1 + 1) / 2')", None)
        self._assert_eq("sumn(5)", (1 + 2 + 3 + 4 + 5))
        self._assert_eq("eval('select abs(-42)')", "42")
        self._assert_eq("define_free()", None)

    def test_fuzzy(self):
        self._assert_eq("dlevenshtein('abc', 'abcd')", 1)
        self._assert_eq("caverphone('awesome')", "AWSM111111")

    @unittest.skipIf(sys.platform == "win32", "ipaddr is not supported on windows")
    def test_ipaddr(self):
        self._assert_eq("iphost('192.168.16.12/24')", "192.168.16.12")
        self._assert_eq("ipcontains('192.168.16.0/24', '192.168.16.3')", 1)

    def test_math(self):
        self._assert_eq("trunc(3.9)", 3)
        self._assert_eq("sqrt(100)", 10)
        self._assert_eq("round(degrees(pi()))", 180)

    def test_regexp(self):
        self._assert_eq("regexp_replace('1 10 100', '\d+', '**')", "** ** **")
        self._assert_eq("regexp_substr('abcdef', 'b(.)d')", "bcd")
        self._assert_eq("regexp_capture('abcdef', 'b(.)d', 1)", "c")

    def test_stats(self):
        self._assert_eq("percentile(value, 50) from generate_series(1, 99)", 50)
        self._assert_eq("median(value) from generate_series(1, 99)", 50)

    def test_text(self):
        self._assert_eq("text_substring('hello world', 7)", "world")
        self._assert_eq("text_split('one|two|three', '|', 2)", "two")
        self._assert_eq("text_translate('hello', 'l', '1')", "he11o")

    def test_uuid(self):
        self._assert_eq("length(uuid4())", 36)

    def test_unicode(self):
        self._assert_eq("nupper('пРиВеТ')", "ПРИВЕТ")
        self._assert_eq("unaccent('hôtel')", "hotel")

    def _assert_eq(self, expr, want):
        cur = self.conn.execute(f"select {expr}")
        got = cur.fetchone()[0]
        self.assertEqual(got, want)


def suite():
    return unittest.TestSuite((unittest.makeSuite(Test),))


def test():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == "__main__":
    test()
