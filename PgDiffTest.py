import argparse
from difflib import unified_diff

from PgDiff import PgDiff
from helpers.Writer import Writer

class PgDiffTestFailedException(Exception):
    def __init__(self, testCase, diff):
        self.testCase = testCase
        self.diff = diff

    def __str__(self):
        message = []
        message.append('Failed test name [%s]:\n' % self.testCase)
        for line in self.diff:
            message.append(line)
        return ''.join(message)



class PgDiffTest(object):

    testCases = {
        "modify_column_type": ("modify_column_type", False, False, False, False),
        "drop_with_oids": ("drop_with_oids", False, False, False, False),
        "add_index": ("add_index", False, False, False, False),
        "drop_index": ("drop_index", False, False, False, False),
        "drop_index_with_cluster": ("drop_index_with_cluster", False, False, False, False),
        "modify_index": ("modify_index", False, False, False, False),
        "add_statistics": ("add_statistics", False, False, False, False),
        "modify_statistics": ("modify_statistics", False, False, False, False),
        "drop_statistics": ("drop_statistics", False, False, False, False),
        "add_default_value": ("add_default_value", False, False, False, False),
        "modify_default_value": ("modify_default_value", False, False, False, False),
        "drop_default_value": ("drop_default_value", False, False, False, False),
        "add_not_null": ("add_not_null", False, False, False, False),
        "drop_not_null": ("drop_not_null", False, False, False, False),
        "add_column": ("add_column", False, False, False, False),
        "drop_column": ("drop_column", False, False, False, False),
        "add_table": ("add_table", False, False, False, False),
        "drop_table": ("drop_table", False, False, False, False),
        "add_constraint": ("add_constraint", False, False, False, False),
        "modify_constraint": ("modify_constraint", False, False, False, False),
        "drop_constraint": ("drop_constraint", False, False, False, False),
        "add_unique_constraint": ("add_unique_constraint", False, False, False, True),
        "add_inherits": ("add_inherits", False, False, False, False),
        "modify_inherits": ("modify_inherits", False, False, False, False),
        "modify_sequence_increment": ("modify_sequence_increment", False, False, False, False),
        "modify_sequence_start_ignore_off": ("modify_sequence_start_ignore_off", False, False, False, False),
        "modify_sequence_start_ignore_on": ("modify_sequence_start_ignore_on", False, False, False, True),
        "modify_sequence_minvalue_set": ("modify_sequence_minvalue_set", False, False, False, False),
        "modify_sequence_minvalue_unset": ("modify_sequence_minvalue_unset", False, False, False, False),
        "modify_sequence_maxvalue_set": ("modify_sequence_maxvalue_set", False, False, False, False),
        "modify_sequence_maxvalue_unset": ("modify_sequence_maxvalue_unset", False, False, False, False),
        "modify_sequence_cache": ("modify_sequence_cache", False, False, False, False),
        "modify_sequence_cycle_on": ("modify_sequence_cycle_on", False, False, False, False),
        "modify_sequence_cycle_off": ("modify_sequence_cycle_off", False, False, False, False),
        "modify_function_end_detection": ("modify_function_end_detection", False, False, False, False),
        "add_function_noargs": ("add_function_noargs", False, False, False, False),
        "drop_function_noargs": ("drop_function_noargs", False, False, False, False),
        "drop_function_similar": ("drop_function_similar", False, False, False, False),
        "modify_function_similar": ("modify_function_similar", False, False, False, False),
        "function_equal_whitespace": ("function_equal_whitespace", False, False, True, False),
        "add_trigger": ("add_trigger", False, False, False, False),
        "drop_trigger": ("drop_trigger", False, False, False, False),
        "modify_trigger": ("modify_trigger", False, False, False, False),
        "add_view": ("add_view", False, False, False, False),
        "drop_view": ("drop_view", False, False, False, False),
        "modify_view": ("modify_view", False, False, False, False),
        "add_defaults": ("add_defaults", True, False, False, False),
        "multiple_schemas": ("multiple_schemas", False, False, False, False),
        "multiple_schemas":("multiple_schemas", False, False, False, False),
        "alter_view_drop_default": ("alter_view_drop_default", False, False, False, False),
        "alter_view_add_default": ("alter_view_add_default", False, False, False, False),
        "add_comments":("add_comments", False, False, False, False),
        "drop_comments": ("drop_comments", False, False, False, False),
        "alter_comments": ("alter_comments", False, False, False, False),
        "alter_view_change_default": ("alter_view_change_default", False, False, False, False),
        "add_sequence_bug2100013": ("add_sequence_bug2100013", False, False, False, False),
        "view_bug3080388": ("view_bug3080388", False, False, False, False),
        "function_bug3084274": ("function_bug3084274", False, False, False, False),
        "add_comment_new_column": ("add_comment_new_column", False, False, False, False),
        "quoted_schema": ("quoted_schema", False, False, False, False),
        "add_column_add_defaults": ("add_column_add_defaults", True, False, False, False),
        "add_owned_sequence": ("add_owned_sequence", False, False, False, False),
        "add_empty_table": ("add_empty_table", False, False, False, False)
    }

    testFilesPrefix = 'tests/sqls'

    @staticmethod
    def run(testName, addDefaults=False, addTransaction=False,
            ignoreFunctionWhitespace=False, ignoreStartWith=False):

        writer = Writer()

        arguments.old_dump = '%s/%s_original.sql' % (PgDiffTest.testFilesPrefix, testName)
        arguments.new_dump = '%s/%s_new.sql' %  (PgDiffTest.testFilesPrefix, testName)
        diffFilePath = '%s/%s_diff.sql' %  (PgDiffTest.testFilesPrefix, testName)

        arguments.addDefaults = addDefaults
        arguments.addTransaction = addTransaction
        arguments.ignoreFunctionWhitespace = ignoreFunctionWhitespace
        arguments.ignoreStartWith = ignoreStartWith

        PgDiff.create_diff(writer, arguments)

        expectedDiffSQL = open(diffFilePath,'r').read().strip()
        gotDiffSQL = str(writer).strip()
        diff = unified_diff(expectedDiffSQL.splitlines(1), gotDiffSQL.splitlines(1), fromfile='expectedSQL', tofile='gotSQL')

        if(expectedDiffSQL != gotDiffSQL):
        # if diff:
            # for line in diff:
            #     print(line)
            raise PgDiffTestFailedException(testName, diff)

        return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(usage='Usage: PgDiffTest.py <test_case> [...]|all ')

    parser.add_argument('test_case', nargs='+')

    # parser.add_argument('--debug', dest='debug', action='store_true', help="outputs debug
    # information as traceback etc. (default is not to output traceback)")

    arguments = parser.parse_args()

    test_cases = []
    if len(arguments.test_case) == 1 and arguments.test_case[0] == 'all':
        test_cases = PgDiffTest.testCases.values()
    else:
        for testName in arguments.test_case:
            try:
                test_cases.append(PgDiffTest.testCases[testName])
            except KeyError as e:
                raise Exception("Test case %s not found in cases list. "
                                "Please check test case name or add such case in PfDiffTest.testCases dict" % testName)

    failedTests = dict()
    successfully_passed_tests = 0
    for testCase in test_cases:
        try:
            PgDiffTest.run(testCase[0], testCase[1], testCase[2], testCase[3], testCase[4])
        except Exception as e:
                import sys, traceback
                failedTests[testCase[0]] = e
                print(traceback.print_exception(*sys.exc_info()))
        else:
            successfully_passed_tests += 1

    print('Passed tests: %s of %s' % (successfully_passed_tests, len(test_cases)))

    for testCase, exception in failedTests.items():
        print('[%s] %s' % (testCase, exception))

    exit(len(failedTests))
