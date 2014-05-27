# What is this?
__Anubis__ is a virtual heater simulator. During a class project at AGH (http://agh.edu.pl/) I had the _pleasure_ of doing a project in programming a radiometer heater.

Sadly, it's expensive equiment, and I can't take it home like an Arduino. Therefore, Anubis was written and used to help with this project. What it does, is it impersonates a heater by serial port, undertands commands and models a heater using simple thermodynamics.

If you ever come across helping with that heater - be welcome to use Anubis.

Anubis requires Python 2.5+ and pySerial.

# How to?

First, install a software that creates two serial ports connected with a virtual cable (eg. com0com or Advanced Virtual COM Port). One of these will be used for controller (eg. LabView), and the other will be used by Anubis. Therefore, Anubis will impersonate a heater!

Then, just start Anubis, pass it the second port identifer, and watch it fly!