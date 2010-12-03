import random
import math
import webbrowser
import urllib


class Buffon:
  def __init__(self, *args):
    self.machines = args
    self.init()
  def init(self):
    pass
  def __call__(self):
    subMachines = tuple(m for m in self.machines)
    return self.go(*subMachines)()
  def toLatex(self):
    subMachines = tuple(m.toLatex() for m in self.machines)
    return r'\{%s\}' %(self.latex(*subMachines))
  def toExpr(self):
    subMachines = tuple(m.toExpr() for m in self.machines)
    return '(%s)' %(self.expr(*subMachines))

class flip(Buffon):
  def init(s): s.cpt = 0
  def toExpr(s): return '0.5'
  def toLatex(s): return r'\frac{1}{2}'
  def __call__(self):
    self.cpt += 1
    return random.randint(0,1)
flip = flip()

class ONE(Buffon):
  def toExpr(s): return '1.0'
  def toLatex(s): return '1'
  def __call__(s): return 1
ONE = ONE()
  
class ZERO(Buffon):
  def expr(s): return '0.0'
  def latex(s): return '0'
  def __call__(s): return 0
ZERO = ZERO()

class COND(Buffon):
  def expr(self, m1, m2, m3): return '%s*%s+(1-%s)*%s'%(m1,m2,m1,m3)
  def latex(s, m1, m2, m3): return r'%s*%s+(1-%s)*%s'%(m1,m2,m1,m3)
  def go(s, m1, m2, m3):
    return m1() and m2 or m3

class MUL(Buffon):
  def expr(self, m1, m2): return '%s*%s'%(m1, m2)
  def latex(s, m1, m2): return r'%s\ %s'%(m1, m2)
  def go(s, m1, m2):
    return COND(m1, m2, ZERO)

class f_or(Buffon):
  def expr(s, m1, m2): return '%s+%s-%s*%s'%(m1, m2, m1, m2)
  def latex(s, m1, m2): return r'%s+%s+%s\ %s'%(m1, m2, m1, m2)
  def go(s, m1, m2):
    return COND(m1, ONE, m2)

class ONE_MINUS(Buffon):
  def expr(s, m1): return '1-%s'%(m1)
  def latex(s, m1): return r'1-%s'%(m1)
  def go(s, m1):
    return COND(m1, ZERO, ONE)

class HALF_SUM(Buffon):
  def expr(s, m1, m2): return '(%s+%s)/2'%(m1, m2)
  def latex(s, m1, m2): return r'\frac{%s+%s}{2}'%(m1, m2)
  def go(s, m1, m2):
    return COND(flip, m1, m2)

class HALF(Buffon):
  def expr(s, m1): return '%s/2'%(m1)
  def latex(s, m1): return r'\frac{%s}{2}'%(m1)
  def go(s, m1):
    return MUL(flip, m1)

class THIRD(Buffon):
  def expr(s, m1): return '%s/3'%(m1)
  def latex(s, m1): return r'\frac{%s}{3}'%(m1)
  def go(s, m1):
    return COND(flip, ZERO, COND(flip, m1, s))

class TWO_THIRD(Buffon):
  def expr(s, m1): return '(2*%s)/3'%(m1)
  def latex(s, m1): return r'\frac{2\ %s}{3}'%(m1)
  def go(s, m1):
    return COND(flip, m1, COND(flip, ZERO, s))
  
class SQR(Buffon):
  def expr(s, m1): return 'math.pow(%s, 2)'%(m1)
  def latex(s, m1): return r'%s^2'%(m1)
  def go(s, m1):
    return MUL(m1, m1)

class CUBE(Buffon):
  def expr(s, m1): return 'math.pow(%s, 3)'%(m1)
  def latex(s, m1): return r'%s^3'%(m1)
  def go(s, m1):
    return MUL(m1, MUL(m1, m1))

class BAG(Buffon):
  def init(s): s.B = {}#[-1 for _ in xrange(50)]
  def geo_half(s, j=0): return j if flip() else s.geo_half(j+1)
  def go(s, m):
    idx = s.geo_half()
    if (s.B.get(idx) is None):
      s.B[idx] = ONE if flip() else ZERO
    val = s.B[idx]
    return MUL(val, m)

class EVENP(Buffon):
  def expr(s, m): return '1/(1+%s)'%(m)
  def latex(s, m): return r'\frac{1}{1+%s}'%(m)
  def go(s, m):
    return COND(m, COND(m, s, ZERO), ONE)
  
class LOG_INCR(Buffon):
  def expr(s, m): return 'math.log(1+%s)'%(m) 
  def latex(s, m): return r'log(1+%s)'%(m)
  def go(s, m):
    return MUL(m, EVENP(BAG(m)))

class ATAN(Buffon):
  def expr(s, m): return 'math.atan(%s)'%(m)
  def latex(s, m): return r'atan(%s)'%(m)
  def go(s, m):
    return MUL(m, EVENP(SQR(BAG(m))))

class MGL_PI_4(Buffon):
  def expr(s): return 'math.pi/4'
  def latex(s): return '\pi/4'
  def go(s):
    b = BAG(ONE)
    return COND(b, COND(b, COND(b, COND(b, s, ZERO), ZERO) , ONE), ONE) 
   
def run(machine, N=10000):
  expr = machine.toExpr()
  print 'Expression :', expr
  formula = urllib.quote(machine.toLatex())
  url = 'http://chart.apis.google.com/chart?cht=tx&chl='+formula
  webbrowser.open(url, 2)
  val = eval(expr)
  print 'Value:', val
  for id in xrange (5): 
    s = 0
    flipsCpt = []
    for _ in xrange(N):
      flip.cpt = 0
      s += machine()
      flipsCpt.append(flip.cpt)
    res = s / float(N)
    dev = (res / val - 1) * 100
    flipMean = sum(flipsCpt) / float(N)
    flipStd = math.sqrt(sum(math.pow((f-flipMean), 2) for f in flipsCpt)/float(N))
    print 'Simulation :', id
    print ' mean flips :', flipMean
    print '  min flips :', min(flipsCpt)
    print '  max flips :', max(flipsCpt)
    print '  std flips :', flipStd
    print '     result :', res
    print '       %dev :', dev
    if not abs(dev) <= 5:
      print "WARNING"
  return res

#machine = ONE_MINUS(HALF(ONE))
#machine = MUL(machine, HALF(ONE))
#machine = ONE_MINUS(machine)
#machine = SQR(machine)
#machine = THIRD(machine)
#machine = TWO_THIRD(machine)
#machine = HALF_SUM(machine, ONE)
#machine = CUBE(machine)
#run(machine, 10000)

PI_8 = HALF_SUM(ATAN(HALF(ONE)), ATAN(THIRD(ONE)))

run(PI_8, 5000)
run(LOG_INCR(flip), 5000)
run(MGL_PI_4(), 10000)
#run(EVENP(HALF(ONE)), 10000)
#run(ATAN(THIRD(ONE)), 5000)
#run(ATAN(HALF(ONE)), 5000)
#run(THIRD(ONE), 5000)

#run(machine, 5000)

