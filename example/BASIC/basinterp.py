# This file provides the runtime support for running a basic program
# Assumes the program has been parsed using basparse.py

import sys
import math
import random


class BasicInterpreter:

    # Initialize the interpreter. prog is a dictionary
    # containing (line,statement) mappings
    def __init__(self, prog):
        self.prog = prog

        self.functions = {           # Built-in function table
            'SIN': lambda z: math.sin(self.eval(z)),
            'COS': lambda z: math.cos(self.eval(z)),
            'TAN': lambda z: math.tan(self.eval(z)),
            'ATN': lambda z: math.atan(self.eval(z)),
            'EXP': lambda z: math.exp(self.eval(z)),
            'ABS': lambda z: abs(self.eval(z)),
            'LOG': lambda z: math.log(self.eval(z)),
            'SQR': lambda z: math.sqrt(self.eval(z)),
            'INT': lambda z: int(self.eval(z)),
            'RND': lambda z: random.random()
        }

    # Collect all data statements
    def collect_data(self):
        self.data = []
        for lineno in self.stat:
            if self.prog[lineno][0] == 'DATA':
                self.data = self.data + self.prog[lineno][1]
        self.dc = 0                  # Initialize the data counter

    # Check for end statements
    def check_end(self):
        has_end = 0
        for lineno in self.stat:
            if self.prog[lineno][0] == 'END' and not has_end:
                has_end = lineno
        if not has_end:
            print("NO END INSTRUCTION")
            self.error = 1
            return
        if has_end != lineno:
            print("END IS NOT LAST")
            self.error = 1

    # Check loops
    def check_loops(self):
        for pc in range(len(self.stat)):
            lineno = self.stat[pc]
            loop_type = self.prog[lineno][0]
            if loop_type in {'FOR', 'WHILE'}:
                loop_inst = self.prog[lineno]
                condition = loop_inst[1]
                is_relop = len(condition) > 1
                is_for_loop = loop_type == 'FOR'
                loop_var = loop_inst[1] if is_for_loop else (condition[2][1][0] if is_relop else None)
                break_pc = 0
                for i in range(pc + 1, len(self.stat)):
                    statement = self.prog[self.stat[i]]
                    if statement[-1] == 'BREAK':
                        break_pc = i
                    if statement[0] == 'NEXT':
                        if is_for_loop or is_relop:
                            nextvar = statement[1]
                            if nextvar != loop_var:
                                continue
                        if break_pc:
                            self.loopend[break_pc] = i + 1
                        self.loopend[pc] = i
                        break
                else:
                    print("LOOP WITHOUT NEXT AT LINE %s" % self.stat[pc])
                    self.error = 1

    # Evaluate an expression
    def eval(self, expr):
        etype = expr[0]
        if etype == 'NUM':
            return expr[1]
        elif etype == 'GROUP':
            return self.eval(expr[1])
        elif etype == 'UNARY':
            if expr[1] == '-':
                return -self.eval(expr[2])
        elif etype == 'BINOP':
            if expr[1] == '+':
                return self.eval(expr[2]) + self.eval(expr[3])
            elif expr[1] == '-':
                return self.eval(expr[2]) - self.eval(expr[3])
            elif expr[1] == '*':
                return self.eval(expr[2]) * self.eval(expr[3])
            elif expr[1] == '/':
                return float(self.eval(expr[2])) / self.eval(expr[3])
            elif expr[1] == '^':
                return abs(self.eval(expr[2]))**self.eval(expr[3])
        elif etype == 'VAR':
            var, dim1, dim2 = expr[1]
            if not dim1 and not dim2:
                if var in self.vars:
                    return self.vars[var]
                elif var in self.lists:
                    return self.lists[var]
                else:
                    print("UNDEFINED VARIABLE %s AT LINE %s" %
                          (var, self.stat[self.pc]))
                    raise RuntimeError
            # May be a list lookup or a function evaluation
            if dim1 and not dim2:
                if var in self.functions:
                    # A function
                    return self.functions[var](dim1)
                else:
                    # A list evaluation
                    if var in self.lists:
                        dim1val = self.eval(dim1)
                        if dim1val < 1 or dim1val > len(self.lists[var]):
                            print("LIST INDEX OUT OF BOUNDS AT LINE %s" %
                                  self.stat[self.pc])
                            raise RuntimeError
                        return self.lists[var][dim1val - 1]
                    # A dict item evaluation
                    else:
                        key = dim1[1]
                        return self.vars[var][key]
            if dim1 and dim2:
                if var in self.tables:
                    dim1val = self.eval(dim1)
                    dim2val = self.eval(dim2)
                    if dim1val < 1 or dim1val > len(self.tables[var]) or dim2val < 1 or dim2val > len(self.tables[var][0]):
                        print("TABLE INDEX OUT OUT BOUNDS AT LINE %s" %
                              self.stat[self.pc])
                        raise RuntimeError
                    return self.tables[var][dim1val - 1][dim2val - 1]
            print("UNDEFINED VARIABLE %s AT LINE %s" %
                  (var, self.stat[self.pc]))
            raise RuntimeError
        elif etype == 'DICT':
            dict_list = expr[1]
            return {key: value[1] for key, value in dict_list}
        elif etype == 'STRING':
            return expr[1]
        elif etype == 'DICT_FUNC':
            var, _, _ = expr[1]
            dictionary = self.vars[var]
            func = expr[2]
            return list(dictionary.keys() if func == 'KEYS' else dictionary.values())

    # Evaluate a relational expression
    def releval(self, expr):
        etype = expr[1]
        lhs = self.eval(expr[2])
        rhs = self.eval(expr[3])
        if etype == '<':
            if lhs < rhs:
                return 1
            else:
                return 0

        elif etype == '<=':
            if lhs <= rhs:
                return 1
            else:
                return 0

        elif etype == '>':
            if lhs > rhs:
                return 1
            else:
                return 0

        elif etype == '>=':
            if lhs >= rhs:
                return 1
            else:
                return 0

        elif etype == '=':
            if lhs == rhs:
                return 1
            else:
                return 0

        elif etype == '<>':
            if lhs != rhs:
                return 1
            else:
                return 0

    # Assignment
    def assign(self, target, value):
        var, dim1, dim2 = target
        if not dim1 and not dim2:
            self.vars[var] = self.eval(value)
        elif dim1 and not dim2:
            # List assignment
            dim1val = self.eval(dim1)
            # Dictionary assignment
            if dim1[0] == 'STRING':
                self.vars[var][dim1[1]] = self.eval(value)
                return
            if not var in self.lists:
                self.lists[var] = [0] * 10

            if dim1val > len(self.lists[var]):
                print ("DIMENSION TOO LARGE AT LINE %s" % self.stat[self.pc])
                raise RuntimeError
            self.lists[var][dim1val - 1] = self.eval(value)
        elif dim1 and dim2:
            dim1val = self.eval(dim1)
            dim2val = self.eval(dim2)
            if not var in self.tables:
                temp = [0] * 10
                v = []
                for i in range(10):
                    v.append(temp[:])
                self.tables[var] = v
            # Variable already exists
            if dim1val > len(self.tables[var]) or dim2val > len(self.tables[var][0]):
                print("DIMENSION TOO LARGE AT LINE %s" % self.stat[self.pc])
                raise RuntimeError
            self.tables[var][dim1val - 1][dim2val - 1] = self.eval(value)

    # Change the current line number
    def goto(self, linenum):
        if not linenum in self.prog:
            print("UNDEFINED LINE NUMBER %d AT LINE %d" %
                  (linenum, self.stat[self.pc]))
            raise RuntimeError
        self.pc = self.stat.index(linenum)

    # Run it
    def run(self):
        self.vars = {}            # All variables
        self.lists = {}            # List variables
        self.tables = {}            # Tables
        self.loops = []            # Currently active loops
        self.loopend = {}            # Mapping saying where loops end
        self.gosub = None           # Gosub return point (if any)
        self.error = 0              # Indicates program error

        self.stat = list(self.prog)  # Ordered list of all line numbers
        self.stat.sort()
        self.pc = 0                  # Current program counter

        # Processing prior to running

        self.collect_data()          # Collect all of the data statements
        self.check_end()
        self.check_loops()

        if self.error:
            raise RuntimeError

        while 1:
            line = self.stat[self.pc]
            instr = self.prog[line]

            op = instr[0]

            # END and STOP statements
            if op == 'END' or op == 'STOP':
                break           # We're done

            # GOTO statement
            elif op == 'GOTO':
                newline = instr[1]
                self.goto(newline)
                continue

            # PRINT statement
            elif op == 'PRINT':
                plist = instr[1]
                out = ""
                for label, val in plist:
                    if out:
                        out += ' ' * (15 - (len(out) % 15))
                    out += label
                    if val:
                        if label:
                            out += " "
                        eval = self.eval(val)
                        out += str(eval)
                sys.stdout.write(out)
                end = instr[2]
                if not (end == ',' or end == ';'):
                    sys.stdout.write("\n")
                if end == ',':
                    sys.stdout.write(" " * (15 - (len(out) % 15)))
                if end == ';':
                    sys.stdout.write(" " * (3 - (len(out) % 3)))

            # LET statement
            elif op == 'LET':
                target = instr[1]
                value = instr[2]
                self.assign(target, value)

            # READ statement
            elif op == 'READ':
                for target in instr[1]:
                    if self.dc < len(self.data):
                        value = ('NUM', self.data[self.dc])
                        self.assign(target, value)
                        self.dc += 1
                    else:
                        # No more data.  Program ends
                        return
            elif op == 'IF':
                relop = instr[1]
                newline = instr[2]
                if self.releval(relop):
                    if newline == 'BREAK':
                        # Loop is done. Jump out the loop
                        self.pc = self.loopend[self.pc]
                        self.loops.pop()
                    elif newline == 'CONTINUE':
                        self.pc = self.loops[-1][0]
                    else:
                        self.goto(newline)
                    continue

            elif op == 'FOR':
                loopvar = instr[1]
                initval = instr[2]
                finval = instr[3]
                stepval = instr[4]

                # Check to see if this is a new loop
                if not self.loops or self.loops[-1][0] != self.pc:
                    # Looks like a new loop. Make the initial assignment
                    newvalue = initval
                    self.assign((loopvar, None, None), initval)
                    if not stepval:
                        stepval = ('NUM', 1)
                    stepval = self.eval(stepval)    # Evaluate step here
                    self.loops.append((self.pc, stepval))
                else:
                    # It's a repeat of the previous loop
                    # Update the value of the loop variable according to the
                    # step
                    stepval = ('NUM', self.loops[-1][1])
                    newvalue = (
                        'BINOP', '+', ('VAR', (loopvar, None, None)), stepval)

                if self.loops[-1][1] < 0:
                    relop = '>='
                else:
                    relop = '<='
                if not self.releval(('RELOP', relop, newvalue, finval)):
                    # Loop is done. Jump to the NEXT
                    self.pc = self.loopend[self.pc]
                    self.loops.pop()
                else:
                    self.assign((loopvar, None, None), newvalue)

            elif op == 'WHILE':
                condition = instr[1]
                if condition[0] == 'TRUE':
                    if not self.loops or self.loops[-1][0] != self.pc:
                        # Looks like a new loop. Make the initial assignment
                        self.loops.append((self.pc, None))
                    self.pc += 1
                    continue
                variable = condition[2]
                loopvar = variable[1][0]
                operation = condition[1]
                fin_val = condition[3]
                stepval = instr[2]
                increment = operation in {'<', '<='}

                # Check to see if this is a new loop
                if not self.loops or self.loops[-1][0] != self.pc:
                    # Looks like a new loop. Make the initial assignment
                    newvalue = ('NUM', self.vars[loopvar])
                    if not stepval:
                        stepval = ('NUM', 1 if increment else -1)
                    self.loops.append((self.pc, self.eval(stepval)))
                else:
                    # It's a repeat of the previous loop
                    # Update the value of the loop variable according to the
                    # step
                    stepval = ('NUM', self.loops[-1][1])
                    newvalue = ('BINOP', '+', ('VAR', (loopvar, None, None)), stepval)

                final_val = self.eval(fin_val) - self.eval(stepval)
                fin_val = ('NUM', final_val)
                if not self.releval(('RELOP', operation, variable, fin_val)):
                    # Loop is done. Jump to the NEXT
                    self.pc = self.loopend[self.pc]
                    self.loops.pop()
                else:
                    self.assign((loopvar, None, None), newvalue)

            elif op == 'NEXT':
                if not self.loops:
                    print("NEXT WITHOUT LOOP AT LINE %s" % line)
                    return

                if len(instr) == 1:
                    self.pc = self.loops[-1][0]
                    continue
                nextvar = instr[1]
                self.pc = self.loops[-1][0]
                loopinst = self.prog[self.stat[self.pc]]
                forvar = loopinst[1] if loopinst[0] == 'FOR' else loopinst[1][2][1][0]
                if nextvar != forvar:
                    print("NEXT DOESN'T MATCH LOOP AT LINE %s" % line)
                    return
                continue
            elif op == 'GOSUB':
                newline = instr[1]
                if self.gosub:
                    print("ALREADY IN A SUBROUTINE AT LINE %s" % line)
                    return
                self.gosub = self.stat[self.pc]
                self.goto(newline)
                continue

            elif op == 'RETURN':
                if not self.gosub:
                    print("RETURN WITHOUT A GOSUB AT LINE %s" % line)
                    return
                self.goto(self.gosub)
                self.gosub = None

            elif op == 'FUNC':
                fname = instr[1]
                pname = instr[2]
                expr = instr[3]

                def eval_func(pvalue, name=pname, self=self, expr=expr):
                    self.assign((pname, None, None), pvalue)
                    return self.eval(expr)
                self.functions[fname] = eval_func

            elif op == 'DIM':
                for vname, x, y in instr[1]:
                    if y == 0:
                        # Single dimension variable
                        self.lists[vname] = [0] * x
                    else:
                        # Double dimension variable
                        temp = [0] * y
                        v = []
                        for i in range(x):
                            v.append(temp[:])
                        self.tables[vname] = v
            elif op == 'OOP':
                command = instr[1]
                obj = command[1]
                func = command[2]
                dict_name = obj[0]
                if func == 'POP':
                    para = command[3]
                    self.vars[dict_name].pop(para)
                elif func == 'CLEAR':
                    self.vars[dict_name].clear()
                elif func == 'UPDATE':
                    obj_2 = command[3]
                    dict_name_2 = obj_2[0]
                    dict_2 = self.vars[dict_name_2]
                    self.vars[dict_name].update(dict_2)

            self.pc += 1

    # Utility functions for program listing
    def expr_str(self, expr):
        etype = expr[0]
        if etype == 'NUM':
            return str(expr[1])
        elif etype == 'GROUP':
            return "(%s)" % self.expr_str(expr[1])
        elif etype == 'UNARY':
            if expr[1] == '-':
                return "-" + str(expr[2])
        elif etype == 'BINOP':
            return "%s %s %s" % (self.expr_str(expr[2]), expr[1], self.expr_str(expr[3]))
        elif etype == 'VAR':
            return self.var_str(expr[1])

    def relexpr_str(self, expr):
        return "%s %s %s" % (self.expr_str(expr[2]), expr[1], self.expr_str(expr[3]))

    def var_str(self, var):
        varname, dim1, dim2 = var
        if not dim1 and not dim2:
            return varname
        if dim1 and not dim2:
            return "%s(%s)" % (varname, self.expr_str(dim1))
        return "%s(%s,%s)" % (varname, self.expr_str(dim1), self.expr_str(dim2))

    # Create a program listing
    def list(self):
        stat = list(self.prog)      # Ordered list of all line numbers
        stat.sort()
        for line in stat:
            instr = self.prog[line]
            op = instr[0]
            if op in ['END', 'STOP', 'RETURN']:
                print("%s %s" % (line, op))
                continue
            elif op == 'REM':
                print("%s %s" % (line, instr[1]))
            elif op == 'PRINT':
                _out = "%s %s " % (line, op)
                first = 1
                for p in instr[1]:
                    if not first:
                        _out += ", "
                    if p[0] and p[1]:
                        _out += '"%s"%s' % (p[0], self.expr_str(p[1]))
                    elif p[1]:
                        _out += self.expr_str(p[1])
                    else:
                        _out += '"%s"' % (p[0],)
                    first = 0
                if instr[2]:
                    _out += instr[2]
                print(_out)
            elif op == 'LET':
                print("%s LET %s = %s" %
                      (line, self.var_str(instr[1]), self.expr_str(instr[2])))
            elif op == 'READ':
                _out = "%s READ " % line
                first = 1
                for r in instr[1]:
                    if not first:
                        _out += ","
                    _out += self.var_str(r)
                    first = 0
                print(_out)
            elif op == 'IF':
                print("%s IF %s THEN %d" %
                      (line, self.relexpr_str(instr[1]), instr[2]))
            elif op == 'GOTO' or op == 'GOSUB':
                print("%s %s %s" % (line, op, instr[1]))
            elif op == 'FOR':
                _out = "%s FOR %s = %s TO %s" % (
                    line, instr[1], self.expr_str(instr[2]), self.expr_str(instr[3]))
                if instr[4]:
                    _out += " STEP %s" % (self.expr_str(instr[4]))
                print(_out)
            elif op == 'NEXT':
                print("%s NEXT %s" % (line, instr[1]))
            elif op == 'FUNC':
                print("%s DEF %s(%s) = %s" %
                      (line, instr[1], instr[2], self.expr_str(instr[3])))
            elif op == 'DIM':
                _out = "%s DIM " % line
                first = 1
                for vname, x, y in instr[1]:
                    if not first:
                        _out += ","
                    first = 0
                    if y == 0:
                        _out += "%s(%d)" % (vname, x)
                    else:
                        _out += "%s(%d,%d)" % (vname, x, y)

                print(_out)
            elif op == 'DATA':
                _out = "%s DATA " % line
                first = 1
                for v in instr[1]:
                    if not first:
                        _out += ","
                    first = 0
                    _out += v
                print(_out)

    # Erase the current program
    def new(self):
        self.prog = {}

    # Insert statements
    def add_statements(self, prog):
        for line, stat in prog.items():
            self.prog[line] = stat

    # Delete a statement
    def del_line(self, lineno):
        try:
            del self.prog[lineno]
        except KeyError:
            pass
