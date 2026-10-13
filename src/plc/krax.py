
from pyplc.platform import plc,hw
from pyplc.utils.logging import logger
from pyplc.pou import POU,IN_INT
from pyplc.utils.misc import BLINK as Aerator,TOF
from project import name as project_name,version as project_version
from typing import Tuple
from concrete import Factory,Mixer,Motor,Weight,Dosator,Container,Manager,Readiness,Loaded,Lock
from concrete.msgate import MPGate
from concrete.dosator import ManualDosator
from concrete.transport import Transport,DROT
from concrete.vibrator import Vibrator,UnloadHelper
from concrete.container import Assembly2
import sys
import gc

logger.info(f'Запуск проекта {project_name} {project_version}')

#VSCode autocompleter блок.
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from collections import namedtuple
    HW = namedtuple('HW', ['FILLERS_M_1', 'MCONTAINER_M_1', 'PRESSURE_1', 'CEMENT_M_1', 'WATER_M_1', 'ADDITIONS_M_1', 'ADDITIONS_M_2', 'MIXER_I_1', 'FILLER_CLOSED_1', 'FILLER_CLOSED_2', 'FILLER_CLOSED_3', 'FILLER_CLOSED_4', 'FILLER_CLOSED_5', 'FILLER_CLOSED_6', 'ROPE_CONVEYOR_1', 'CONVEYOR_ROTATING_1', 'ROPE_TCONVEYOR_1', 'TCONVEYOR_ROTATING_1', 'MCONTAINER_CLOSED_1', 'AUGER_ISON_1', 'HLEVEL_SILAGE_1', 'LLEVEL_SILAGE_1', 'DCEMENT_CLOSED_1', 'WATER_CLOSED_1', 'WPUMP_OUT_ISON_1', 'DWATER_CLOSED_1', 'ADDITION_CLOSED_1', 'ADDITION_CLOSED_2', 'DADDITIONS_CLOSED_1', 'ADDITION_CLOSED_3', 'ADDITION_CLOSED_4', 'DADDITIONS_CLOSED_2', 'MIXER_ISON_1', 'MIXER_ADOOR_CLOSED_1', 'MIXER_OPENED_1', 'MIXER_MIDDLE_1', 'MIXER_CLOSED_1', 'CONV_POWER_OK_1', 'C_POWER_OK_1', 'P_POWER_OK_1', 'M_POWER_OK_1', 'A_POWER_OK_1', 'PHASE_OK_1', 'INPUT_OK_1', 'EMERGENCY_1', 'MAN_AUGER_ON_1', 'MAN_DISABLE_1', 'MAN_MIXER_ON_1', 'MAN_MIXER_OFF_1',
                    'MAN_MIXER_OPEN_1', 'MAN_MIXER_CLOSE_1', 'MAN_WATER_OPEN_1', 'AUGER_ISON_2', 'FILLER_OPEN_1', 'VIBRATOR_ON_1', 'FILLER_OPEN_2', 'VIBRATOR_ON_2', 'FILLER_OPEN_3', 'VIBRATOR_ON_3', 'FILLER_OPEN_4', 'VIBRATOR_ON_4', 'FILLER_OPEN_5', 'VIBRATOR_ON_5', 'FILLER_OPEN_6', 'VIBRATOR_ON_6', 'CONVEYOR_ON_1', 'CONVEYOR_OFF_1', 'DF_VIBRATOR_ON_1', 'TCONVEYOR_ON_1', 'TCONVEYOR_OFF_1', 'T_VIBRATOR_ON_1', 'T_VIBRATOR_ON_2', 'MCONTAINER_OPEN_1', 'MC_VIBRATOR_ON_1', 'FILTER_ON_1', 'AERATOR_ON_1', 'AUGER_ON_1', 'WPUMP_ON_1', 'WPUMP_OUT_ON_1', 'APUMP_ON_1', 'APUMP_ON_2', 'APUMP_ON_3', 'APUMP_ON_4', 'MIXER_ON_1', 'MIXER_OFF_1', 'MIXER_OPEN_1', 'MIXER_CLOSE_1', 'BELL_ON_1', 'MANUAL_ON_1', 'DCEMENT_OPEN_1', 'WATER_OPEN_1', 'DWATER_OPEN_1', 'ADDITION_OPEN_1', 'ADDITION_OPEN_2', 'DADDITIONS_OPEN_1', 'ADDITION_OPEN_3', 'ADDITION_OPEN_4', 'DADDITIONS_OPEN_2', 'AUGER_ON_2', 'AERATOR_ON_2', 'DC_VIBRATOR_ON_1'], defaults=[])
    hw = HW()

class MCLevel(POU):
    zero = POU.var(int(0),persistent=True)  #точка где можно считать пусто
    empty= POU.var(bool(False))                         #установить точку пусто
    raw  = POU.input(int(0))                            #с датчика веса
    level= POU.var(bool(False))                         #уровень
    def __init__(self, *_, raw: IN_INT, id: str | None = None, parent: POU | None = None):
        super().__init__(*_, id=id, parent=parent)
        self.raw = raw
        self.level = False
        self._lempty = False
    def __call__(self):
        with self:
            if self.raw>self.zero: 
                self.level = True
            if self.raw<=self.zero:
                self.level = False
            if self.empty and not self._lempty:
                self.zero = self.raw + 500
            self._lempty = self.empty

mclevel_1 = MCLevel(raw=hw.MCONTAINER_M_1)

factory_1 = Factory()

cement_m_1 = Weight(raw=hw.CEMENT_M_1,mmax=1500)
silage_1 = Container(m = cement_m_1.get_m , out=hw.AUGER_ON_1,closed=~hw.AUGER_ON_1,lock=Lock(key=lambda: hw.DCEMENT_CLOSED_1 or hw.AUGER_ON_2) )
silage_2 = Container(m = cement_m_1.get_m ,out=hw.AUGER_ON_2,closed=~hw.AUGER_ON_2,lock=Lock(key=lambda: hw.DCEMENT_CLOSED_1 or hw.AUGER_ON_1) )
dcement_1 = Dosator(m = cement_m_1.get_m, out = hw.DCEMENT_OPEN_1,closed=~hw.DCEMENT_CLOSED_1, containers=(silage_1,silage_2),lock=Lock(key=lambda: hw.AUGER_ON_1 or hw.AUGER_ON_2 or not hw.MIXER_ISON_1))
dc_vibrator_1 = UnloadHelper(q=hw.DC_VIBRATOR_ON_1,dosator=dcement_1,weight=cement_m_1,point=20, dr=3000)
aerator_1 = Aerator(enable=hw.AUGER_ON_1,q = hw.AERATOR_ON_1)
from pyplc.ld import LD     #pyplc>=0.5.2 с новым LD
from pyplc.attribute import AnyAttribute
AERATOR_EN_2 = AnyAttribute( False )
aerator_2 = Aerator(enable=hw.AUGER_ON_2,q = LD.entry().no(AERATOR_EN_2).mov(hw.AERATOR_ON_2).fe(AERATOR_EN_2).rst(hw.AERATOR_ON_2).end())

water_m_1 = Weight(raw=hw.WATER_M_1,mmax=500)
water_1 = Container(m = water_m_1.get_m, out=hw.WATER_OPEN_1,closed=~hw.WATER_CLOSED_1,lock=Lock(key=hw.DWATER_CLOSED_1))
dwater_1 = Dosator(m = water_m_1.get_m, out = hw.DWATER_OPEN_1,closed=~hw.DWATER_CLOSED_1, containers=(water_1,),lock=Lock(key=lambda: hw.WATER_OPEN_1 or hw.WATER_CLOSED_1))
wpump_1 = TOF(clk=hw.WATER_OPEN_1,q=hw.WPUMP_ON_1)
wpump_out_1 = TOF(clk=hw.DWATER_OPEN_1,q=hw.WPUMP_OUT_ON_1)

additions_m_1 = Weight(raw=hw.ADDITIONS_M_1,mmax=50)
addition_1 = Container(m = additions_m_1.get_m, out=hw.ADDITION_OPEN_1,closed=~hw.ADDITION_CLOSED_1,lock=Lock(key=lambda: not hw.DADDITIONS_CLOSED_1 or hw.ADDITION_CLOSED_2))
addition_2 = Container(m = additions_m_1.get_m, out=hw.ADDITION_OPEN_2,closed=~hw.ADDITION_CLOSED_2,lock=Lock(key=lambda: not hw.DADDITIONS_CLOSED_1 or hw.ADDITION_CLOSED_1))
dadditions_1 = Dosator(m = additions_m_1.get_m, out = hw.DADDITIONS_OPEN_1,closed=hw.DADDITIONS_CLOSED_1, containers=(addition_1,addition_2),lock=Lock(key=lambda: hw.ADDITION_CLOSED_1 or hw.ADDITION_CLOSED_2))
apump_1 = TOF(clk=hw.ADDITION_OPEN_1,q=hw.APUMP_ON_1)
apump_2 = TOF(clk=hw.ADDITION_OPEN_2,q=hw.APUMP_ON_2)

additions_m_2 = Weight(raw=hw.ADDITIONS_M_2,mmax=50)
addition_3 = Container(m = additions_m_2.get_m, out=hw.ADDITION_OPEN_3,closed=~hw.ADDITION_CLOSED_3,lock=Lock(key=lambda: not hw.DADDITIONS_CLOSED_2 or hw.ADDITION_CLOSED_4))
addition_4 = Container(m = additions_m_2.get_m, out=hw.ADDITION_OPEN_4,closed=~hw.ADDITION_CLOSED_4,lock=Lock(key=lambda: not hw.DADDITIONS_CLOSED_2 or hw.ADDITION_CLOSED_3))
dadditions_2 = Dosator(m = additions_m_2.get_m, out = hw.DADDITIONS_OPEN_2,closed=hw.DADDITIONS_CLOSED_2, containers=(addition_3,addition_4),lock=Lock(key=lambda: hw.ADDITION_CLOSED_3 or hw.ADDITION_CLOSED_4))
apump_3 = TOF(clk=hw.ADDITION_OPEN_3,q=hw.APUMP_ON_3)
apump_4 = TOF(clk=hw.ADDITION_OPEN_4,q=hw.APUMP_ON_4)

fillers_m_1 = Weight(raw=hw.FILLERS_M_1,mmax=6000)

adapter_1 = Assembly2(outs=(hw.FILLER_OPEN_1,hw.FILLER_OPEN_2),sts=(hw.FILLER_CLOSED_1,hw.FILLER_CLOSED_2) )
adapter_2 = Assembly2(outs=(hw.FILLER_OPEN_3,hw.FILLER_OPEN_4),sts=(hw.FILLER_CLOSED_3,hw.FILLER_CLOSED_4) )
adapter_3 = Assembly2(outs=(hw.FILLER_OPEN_5,hw.FILLER_OPEN_6),sts=(hw.FILLER_CLOSED_5,hw.FILLER_CLOSED_6) )

filler_1 = Container(m = fillers_m_1.get_m, out=adapter_1.out,closed=adapter_1.closed,lock=Lock(key=lambda: not adapter_2.closed() or not adapter_3.closed() ))
filler_2 = Container(m = fillers_m_1.get_m, out=adapter_2.out,closed=adapter_2.closed,lock=Lock(key=lambda: not adapter_1.closed() or not adapter_3.closed()))
filler_3 = Container(m = fillers_m_1.get_m, out=adapter_3.out,closed=adapter_3.closed,lock=Lock(key=lambda: not adapter_2.closed() or not adapter_1.closed()))

vibrator_1 = Vibrator( q = hw.VIBRATOR_ON_1,containers=[hw.FILLER_OPEN_1],weight = fillers_m_1 )
vibrator_2 = Vibrator( q = hw.VIBRATOR_ON_2,containers=[hw.FILLER_OPEN_2],weight = fillers_m_1 )
vibrator_3 = Vibrator( q = hw.VIBRATOR_ON_3,containers=[hw.FILLER_OPEN_3],weight = fillers_m_1 )
vibrator_4 = Vibrator( q = hw.VIBRATOR_ON_4,containers=[hw.FILLER_OPEN_4],weight = fillers_m_1 )
vibrator_5 = Vibrator( q = hw.VIBRATOR_ON_5,containers=[hw.FILLER_OPEN_5],weight = fillers_m_1 )
vibrator_6 = Vibrator( q = hw.VIBRATOR_ON_6,containers=[hw.FILLER_OPEN_6],weight = fillers_m_1 )

adapter_1.link(filler_1)
adapter_2.link(filler_2)
adapter_3.link(filler_3)

c_motor_1 = Motor(on=hw.CONVEYOR_ON_1,off=hw.CONVEYOR_OFF_1,ison=hw.CONVEYOR_ON_1)        #конвейер управляется 2мя сигналами
tc_motor_1 = Motor(on=hw.TCONVEYOR_ON_1,off=hw.TCONVEYOR_OFF_1,ison=True)     #транспортный тоже
                
tc_gear_1 = DROT(clk=hw.TCONVEYOR_ROTATING_1,ms=3000)
c_gear_1 = DROT(clk=hw.CONVEYOR_ROTATING_1,ms=3000)

tconveyor_1 = Transport(ison=lambda: tc_gear_1.rotating,out = c_motor_1.remote,power = tc_motor_1.remote )

#инертные выгружаются на транспорт, включение через транспорт происходит
dfillers_1 = Dosator(m = fillers_m_1.get_m, closed=lambda: not c_gear_1.rotating, containers=(filler_1,filler_2,filler_3),out=tconveyor_1.set_auto,lock=Lock(key=lambda: not(hw.FILLER_CLOSED_1 and hw.FILLER_CLOSED_2 and hw.FILLER_CLOSED_3 and hw.FILLER_CLOSED_4 and hw.FILLER_CLOSED_5 and hw.FILLER_CLOSED_6)))

df_vibrator_1 = UnloadHelper(q=hw.DF_VIBRATOR_ON_1,dosator=dfillers_1,weight=fillers_m_1, dr=1000 )

mcontainer_1 = ManualDosator( closed=hw.MCONTAINER_CLOSED_1, out=hw.MCONTAINER_OPEN_1,dosator=dfillers_1,mode=1,helper=hw.MC_VIBRATOR_ON_1,level=lambda: mclevel_1.level)

motor_1 = Motor(on = hw.MIXER_ON_1,off=hw.MIXER_OFF_1,ison=hw.MIXER_ISON_1)
gate_1 = MPGate(open = hw.MIXER_OPEN_1,close = hw.MIXER_CLOSE_1,closed=hw.MIXER_CLOSED_1,opened=hw.MIXER_OPENED_1,middle=hw.MIXER_MIDDLE_1)

class Mixer10(Mixer):
    expense_0 = POU.var(float(0))
    expense_1 = POU.var(float(0))
    expense_2 = POU.var(float(0))
    expense_3 = POU.var(float(0))
    expense_4 = POU.var(float(0))
    expense_5 = POU.var(float(0))
    expense_6 = POU.var(float(0))
    expense_7 = POU.var(float(0))
    expense_8 = POU.var(float(0))
    expense_9 = POU.var(float(0))
    
mixer_1 = Mixer10(motor=motor_1,gate=gate_1,flows=[x.q for x in [silage_1,silage_2,water_1,addition_1,addition_2,addition_3,addition_4]]+[x.q for x in mcontainer_1.expenses])

ready_1 = Readiness(rails=[dcement_1,dwater_1,dadditions_1,dadditions_2,mcontainer_1,mixer_1] )
loaded_1 = Loaded(rails=[dcement_1,dwater_1,dadditions_1,dadditions_2,mcontainer_1] )
manager_1 = Manager(collected=ready_1,loaded=loaded_1,mixer=mixer_1,dosators=[dcement_1,dwater_1,dadditions_1,dadditions_2,mcontainer_1])

factory_1.on_mode = tuple(x.switch_mode for x in [dcement_1,dwater_1,dadditions_1,dadditions_2,dfillers_1,mcontainer_1,silage_1,water_1,addition_1,addition_2,addition_3,addition_4,filler_1,filler_2,filler_3] )
factory_1.on_emergency = tuple(x.emergency for x in [manager_1,mixer_1,dcement_1,dwater_1,dadditions_1,dadditions_2,dfillers_1,mcontainer_1,silage_1,water_1,addition_1,addition_2,addition_3,addition_4,filler_1,filler_2,filler_3 ])

def mem_manager():
    mem = factory_1.mem
    if mem<40 and not gc.isenabled():
        gc.enable()
    elif mem>90 and gc.isenabled():
        gc.disable()
    if ready_1.q:
        gc.collect()
        
def addons():
    if not hw.EMERGENCY_1:
        hw.MIXER_OFF_1 = True
        hw.MIXER_ON_1 = False
        hw.CONVEYOR_ON_1 = False
        hw.CONVEYOR_OFF_1 = True
        hw.TCONVEYOR_ON_1 = False
        hw.TCONVEYOR_OFF_1 = True

    tconveyor_1.set_auto(dfillers_1.out)    #TODO: убрать этот хак, чтобы без него работало

    if hw.MAN_DISABLE_1:
        hw.MANUAL_ON_1 = False
        return
    
    hw.MANUAL_ON_1 = True
    factory_1.manual = True
    hw.MIXER_ON_1 = hw.MAN_MIXER_ON_1
    hw.MIXER_OFF_1 = not hw.MAN_MIXER_OFF_1
    hw.AUGER_ON_1 = hw.MAN_AUGER_ON_1
    hw.MIXER_CLOSE_1 = hw.MAN_MIXER_CLOSE_1
    hw.MIXER_OPEN_1 = hw.MAN_MIXER_OPEN_1
    hw.WATER_OPEN_1 = hw.MAN_WATER_OPEN_1

instances = ( 
            manager_1, factory_1, ready_1, loaded_1,
            cement_m_1, dcement_1, silage_1, silage_2, aerator_1,aerator_2,
            water_m_1, dwater_1, water_1,  
            additions_m_1,dadditions_1, addition_1, addition_2,
            additions_m_2,dadditions_2, addition_3, addition_4,
            fillers_m_1, dfillers_1, mcontainer_1, filler_1, filler_2, filler_3, tconveyor_1,tc_motor_1,c_motor_1,c_gear_1,tc_gear_1,
            adapter_1,adapter_2,adapter_3,vibrator_1, vibrator_2,vibrator_3,vibrator_4,vibrator_5,vibrator_6,
            dc_vibrator_1,df_vibrator_1,
            motor_1, gate_1, mixer_1,
            mclevel_1,
            wpump_1, wpump_out_1,apump_1,apump_2,apump_3,apump_4,
            addons,
            # mem_manager
            )

def imitation()->Tuple[POU,...]:    #если имитацию создавать внутри функции, то не будет проблем с импортами и глобальными переменными, а так же не будет проблем с автокомплитом в VSCode
    global hw
    if TYPE_CHECKING:
        hw = HW()
        
    from concrete.imitation import iVALVE,iMOTOR,iGATE,iWEIGHT,iROTARYFLOW
    
    imotor_1 = iMOTOR(on = hw.MIXER_ON_1,off=hw.MIXER_OFF_1,ison=hw.MIXER_ISON_1)
    igate_1 = iGATE(open = hw.MIXER_OPEN_1,close=hw.MIXER_CLOSE_1,closed=hw.MIXER_CLOSED_1,opened=hw.MIXER_OPENED_1,middle=hw.MIXER_MIDDLE_1)

    idcement_1 = iVALVE(open = hw.DCEMENT_OPEN_1,opened=hw.DCEMENT_CLOSED_1)
    idwater_1 = iVALVE(open = hw.DWATER_OPEN_1,opened=hw.DWATER_CLOSED_1)
    idadditions_1 = iVALVE(open = hw.DADDITIONS_OPEN_1,closed=hw.DADDITIONS_CLOSED_1)
    idadditions_2 = iVALVE(open = hw.DADDITIONS_OPEN_2,closed=hw.DADDITIONS_CLOSED_2)
    
    imcontainer = iGATE(simple=True,open = hw.MCONTAINER_OPEN_1,closed=hw.MCONTAINER_CLOSED_1)

    iauger_1 = iMOTOR(simple=True,on = hw.AUGER_ON_1,ison=hw.AUGER_ISON_1)
    iauger_2 = iMOTOR(simple=True,on = hw.AUGER_ON_2,ison=hw.AUGER_ISON_2)
    iwater_1 = iVALVE(open = hw.WATER_OPEN_1,opened=hw.WATER_CLOSED_1)
    iaddition_1 = iVALVE(open = hw.ADDITION_OPEN_1,opened=hw.ADDITION_CLOSED_1)
    iaddition_2 = iVALVE(open = hw.ADDITION_OPEN_2,opened=hw.ADDITION_CLOSED_2)
    iaddition_3 = iVALVE(open = hw.ADDITION_OPEN_3,opened=hw.ADDITION_CLOSED_3)
    iaddition_4 = iVALVE(open = hw.ADDITION_OPEN_4,opened=hw.ADDITION_CLOSED_4)
    
    ifiller_1 = iVALVE(open = hw.FILLER_OPEN_1,closed=hw.FILLER_CLOSED_1)
    ifiller_2 = iVALVE(open = hw.FILLER_OPEN_2,closed=hw.FILLER_CLOSED_2)
    ifiller_3 = iVALVE(open = hw.FILLER_OPEN_3,closed=hw.FILLER_CLOSED_3)
    ifiller_4 = iVALVE(open = hw.FILLER_OPEN_4,closed=hw.FILLER_CLOSED_4)
    ifiller_5 = iVALVE(open = hw.FILLER_OPEN_5,closed=hw.FILLER_CLOSED_5)
    ifiller_6 = iVALVE(open = hw.FILLER_OPEN_6,closed=hw.FILLER_CLOSED_6)
    
    icement_m_1 = iWEIGHT(speed=100, q = hw.CEMENT_M_1,loading=lambda: hw.AUGER_ON_1 or hw.AUGER_ON_2, unloading=hw.DCEMENT_OPEN_1)
    iwater_m_1 = iWEIGHT(speed=100,q = hw.WATER_M_1,loading=hw.WATER_OPEN_1, unloading=hw.DWATER_OPEN_1)
    iadditions_m_1 = iWEIGHT(speed=100,q = hw.ADDITIONS_M_1,loading=lambda: hw.ADDITION_OPEN_1 or hw.ADDITION_OPEN_2, unloading=hw.DADDITIONS_OPEN_1)
    iadditions_m_2 = iWEIGHT(speed=100,q = hw.ADDITIONS_M_2,loading=lambda: hw.ADDITION_OPEN_3 or hw.ADDITION_OPEN_4, unloading=hw.DADDITIONS_OPEN_2)
    ifillers_m_1 = iWEIGHT(speed=100, q = hw.FILLERS_M_1,loading=lambda: hw.FILLER_OPEN_1 or hw.FILLER_OPEN_2 or hw.FILLER_OPEN_3 or hw.FILLER_OPEN_4 or hw.FILLER_OPEN_5 or hw.FILLER_OPEN_6, unloading=lambda: c_motor_1.powered)
    imcontainer_m_1 = iWEIGHT(speed=100, q = hw.MCONTAINER_M_1,loading=lambda: c_motor_1.powered, unloading=hw.MCONTAINER_OPEN_1)
    itconv_rot_1 = iROTARYFLOW(loading=lambda: tc_motor_1.powered, clk = hw.TCONVEYOR_ROTATING_1 )
    iconv_rot_1 = iROTARYFLOW(loading=lambda: c_motor_1.powered, clk = hw.CONVEYOR_ROTATING_1 )
    
    hw.A_POWER_OK_1.force(True)
    hw.C_POWER_OK_1.force(True)
    hw.INPUT_OK_1.force(True)
    hw.MIXER_ADOOR_CLOSED_1.force(True)
    hw.P_POWER_OK_1.force(True)
    hw.M_POWER_OK_1.force(True)
    hw.CONV_POWER_OK_1.force(True)
    hw.LLEVEL_SILAGE_1.force(True)
    hw.MAN_DISABLE_1.force(True)
    hw.EMERGENCY_1.force(True)
    
    return (imotor_1, igate_1, 
            idcement_1, iauger_1, iauger_2, icement_m_1, 
            idwater_1, iwater_1, iwater_m_1, 
            idadditions_1, iaddition_1, iaddition_2, iadditions_m_1, 
            idadditions_2, iaddition_3, iaddition_4, iadditions_m_2, 
            ifiller_1, ifiller_2, ifiller_3, ifiller_4, ifiller_5, ifiller_6, ifillers_m_1, 
            imcontainer, 
            itconv_rot_1, 
            iconv_rot_1,
            imcontainer_m_1,)

if sys.platform=='esp32':
    instances += imitation( )
    
if plc: plc.run(instances=instances,ctx=globals())

gc.collect()
