#
# Drupy/helper.py
# Drupy Helpers
# 
# @package Drupy
# @file helper.py
# @module drupy.helper
# @author Brendon Crawford
# @see http://drupy.sourceforge.net
# @created 2008-02-27
# @version 0.1.1
# @modified 2008-08-20
#
#

def get_import(filename):
  name = filename.replace('/', '.')
  mod = __import__(name)
  components = name.split('.')
  for comp in components[1:]:
      mod = getattr(mod, comp)
  return mod



#
# Reference class
#
class Reference:
  def __init__(self):
    self.val = None
  #
  # Enforces a reference
  # @param Object data
  # @raise Exception 
  # @return Bool
  #
  @staticmethod
  def check(data):
    if not isinstance(data, Reference) or not hasattr(data, 'val'):
      raise Exception, "Argument must be an object and must contain a 'val' property."
    else:
      return True
