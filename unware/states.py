from aiogram.fsm.state import State, StatesGroup

class GetCarState(StatesGroup):
    waiting_for_car_id = State()

class GetSkinState(StatesGroup):
    waiting_for_skin_id = State()

class GetMapState(StatesGroup):
    waiting_for_map_id = State()

class AddCarState(StatesGroup):
    waiting_data = State()

class AddSkinState(StatesGroup):
    waiting_data = State()

class ModConvert(StatesGroup):
    collecting = State()
    ready = State()