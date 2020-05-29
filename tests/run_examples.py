#!/usr/bin/python3

"""
    Copyright Kristjan Kongas 2020

    Boost Software License - Version 1.0 - August 17th, 2003

    Permission is hereby granted, free of charge, to any person or organization
    obtaining a copy of the software and accompanying documentation covered by
    this license (the "Software") to use, reproduce, display, distribute,
    execute, and transmit the Software, and to prepare derivative works of the
    Software, and to permit third-parties to whom the Software is furnished to
    do so, all subject to the following:

    The copyright notices in the Software and this entire statement, including
    the above license grant, this restriction and the following disclaimer,
    must be included in all copies of the Software, in whole or in part, and
    all derivative works of the Software, unless such copies or derivative
    works are solely in the form of machine-executable object code generated by
    a source language processor.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE, TITLE AND NON-INFRINGEMENT. IN NO EVENT
    SHALL THE COPYRIGHT HOLDERS OR ANYONE DISTRIBUTING THE SOFTWARE BE LIABLE
    FOR ANY DAMAGES OR OTHER LIABILITY, WHETHER IN CONTRACT, TORT OR OTHERWISE,
    ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
    DEALINGS IN THE SOFTWARE.
"""

import os, subprocess
from pathlib import Path

fire_failure_code = 1

class assert_runner:
    test_count = 0
    check_count = 0

    def __init__(self, pth):
        self.pth = pth
        assert_runner.test_count += 1

    def equal(self, cmd, out):
        result = subprocess.run([self.pth] + cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        assert result.returncode == 0
        assert self.b2str(result.stdout.strip()) == out.strip()
        assert result.stderr == b""
        assert_runner.check_count += 1

    def handled_failure(self, cmd):
        result = subprocess.run([self.pth] + cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        assert result.returncode == fire_failure_code
        assert result.stdout == b""
        assert result.stderr != b""
        assert_runner.check_count += 1

    def help_success(self, cmd):
        result = subprocess.run([self.pth] + cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        assert result.returncode == 0
        assert_runner.check_count += 1

    def b2str(self, b):
        return str(b, "utf-8")


def run_all_combinations(pth_prefix):
    runner = assert_runner(pth_prefix + "all_combinations")

    runner.help_success("-h")


def run_basic(pth_prefix):
    runner = assert_runner(pth_prefix + "basic")

    runner.equal("-x 3 -y 4", "3 + 4 = 7")
    runner.equal("-x -3 -y 3", "-3 + 3 = 0")
    runner.equal("-x=-3 -y=3", "-3 + 3 = 0")
    runner.handled_failure("")
    runner.handled_failure("-x 3")
    runner.handled_failure("-y 4")
    runner.handled_failure("-x test")
    runner.handled_failure("-x")
    runner.handled_failure("--undefined 0")
    runner.help_success("-h")
    runner.help_success("--help")
    runner.help_success("-x 0 -h")
    runner.help_success("-h --undefined")


def run_flag(pth_prefix):
    runner = assert_runner(pth_prefix + "flag")

    runner.help_success("-h")
    runner.equal("", "0 0")
    runner.equal("-a -b", "1 1")
    runner.handled_failure("-a 1")


def run_optional_and_default(pth_prefix):
    runner = assert_runner(pth_prefix + "optional_and_default")

    runner.help_success("-h")
    runner.equal("", "false false")
    runner.equal("--default 1", "false true")
    runner.equal("--optional 1", "true false")
    runner.equal("--optional 1 --default 1", "true true")


def run_positional(pth_prefix):
    runner = assert_runner(pth_prefix + "positional")

    runner.help_success("-h")
    runner.handled_failure("")
    runner.handled_failure("test")
    runner.equal("2", "2 0")
    runner.equal("2 3", "2 3")
    runner.handled_failure("2 3 4")
    runner.equal("-1 -3", "-1 -3")


def run_vector_positional(pth_prefix):
    runner = assert_runner(pth_prefix + "vector_positional")

    runner.help_success("-h")
    runner.equal("", "\n")
    runner.equal("b a", "b a\n")
    runner.equal("b a -o", "b\na\n")
    runner.equal("b a -s", "a b\n")
    runner.equal("b a -os", "a\nb\n")


def main():
    pth_prefix = str(Path(__file__).absolute().parent.parent / "examples") + "/"

    print("Running tests in {} ...".format(pth_prefix), end="")

    run_all_combinations(pth_prefix)
    run_basic(pth_prefix)
    run_flag(pth_prefix)
    run_optional_and_default(pth_prefix)
    run_positional(pth_prefix)
    run_vector_positional(pth_prefix)

    print(" SUCCESS! (ran {} tests with {} checks)".format(assert_runner.test_count, assert_runner.check_count))


if __name__ == "__main__":
    main()
