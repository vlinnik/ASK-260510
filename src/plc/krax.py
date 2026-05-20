
from pyplc.platform import plc,hw
from pyplc.utils.logging import logger
from pyplc.pou import POU
from project import name as project_name,version as project_version
from typing import Tuple
from concrete import Factory,Mixer,Motor,MSGate,Weight,Dosator,Container,Manager,Readiness,Loaded,Lock
from concrete.dosator import ManualDosator
from concrete.transport import Transport,DROT
from concrete.vibrator import Vibrator,UnloadHelper
from concrete.container import Assembly2
import sys
import gc

#VSCode autocompleter блок.
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from collections import namedtuple
    HW = namedtuple('HW',['CEMENT_M_1','WATER_M_1','ADDITION_M_1','ADDITION_M_2','FILLERS_M_1','MCONTAINER_M_1','MIXER_I_1','DCEMENT_CLOSED_1','DWATER_CLOSED_1','DADDITIONS_CLOSED_1','DADDITIONS_CLOSED_2','MCONTAINER_CLOSED_1','MCONTAINER_OPENED_1','AUGER_ISON_1','AUGER_ISON_2','WATER_CLOSED_1','ADDITION_CLOSED_1','ADDITION_CLOSED_2','ADDITION_CLOSED_3','ADDITION_CLOSED_4','FILLER_CLOSED_1','FILLER_CLOSED_2','FILLER_CLOSED_3','FILLER_CLOSED_4','FILLER_CLOSED_5','FILLER_CLOSED_6','MIXER_CLOSED_1','MIXER_OPENED_1','MIXER_ISON_1','CONVEYOR_ISON_1','CONVEYOR_ROTATING_1','TCONVEYOR_ISON_1','TCONVEYOR_ROTATING_1','PUMP_WATER_ISON_1','PUMP_ADDITION_1_ISON_1','PUMP_ADDITION_2_ISON_1','PUMP_ADDITION_3_ISON_1','PUMP_ADDITION_4_ISON_1','ROPE_CONVEYOR_1','ROPE_TCONVEYOR_1','AUTOMAT_1_ISON_1','AUTOMAT_2_ISON_1','AUTOMAT_3_ISON_1','DCEMENT_OPEN_1','DWATER_OPEN_1','DADDITIONS_OPEN_1','DADDITION_OPEN_2','CONVEYOR_ON_1','CONVEYOR_OFF_1','TCONVEYOR_ON_1','TCONVEYOR_OFF_1','MCONTAINER_OPEN_1','AUGER_ON_1','AUGER_ON_2','WPUMP_ON_1','APUMP_ON_1','APUMP_ON_2','APUMP_ON_3','APUMP_ON_4','FILLER_OPEN_1','FILLER_OPEN_2','FILLER_OPEN_3','FILLER_OPEN_4','FILLER_OPEN_5','FILLER_OPEN_6','MIXER_ON_1','MIXER_OFF_1','MIXER_OPEN_1','WATER_OPEN_1','ADDITION_OPEN_1','ADDITION_OPEN_2','ADDITION_OPEN_3','ADDITION_OPEN_4'],defaults=[])
    hw = HW()

logger.info(f'Запуск проекта {project_name} {project_version}')

factory_1 = Factory()

cement_m_1 = Weight(raw=hw.CEMENT_M_1,mmax=1500)
silage_1 = Container(m = cement_m_1.get_m ,out=hw.AUGER_ON_1,closed=~hw.AUGER_ON_1)
dcement_1 = Dosator(m = cement_m_1.get_m, out = hw.DCEMENT_OPEN_1,closed=hw.DCEMENT_CLOSED_1, containers=(silage_1,))
dc_vibrator_1 = UnloadHelper(q=hw.DC_VIBRATOR_ON_1,dosator=dcement_1,weight=cement_m_1,point=20, dr=3000)

water_m_1 = Weight(raw=hw.WATER_M_1,mmax=500)
water_1 = Container(m = water_m_1.get_m, out=hw.WATER_OPEN_1,closed=hw.WATER_CLOSED_1)
dwater_1 = Dosator(m = water_m_1.get_m, out = hw.DWATER_OPEN_1,closed=hw.DWATER_CLOSED_1, containers=(water_1,))

additions_m_1 = Weight(raw=hw.ADDITIONS_M_1,mmax=50)
addition_1 = Container(m = additions_m_1.get_m, out=hw.ADDITION_OPEN_1,closed=hw.ADDITION_CLOSED_1)
dadditions_1 = Dosator(m = additions_m_1.get_m, out = hw.DADDITIONS_OPEN_1,closed=hw.DADDITIONS_CLOSED_1, containers=(addition_1,))

fillers_m_1 = Weight(raw=hw.FILLERS_M_1,mmax=6000)


adapter_1 = Assembly2(outs=(hw.FILLER_OPEN_1,hw.FILLER_OPEN_2),sts=(hw.FILLER_CLOSED_1,hw.FILLER_CLOSED_2) )
adapter_2 = Assembly2(outs=(hw.FILLER_OPEN_3,hw.FILLER_OPEN_4),sts=(hw.FILLER_CLOSED_3,hw.FILLER_CLOSED_4) )
adapter_3 = Assembly2(outs=(hw.FILLER_OPEN_5,hw.FILLER_OPEN_6),sts=(hw.FILLER_CLOSED_5,hw.FILLER_CLOSED_6) )

filler_1 = Container(m = fillers_m_1.get_m, out=adapter_1.out,closed=adapter_1.closed,lock=Lock(key=lambda: hw.CONVEYOR_ISON_1 or not adapter_2.closed() or not adapter_3.closed() ))
filler_2 = Container(m = fillers_m_1.get_m, out=adapter_2.out,closed=adapter_2.closed,lock=Lock(key=lambda: hw.CONVEYOR_ISON_1 or not adapter_1.closed() or not adapter_3.closed()))
filler_3 = Container(m = fillers_m_1.get_m, out=adapter_3.out,closed=adapter_3.closed,lock=Lock(key=lambda: hw.CONVEYOR_ISON_1 or not adapter_2.closed() or not adapter_1.closed()))

vibrator_1 = Vibrator( q = hw.VIBRATOR_ON_1,containers=(hw.FILLER_OPEN_1,),weight = fillers_m_1 )
vibrator_2 = Vibrator( q = hw.VIBRATOR_ON_2,containers=(hw.FILLER_OPEN_2,),weight = fillers_m_1 )
vibrator_3 = Vibrator( q = hw.VIBRATOR_ON_3,containers=(hw.FILLER_OPEN_3,),weight = fillers_m_1 )
vibrator_4 = Vibrator( q = hw.VIBRATOR_ON_4,containers=(hw.FILLER_OPEN_4,),weight = fillers_m_1 )
vibrator_5 = Vibrator( q = hw.VIBRATOR_ON_5,containers=(hw.FILLER_OPEN_5,),weight = fillers_m_1 )
vibrator_6 = Vibrator( q = hw.VIBRATOR_ON_6,containers=(hw.FILLER_OPEN_6,),weight = fillers_m_1 )

adapter_1.link(filler_1)
adapter_2.link(filler_2)
adapter_3.link(filler_3)

c_motor_1 = Motor(on=hw.CONVEYOR_ON_1,off=hw.CONVEYOR_OFF_1,ison=hw.CONVEYOR_ISON_1)        #конвейер управляется 2мя сигналами
tc_motor_1 = Motor(on=hw.TCONVEYOR_ON_1,off=hw.TCONVEYOR_OFF_1,ison=hw.TCONVEYOR_ISON_1)    #транспортный тоже
                
tc_gear_1 = DROT(clk=hw.TCONVEYOR_ROTATING_1,ms=2000)
c_gear_1 = DROT(clk=hw.CONVEYOR_ROTATING_1,ms=2000)

tconveyor_1 = Transport(ison=lambda: tc_gear_1.rotating,out = c_motor_1.remote,power = tc_motor_1.remote )

#инертные выгружаются на транспорт, включение через транспорт происходит
dfillers_1 = Dosator(m = fillers_m_1.get_m, closed=lambda: not c_gear_1.rotating, containers=(filler_1,filler_2,filler_3),out=tconveyor_1.set_auto,lock=Lock(key=lambda: not(hw.FILLER_CLOSED_1 and hw.FILLER_CLOSED_2 and hw.FILLER_CLOSED_3 and hw.FILLER_CLOSED_4 and hw.FILLER_CLOSED_5 and hw.FILLER_CLOSED_6)))

df_vibrator_1 = UnloadHelper(q=hw.DF_VIBRATOR_ON_1,dosator=dfillers_1,weight=fillers_m_1, dr=1000 )

mcontainer_1 = ManualDosator( closed=hw.MCONTAINER_CLOSED_1, out=hw.MCONTAINER_OPEN_1,dosator=dfillers_1,mode=1,helper=hw.MC_VIBRATOR_ON_1)

motor_1 = Motor(on = hw.MIXER_ON_1,off=hw.MIXER_OFF_1,ison=hw.MIXER_ISON_1)
gate_1 = MSGate(open = hw.MIXER_OPEN_1,closed=hw.MIXER_CLOSED_1,opened=hw.MIXER_OPENED_1)
mixer_1 = Mixer(motor=motor_1,gate=gate_1,flows=tuple([x.q for x in [silage_1,water_1,addition_1]]+[x.q for x in mcontainer_1.expenses]))

ready_1 = Readiness(rails=[dcement_1,dwater_1,dadditions_1,mcontainer_1,mixer_1] )
loaded_1 = Loaded(rails=[dcement_1,dwater_1,dadditions_1,mcontainer_1] )
manager_1 = Manager(collected=ready_1,loaded=loaded_1,mixer=mixer_1,dosators=[dcement_1,dwater_1,dadditions_1,mcontainer_1])

factory_1.on_mode = tuple(x.switch_mode for x in [dcement_1,dwater_1,dadditions_1,dfillers_1,mcontainer_1,silage_1,water_1,addition_1,filler_1,filler_2,filler_3] )
factory_1.on_emergency = tuple(x.emergency for x in [manager_1,mixer_1,dcement_1,dwater_1,dadditions_1,dfillers_1,mcontainer_1,silage_1,water_1,addition_1,filler_1,filler_2,filler_3 ])

def mem_manager():
    mem = factory_1.mem
    if mem<40 and not gc.isenabled():
        gc.enable()
    elif mem>90 and gc.isenabled():
        gc.disable()
    if ready_1.q:
        gc.collect()

instances = ( 
            manager_1, factory_1, ready_1, loaded_1,
            cement_m_1, dcement_1, silage_1, 
            water_m_1, dwater_1, water_1,  
            additions_m_1,dadditions_1, addition_1, 
            fillers_m_1, dfillers_1, mcontainer_1, filler_1, filler_2, filler_3, tconveyor_1,tc_motor_1,c_motor_1,c_gear_1,tc_gear_1,
            adapter_1,adapter_2,adapter_3,vibrator_1, vibrator_2,vibrator_3,vibrator_4,vibrator_5,vibrator_6,
            dc_vibrator_1,df_vibrator_1,
            motor_1, gate_1, mixer_1,mem_manager 
            )

def imitation()->Tuple[POU,...]:    #если имитацию создавать внутри функции, то не будет проблем с импортами и глобальными переменными, а так же не будет проблем с автокомплитом в VSCode
    global hw
    from concrete.imitation import iVALVE,iMOTOR,iGATE,iWEIGHT,iROTARYFLOW
    
    imotor_1 = iMOTOR(on = hw.MIXER_ON_1,off=hw.MIXER_OFF_1,ison=hw.MIXER_ISON_1)
    igate_1 = iGATE(simple=True,open = hw.MIXER_OPEN_1,closed=hw.MIXER_CLOSED_1,opened=hw.MIXER_OPENED_1)

    idcement_1 = iVALVE(open = hw.DCEMENT_OPEN_1,closed=hw.DCEMENT_CLOSED_1)
    idwater_1 = iVALVE(open = hw.DWATER_OPEN_1,closed=hw.DWATER_CLOSED_1)
    idadditions_1 = iVALVE(open = hw.DADDITIONS_OPEN_1,closed=hw.DADDITIONS_CLOSED_1)
    
    iconveyor_1 = iMOTOR(on = hw.CONVEYOR_ON_1,off=hw.CONVEYOR_OFF_1,ison=hw.CONVEYOR_ISON_1)
    itconveyor_1 = iMOTOR(on = hw.TCONVEYOR_ON_1,off=hw.TCONVEYOR_OFF_1,ison=hw.TCONVEYOR_ISON_1)
    
    imcontainer = iGATE(simple=True,open = hw.MCONTAINER_OPEN_1,closed=hw.MCONTAINER_CLOSED_1,opened=hw.MCONTAINER_OPENED_1)

    iauger_1 = iMOTOR(simple=True,on = hw.AUGER_ON_1,ison=hw.AUGER_ISON_1)
    iwater_1 = iVALVE(open = hw.WATER_OPEN_1,closed=hw.WATER_CLOSED_1)
    iaddition_1 = iVALVE(open = hw.ADDITION_OPEN_1,closed=hw.ADDITION_CLOSED_1)
    
    ifiller_1 = iVALVE(open = hw.FILLER_OPEN_1,closed=hw.FILLER_CLOSED_1)
    ifiller_2 = iVALVE(open = hw.FILLER_OPEN_2,closed=hw.FILLER_CLOSED_2)
    ifiller_3 = iVALVE(open = hw.FILLER_OPEN_3,closed=hw.FILLER_CLOSED_3)
    ifiller_4 = iVALVE(open = hw.FILLER_OPEN_4,closed=hw.FILLER_CLOSED_4)
    ifiller_5 = iVALVE(open = hw.FILLER_OPEN_5,closed=hw.FILLER_CLOSED_5)
    ifiller_6 = iVALVE(open = hw.FILLER_OPEN_6,closed=hw.FILLER_CLOSED_6)
    
    icement_m_1 = iWEIGHT(speed=100, q = hw.CEMENT_M_1,loading=hw.AUGER_ON_1, unloading=hw.DCEMENT_OPEN_1)
    iwater_m_1 = iWEIGHT(speed=100,q = hw.WATER_M_1,loading=hw.WATER_OPEN_1, unloading=hw.DWATER_OPEN_1)
    iadditions_m_1 = iWEIGHT(speed=100,q = hw.ADDITIONS_M_1,loading=hw.ADDITION_OPEN_1, unloading=hw.DADDITIONS_OPEN_1)
    ifillers_m_1 = iWEIGHT(speed=100, q = hw.FILLERS_M_1,loading=lambda: hw.FILLER_OPEN_1 or hw.FILLER_OPEN_2 or hw.FILLER_OPEN_3 or hw.FILLER_OPEN_4 or hw.FILLER_OPEN_5 or hw.FILLER_OPEN_6, unloading=hw.CONVEYOR_ISON_1)
    itconv_rot_1 = iROTARYFLOW(loading=lambda: tc_motor_1.ison, clk = hw.TCONVEYOR_ROTATING_1 )
    iconv_rot_1 = iROTARYFLOW(loading=lambda: c_motor_1.ison, clk = hw.CONVEYOR_ROTATING_1 )
    
    return (imotor_1,igate_1,idcement_1,idwater_1,idadditions_1,iconveyor_1,itconveyor_1,imcontainer,iauger_1,iwater_1,iaddition_1,ifiller_1,ifiller_2,ifiller_3,ifiller_4,ifiller_5,ifiller_6,icement_m_1,iwater_m_1,ifillers_m_1,iadditions_m_1,itconv_rot_1,iconv_rot_1)

if sys.platform!='esp32' or True:
    instances += imitation( )

if plc: plc.run(instances=instances,ctx=globals())
