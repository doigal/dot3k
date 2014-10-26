import os, math, psutil, commands, time
from subprocess import *  
from dot3k.menu import MenuOption
import dot3k.backlight

def run_cmd(cmd):  
   p = Popen(cmd, shell=True, stdout=PIPE, stderr=STDOUT)  
   output = p.communicate()[0]  
   return output   
   
class GraphCPU(MenuOption):
  """
  A simple "plug-in" example, this gets the CPU load
  and draws it to the LCD when active
  """
  def __init__(self):
    self.cpu_samples = [0,0,0,0,0]
    self.last = self.millis()
    MenuOption.__init__(self)
  
  def redraw(self, menu):
    now = self.millis()
    if now - self.last < 1000:
      return false

    self.cpu_samples.append(psutil.cpu_percent())
    self.cpu_samples.pop(0)
    self.cpu_avg = sum(self.cpu_samples) / len(self.cpu_samples)

    menu.write_row(0, 'CPU Load')
    menu.write_row(1, str(self.cpu_avg) + '%')
    menu.write_row(2, '#' * int(16*(self.cpu_avg/100.0)))
    
    dot3k.backlight.set_graph(self.cpu_avg/100.0)

  def left(self):
    dot3k.backlight.set_graph(0)
    return False

class GraphTemp(MenuOption):
  """
  A simple "plug-in" example, this gets the Temperature
  and draws it to the LCD when active
  """
  def __init__(self):
    self.last = self.millis()
    MenuOption.__init__(self)

  def get_cpu_temp(self):
    tempFile = open( "/sys/class/thermal/thermal_zone0/temp" )
    cpu_temp = tempFile.read()
    tempFile.close()
    return float(cpu_temp)/1000

  def get_gpu_temp(self):
    gpu_temp = commands.getoutput( '/opt/vc/bin/vcgencmd measure_temp' ).replace( 'temp=', '' ).replace( '\'C', '' )
    return float(gpu_temp)

  def redraw(self, menu):
    now = self.millis()
    if now - self.last < 1000:
      return false
    
    menu.write_row(0,'Temperature')
    menu.write_row(1,'CPU:' + str(self.get_cpu_temp()))
    menu.write_row(2,'GPU:' + str(self.get_gpu_temp()))
    
class GraphNetIP(MenuOption):
  """
  Gets the IP of the raspberry and displays to the LCD
  """
  def __init__(self):
    self.last = self.millis()
    MenuOption.__init__(self)

  def get_ip_addr(self):
    show_wlan0 = "ifconfig wlan0 | grep inet | cut -d: -f2 | cut -d ' ' -f1"      
    show_eth0  = "ifconfig eth0 | grep inet | cut -d: -f2 | cut -d ' ' -f1"  
    
    ipaddr = run_cmd(show_eth0)
    
    if ipaddr == "":  
       ipaddr = run_cmd(show_wlan0) 
    
    return ipaddr
    
  def redraw(self, menu):
    now = self.millis()
    if now - self.last < 1000:
      return false
    
    menu.write_row(0,time.strftime('  %a %H:%M:%S  '))
    menu.write_row(1,'IP Address')
    menu.write_row(2, str(self.get_ip_addr())[:-1])    

class GraphNetTrans(MenuOption):
  """
  Gets the total transfered amount of the raspberry and displays to the LCD
  """
  def __init__(self):
    self.last = self.millis()
    MenuOption.__init__(self)

  def get_down(self):
    show_dl_raw = ""
    show_dl_hr = "ifconfig eth0 | grep bytes | cut -d')' -f1 | cut -d'(' -f2"
    hr_dl = run_cmd(show_dl_hr) 
    return hr_dl

  def get_up(self):
    show_ul_raw = ""
    show_ul_hr = "ifconfig eth0 | grep bytes | cut -d')' -f2 | cut -d'(' -f2"
    hr_ul = run_cmd(show_ul_hr) 
    return hr_ul

    
  def redraw(self, menu):
    now = self.millis()
    if now - self.last < 1000:
      return false
    
    menu.write_row(0,'ETH0 Transfers')
    menu.write_row(1,str('Dn:' + self.get_down())[:-1])
    menu.write_row(2,str('Up:' + self.get_up())[:-1])     


class GraphNetSpeed(MenuOption):
  """
  Gets the total transfered amount of the raspberry and displays to the LCD
  """
 
  def __init__(self):
    self.last = self.millis()
    self.last_update = 0
    self.raw_dlold = 0
    self.raw_ulold = 0
    MenuOption.__init__(self)

  def get_current_down(self):
    show_dl_raw = "ifconfig eth0 | grep bytes | cut -d':' -f2 | cut -d' ' -f1"
    raw_dl = run_cmd(show_dl_raw) 
    return raw_dl

  def get_current_up(self):
    show_ul_raw = "ifconfig eth0 | grep bytes | cut -d':' -f3 | cut -d' ' -f1"
    raw_ul = run_cmd(show_ul_raw) 
    return raw_ul
   
  def redraw(self, menu, force = False):
    now = self.millis()
 
    #if now - self.last < 1000:
    #  return false
 
    if self.millis() - self.last_update < 1000*1 and not force:
      return False

    tdelta = self.millis() - self.last_update
    self.last_update = self.millis()
 
    raw_dlnew = self.get_current_down()[:-1]
    raw_ulnew = self.get_current_up()[:-1]
    
    ddelta = int(raw_dlnew) - int(self.raw_dlold)
    udelta = int(raw_ulnew) - int(self.raw_ulold)
    
    dlspeed = round(float(ddelta) / float(tdelta),1)
    ulspeed = round(float(udelta) / float(tdelta),1)    
    
    menu.write_row(0,'ETH0 Speed')
    menu.write_row(1,str('Dn:'+ str(dlspeed) + 'kB/s'))
    menu.write_row(2,str('Up:'+ str(ulspeed) + 'kB/s'))
    
    self.raw_dlold = raw_dlnew
    self.raw_ulold = raw_ulnew
