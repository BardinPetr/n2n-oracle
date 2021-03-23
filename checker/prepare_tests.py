import os
import argparse
import shutil

ORIGIN_TESTS_DIR = 'origin_tests'
TESTS_DIR = 'tests'

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('run_only', nargs='*')
    parser.add_argument('--keep_dependencies', action='store_true')
    args = parser.parse_args()
    run_only, keep_dependencies = args.run_only, args.keep_dependencies

    shutil.rmtree(TESTS_DIR)
    os.mkdir(TESTS_DIR)

    if not run_only:
        run_only = [str(x) for x in range(1, 22)]

    run_only = set(map(lambda x: f"test_US-{x.rjust(3, '0')}.py", run_only))

    for test in os.listdir(ORIGIN_TESTS_DIR):
        if os.path.isfile(os.path.join(ORIGIN_TESTS_DIR, test)):
            if not test.startswith('test_'):
                shutil.copy(os.path.join(ORIGIN_TESTS_DIR, test), os.path.join(TESTS_DIR, test))
            elif test in run_only:
                if not keep_dependencies:
                    with open(os.path.join(TESTS_DIR, test), 'w') as out:
                        with open(os.path.join(ORIGIN_TESTS_DIR, test)) as inp:
                            out.writelines(
                                filter(lambda x: not x.startswith('@pytest.mark.dependency'), inp.readlines()))
                else:
                    shutil.copy(os.path.join(ORIGIN_TESTS_DIR, test), os.path.join(TESTS_DIR, test))

    print(os.listdir(TESTS_DIR))
