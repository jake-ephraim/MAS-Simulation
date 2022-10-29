import matplotlib
matplotlib.use('TkAgg')
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from multiprocessing import Process

lax1, lax2, lax3, lax4, lax5, lax6 = None, None, None, None, None, None
sax1, sax2, sax3, sax4, sax5, sax6 = None, None, None, None, None, None
stime = None

def animation_frame(i):
        lax1.set_ydata(sax1[:i])
        lax2.set_ydata(sax2[:i])
        lax3.set_ydata(sax3[:i])
        lax4.set_ydata(sax4[:i])
        lax5.set_ydata(sax5[:i])
        lax6.set_ydata(sax6[:i])
        t = stime[:i]
        lax1.set_xdata(t)
        lax2.set_xdata(t)
        lax3.set_xdata(t)
        lax4.set_xdata(t)
        lax5.set_xdata(t)
        lax6.set_xdata(t)

def plot_graph_(name, x = 100, resolution = 600, v = 1.05, v_padding = 1.2, c = 250, c_padding = 1.3, fault_v1 = 0.7, fault_c1 = 300, fault_v2 = 0.7, fault_c2 = 300, fault_v3 = 0.7, fault_c3 = 300, animation=True, fault_bar=False):

        t_start = int(0.2 * resolution)
        t_end = int(0.4 * resolution)
        cy_lim = c//2
        cy_lim = [-c, -cy_lim, 0, cy_lim, c]
        vy_lim = [-v, -fault_v1, 0, fault_v1, v]

        fault_v1 = v if c == fault_c1 else fault_v1
        fault_v2 = v if c == fault_c2 else fault_v2
        fault_v3 = v if c == fault_c3 else fault_v3
        
        fault_v1 = 0 if fault_c1 < 1 else fault_v1
        fault_v2 = 0 if fault_c2 < 1 else fault_v2
        fault_v3 = 0 if fault_c3 < 1 else fault_v3
        
        time = np.linspace(0, x, resolution)
        fig, (ax1, ax2) = plt.subplots(nrows=2)

        global lax1, lax2, lax3, lax4, lax5, lax6, sax1, sax2, sax3, sax4, sax5, sax6, stime
        sax1 = np.sin(time)*c 
        sax1[t_start:t_end] *= fault_c1/c
        lax1, *_ = ax1.plot(time[:1]/100,sax1[:1], label='phase 1')

        sax2 = np.sin(time - 2*(np.pi)/3)*c 
        sax2[t_start:t_end] *= fault_c2/c
        lax2, *_ = ax1.plot(time[:1]/100, sax2[:1], label='phase 2')

        sax3 = np.sin(time + 2*(np.pi)/3)*c
        sax3[t_start:t_end] *= fault_c3/c
        lax3, *_ = ax1.plot(time[:1]/100, sax3[:1], label='phase 3')
        # ax1.axhline(y=0, color='k')
        if fault_bar:
            ax1.axvline(x=0.198, color="red")
            ax1.axvline(x=0.402, color="red")
        ax1.legend(loc = 'lower right')
        ax1.set_ylim([-c*c_padding, c*c_padding])
        ax1.set_xlim([0, 1])
        ax1.set_ylabel("Current (A)")
        ax1.set_yticks(cy_lim)

        sax4 = np.sin(time)*v
        sax4[t_start:t_end] *= fault_v1/v
        lax4, *_ = ax2.plot(time[:1]/100, sax4[:1], label='phase 1')

        sax5 = np.sin(time - 2*(np.pi)/3)*v
        sax5[t_start:t_end] *= fault_v2/v
        lax5, *_ = ax2.plot(time[:1]/100, sax5[:1], label='phase 2')

        sax6 = np.sin(time + 2*(np.pi)/3)*v 
        sax6[t_start:t_end] *= fault_v3/v
        lax6, *_ = ax2.plot(time[:1]/100, sax6[:1], label='phase 3')
        # ax2.axhline(y=0, color='k')
        if fault_bar:
            ax2.axvline(x=0.198, color="red")
            ax2.axvline(x=0.402, color="red")
        stime = time/x
        ax2.legend(loc = 'lower right')
        ax2.set_ylim([-v*v_padding, v*v_padding])
        ax2.set_xlim([0, 1])
        ax2.set_ylabel("Voltage (pu)")
        ax2.set_yticks(vy_lim)

        plt.xlabel("time (s)")
        plt.suptitle(f"Bus {name} Fault Analysis")
        fig.canvas.manager.set_window_title("Plottings")
        if animation:
            anim = FuncAnimation(fig, func = animation_frame, frames=np.arange(0, resolution, 4), interval=100, repeat=False)
        else:
            animation_frame(resolution)
        plt.show()

if __name__ == "__main__":
    from os import name as _OS_Name_
    if _OS_Name_ == 'nt':
        from os import environ
        environ['KIVY_GL_BACKEND'] = 'angle_sdl2'
    from kivy import require
    require("2.1.0")
    from kivy.app import App
    from kivy.uix.screenmanager import ScreenManager
    from kivy.uix.relativelayout import RelativeLayout
    from kivy.lang import Builder 
    from kivy.clock import Clock
    from kivy.factory import Factory
    from threading import Thread
    from assets import *
    from mas_lib.agent import AgentCB, AgentB, AgentDG, AgentSource
    from parseconfig import MyParser

    _HOST = ""
    _PORT = 10001

    class SimulationArea(RelativeLayout):

        def __init__(self, **kw):
            super().__init__(**kw)
            self.app = App.get_running_app()
            self.broken = []
        
        def create_connect(self, _HOST=_HOST, _PORT=_PORT):
            self.source = AgentSource('SOURCE33V', _HOST, _PORT, broadcast_channel=self.comm_channel)
            self.dg = [
                AgentDG("DG1", _HOST, _PORT, non_blocking_callback=self._agent_state_callback),
                AgentDG("DG2", _HOST, _PORT, non_blocking_callback=self._agent_state_callback)
            ]
            self.cb = [
                AgentCB("CB1A", _HOST, _PORT, non_blocking_callback=self._agent_state_callback),
                AgentCB("CB1B", _HOST, _PORT, non_blocking_callback=self._agent_state_callback),
                AgentCB("CB2A", _HOST, _PORT, non_blocking_callback=self._agent_state_callback),
                AgentCB("CB2B", _HOST, _PORT, non_blocking_callback=self._agent_state_callback),
                AgentCB("CB3A", _HOST, _PORT, non_blocking_callback=self._agent_state_callback),
                AgentCB("CB4A", _HOST, _PORT, non_blocking_callback=self._agent_state_callback),
                AgentCB("CB4B", _HOST, _PORT, non_blocking_callback=self._agent_state_callback),
                AgentCB("CB5A", _HOST, _PORT, non_blocking_callback=self._agent_state_callback),
                AgentCB("CB6A", _HOST, _PORT, non_blocking_callback=self._agent_state_callback),
                AgentCB("CB7A", _HOST, _PORT, non_blocking_callback=self._agent_state_callback),
                AgentCB("CB7B", _HOST, _PORT, non_blocking_callback=self._agent_state_callback),
                AgentCB("CB8A", _HOST, _PORT, non_blocking_callback=self._agent_state_callback),
                AgentCB("CB9A", _HOST, _PORT, non_blocking_callback=self._agent_state_callback),
                AgentCB("CB9B", _HOST, _PORT, non_blocking_callback=self._agent_state_callback),
                AgentCB("CB10A", _HOST, _PORT, non_blocking_callback=self._agent_state_callback)
                ]
            self.b =[
                AgentB("B1", _HOST, _PORT, non_blocking_callback=self._agent_state_callback),
                AgentB("B2", _HOST, _PORT, non_blocking_callback=self._agent_state_callback),
                AgentB("B3", _HOST, _PORT, non_blocking_callback=self._agent_state_callback),
                AgentB("B4", _HOST, _PORT, non_blocking_callback=self._agent_state_callback),
                AgentB("B5", _HOST, _PORT, non_blocking_callback=self._agent_state_callback),
                AgentB("B6", _HOST, _PORT, non_blocking_callback=self._agent_state_callback),
                AgentB("B7", _HOST, _PORT, non_blocking_callback=self._agent_state_callback),
                AgentB("B8", _HOST, _PORT, non_blocking_callback=self._agent_state_callback),
                AgentB("B9", _HOST, _PORT, non_blocking_callback=self._agent_state_callback),
                AgentB("B10", _HOST, _PORT, non_blocking_callback=self._agent_state_callback)
            ]
        
        def _agent_state_callback(self, name, state):
            Clock.schedule_once(lambda x: self._set_agent_state(name, state))

        def _set_agent_state(self, name, state):
            obj = self.ids[name]
            if state == getattr(obj, "agent_attr"):
                return
            # print(obj,name,  state)
            setattr(obj, "agent_attr", state)
        
        def simulate_bus(self, bus_name, voltage):
            t = 2
            if len(bus_name) == 0 :
                m = Factory.Message()
                m.ids.msg.text = "Bus name cannot be empty!"
                m.open()
                Clock.schedule_once(lambda x: m.dismiss(), t)
                return
            if len(voltage) == 0:
                m = Factory.Message()
                m.ids.msg.text = "Voltage cannot be empty!"
                m.open()
                Clock.schedule_once(lambda x: m.dismiss(), t)
                return
            if MyParser.its_B(bus_name) == None:
                m = Factory.Message()
                m.ids.msg.text = "Name entered is not a valid bus name!"
                m.open()
                Clock.schedule_once(lambda x: m.dismiss(), t)
                return
            if not (voltage.isdigit() or voltage.isdecimal()):
                m = Factory.Message()
                m.ids.msg.text = "Volatage must be a number!"
                m.open()
                Clock.schedule_once(lambda x: m.dismiss(), t)
                return
            if bus_name in self.broken:
                m = Factory.Message()
                m.ids.msg.text = f"{bus_name} is already down!"
                m.open()
                Clock.schedule_once(lambda x: m.dismiss(), t)
                return
            Thread(name="simulate_bus", target=self._simulate_bus, args=[bus_name, voltage], daemon=True).start()
        
        def _simulate_bus(self, name, voltage):
            for bus in self.b:
                if bus.name == name:
                    bus.broken = True
                    bus.voltage = float(voltage)
        
        def refresh(self):
            self.broken = []
            Thread(name="simulation canvas refresh", target= self.source.reset_network, daemon=True).start()
        
        def comm_channel(self, name, state):
            console = self.app.root.ids.sexy_console
            Clock.schedule_once(lambda x: self._comm_channel(name, state, console))
        
        def _comm_channel(self, name, state, console):
            d = console.data[:]
            if len(d) > 100:
                d.pop(0)
            d.append({"text": f"{name}: {state}"})
            console.data = d
            

    class MASManager(ScreenManager):
        
        def change_screens(self, screen:str, host, port):
            try:
                self.ids.simulation_canvas.create_connect(host, int(port))
                self.current = screen
            except Exception as e:
                print(e)


    class MASApp(App):
        plotter = None
        def build(self):
            Builder.load_file("./kv_files/assets.kv")
            return Builder.load_file("./kv_files/mas.kv")
        
        def plot_graph(self, bus_name, normal_current, fault_current, phase_number, animation, fault_bar):
            if self.plotter and self.plotter.is_alive():
                self.plotter.kill()
            t = 2
            if not MyParser.its_B(bus_name):
                m = Factory.Message()
                m.ids.msg.text = "Name entered is not a valid bus name!"
                m.open()
                Clock.schedule_once(lambda x: m.dismiss(), t)
                return
            self.plotter = Process(name="plottings", target=plot_graph_, kwargs={
                                                                                "name": bus_name,
                                                                                "c": float(normal_current),
                                                                                "fault_c1": float(fault_current),
                                                                                "fault_c2": float(fault_current) if phase_number in ("2", "3") else float(normal_current),
                                                                                "fault_c3": float(fault_current) if phase_number == '3' else float(normal_current),
                                                                                "animation": animation,
                                                                                "fault_bar": fault_bar
                                                                                })
            self.plotter.start()
                
        def on_stop(self):
            if self.plotter:
                self.plotter.kill()
            return super().on_stop()

    MASApp().run()
