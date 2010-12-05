import math
import webbrowser
import urllib
import random

class RandomBitFlow:
  def __init__(self):
    self.buffer = []
  def fillBuffer(self):
    raise NotImplementedError()
  def __call__(self):
    if not self.buffer:
      self.fillBuffer()
    bit = self.buffer.pop()
    return bit

class Ramdom_atmospheric(RandomBitFlow):
  def fillBuffer(self):
    url = "http://www.random.org/integers/?num=1000&min=0&max=1&col=1&base=2&format=plain&rnd=new"
    for bit in urllib.urlopen(url).read().split():
      self.buffer.append(int(bit))
Random_atmospheric = Ramdom_atmospheric()

class Random_atomic(RandomBitFlow):
    def fillBuffer(self):
      url = "http://www.fourmilab.ch/cgi-bin/uncgi/Hotbits?nbytes=1024&fmt=bin"
      s = urllib.urlopen(url).read()
      self.buffer = list(int(ord(c) & (1 << i) > 0) for c in s for i in xrange(8))
Random_atomic = Random_atomic()

def Random_python():
  return random.randint(0,1)
  
randomBit = Random_atomic

class Buffon:
  allMachines = []
  def __init__(self, *args):
    self.machines = args
    self.vars = None
    self.cpt = 0
    if self.__class__ not in Buffon.allMachines:
      self.__class__.CPT = 0
      Buffon.allMachines.append(self.__class__)
    self.init()
  def reset(self):
    self.init()
    for m in self.machines:
      m.reset()
    if 'core' in self.__dict__:
      self.core(*self.machines).reset()
  def init(self):
    pass
  def __call__(self):
    self.__class__.CPT += 1
    self.cpt += 1
    return self.call()
  def call(self):
    return self.core(*self.machines)()
  def toLatex(self):
    subMachines = tuple(m.toLatex() for m in self.machines)
    return r'\{%s\}' %(self.latex(*subMachines))
  def toExpr(self):
    subMachines = tuple(m.toExpr() for m in self.machines)
    return '(%s)' %(self.expr(*subMachines))

class FLIP(Buffon):
  def toExpr(s): return '0.5'
  def toLatex(s): return r'\frac{1}{2}'
  def call(self):
    return randomBit()
FLIP = FLIP()

class ONE(Buffon):
  def toExpr(s): return '1.0'
  def toLatex(s): return '1'
  def call(s): return 1
ONE = ONE()

class ZERO(Buffon):
  def expr(s): return '0.0'
  def latex(s): return '0'
  def call(s): return 0
ZERO = ZERO()

class COND(Buffon):
  def expr(self, m1, m2, m3): return '%s*%s+(1-%s)*%s'%(m1,m2,m1,m3)
  def latex(s, m1, m2, m3): return r'%s*%s+(1-%s)*%s'%(m1,m2,m1,m3)
  def core(s, m1, m2, m3):
    return m2 if m1() else m3

class MUL(Buffon):
  def expr(self, m1, m2): return '%s*%s'%(m1, m2)
  def latex(s, m1, m2): return r'%s\ %s'%(m1, m2)
  def core(s, m1, m2):
    return COND(m1, m2, ZERO)

class f_or(Buffon):
  def expr(s, m1, m2): return '%s+%s-%s*%s'%(m1, m2, m1, m2)
  def latex(s, m1, m2): return r'%s+%s+%s\ %s'%(m1, m2, m1, m2)
  def core(s, m1, m2):
    return COND(m1, ONE, m2)

class ONE_MINUS(Buffon):
  def expr(s, m1): return '1-%s'%(m1)
  def latex(s, m1): return r'1-%s'%(m1)
  def core(s, m1):
    return COND(m1, ZERO, ONE)

class HALF_SUM(Buffon):
  def expr(s, m1, m2): return '(%s+%s)/2'%(m1, m2)
  def latex(s, m1, m2): return r'\frac{%s+%s}{2}'%(m1, m2)
  def core(s, m1, m2):
    return COND(FLIP(), m1, m2)

class HALF(Buffon):
  def expr(s, m1): return '%s/2'%(m1)
  def latex(s, m1): return r'\frac{%s}{2}'%(m1)
  def core(s, m1):
    return MUL(FLIP, m1)

class THIRD(Buffon):
  def expr(s, m1): return '%s/3'%(m1)
  def latex(s, m1): return r'\frac{%s}{3}'%(m1)
  def core(s, m1):
    return COND(FLIP, ZERO, COND(FLIP, m1, s))

class TWO_THIRD(Buffon):
  def expr(s, m1): return '(2*%s)/3'%(m1)
  def latex(s, m1): return r'\frac{2\ %s}{3}'%(m1)
  def core(s, m1):
    return COND(FLIP, m1, COND(FLIP, ZERO, s))
  
class SQR(Buffon):
  def expr(s, m1): return 'math.pow(%s, 2)'%(m1)
  def latex(s, m1): return r'%s^2'%(m1)
  def core(s, m1):
    return MUL(m1, m1)

class CUBE(Buffon):
  def expr(s, m1): return 'math.pow(%s, 3)'%(m1)
  def latex(s, m1): return r'%s^3'%(m1)
  def core(s, m1):
    return MUL(m1, MUL(m1, m1))

class BAG(Buffon):
  def init(s): s.B = {}#[-1 for _ in xrange(50)]
  def geo_half(s, j=0):
    j = 0
    while 1:
      if randomBit():
        return j
      j += 1
  def __str__(s):
    #print s.B
    return "".join(str(s.B.get(i, '_')) for i in xrange(32))
  def call(s):
    idx = s.geo_half()
    if (s.B.get(idx) is None):
      f = randomBit()
      s.B[idx] = f
      #print "=>", idx, f, s
    return s.B[idx]

class EVENP(Buffon):
  def expr(s, m): return '1/(1+%s)'%(m)
  def latex(s, m): return r'\frac{1}{1+%s}'%(m)
  def core(s, m):
    return COND(m, COND(m, s, ZERO), ONE)
  
class LOG_INCR(Buffon):
  def expr(s, m): return 'math.log(1+%s)'%(m) 
  def latex(s, m): return r'log(1+%s)'%(m)
  def core(s, m):
    return MUL(m, EVENP(BAG(m)))

class ATAN(Buffon):
  def expr(s, m): return 'math.atan(%s)'%(m)
  def latex(s, m): return r'atan(%s)'%(m)
  def core(s, m):
    return MUL(m, EVENP(SQR(MUL(BAG(), m))))

class MGL_PI_4(Buffon):
  def init(s): s.b = BAG()
  def expr(s): return 'math.pi/4'
  def latex(s): return '\pi/4'
  def call(s):
    #print 'hit', s.b
    b = BAG()
    print '***'
    while 1:
      print s.b
      if s.b() == 0: return 1
      if s.b() == 0: return 1
      if s.b() == 0: return 0
      if s.b() == 0: return 0
    #return COND(s.b, COND(s.b, COND(s.b, COND(s.b, s, ZERO), ZERO) , ONE), ONE) 

def stats(name, lst):
  N = float(len(lst))
  lstMean = sum(lst) / N
  lstStd = math.sqrt(sum(math.pow((f-lstMean), 2) for f in lst)/N)
  print '  min', name, ':', min(lst)
  print ' mean', name, ':', lstMean
  print '  max', name, ':', max(lst)
  print '  std', name, ':', lstStd
  
   
def run(machine, N=10000, S=5):
  expr = machine.toExpr()
  print 'Expression :', expr
  #formula = urllib.quote(machine.toLatex())
  #url = 'http://chart.apis.google.com/chart?cht=tx&chl='+formula
  #webbrowser.open(url, 2)
  val = eval(expr)
  print 'Value:', val
  for id in xrange(S): 
    s = 0
    flipsCpt = []
    condsCpt = []
    N2 = 0
    for _ in xrange(N):
      #COND.CPT = 0
      #FLIP.CPT = 0
      machine.reset()
      try:
        s += machine()
        N2 += 1
      except:
        pass
      #print '-----------'
      #flipsCpt.append(FLIP.CPT)
      #condsCpt.append(COND.CPT)
    res = s / float(N2)
    dev = (res / val - 1) * 100
    print 'Simulation :', id
    print '     result :', res
    print '       %dev :', dev
    #stats('flips', flipsCpt)
    #stats('conds', condsCpt)
    if not abs(dev) <= 5:
      print "WARNING"
  return res

machine = ONE_MINUS(HALF(ONE))

#machine = MUL(machine, HALF(ONE))
#machine = ONE_MINUS(machine)
#machine = SQR(machine)
#machine = THIRD(machine)
#machine = TWO_THIRD(machine)
#machine = HALF_SUM(machine, ONE)
#machine = CUBE(machine)
run(machine, 1, 1)

PI_8 = HALF_SUM(ATAN(HALF(ONE)), ATAN(THIRD(ONE)))

run(MGL_PI_4(), 1000, 1)
#run(PI_8, 5000)
#run(LOG_INCR(flip), 5000)
#run(EVENP(HALF(ONE)), 10000)
#run(ATAN(THIRD(ONE)), 5000)
#run(ATAN(HALF(ONE)), 5000)
#run(THIRD(ONE), 5000)

#run(machine, 5000)

