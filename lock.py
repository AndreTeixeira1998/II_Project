import  threading
import asyncio

lock = threading.Lock()
optimization_lock = threading.Lock()
mega_mutex = threading.Lock()
flag = threading.Event()
reverse_flag = threading.Event()

cell3_is_clear = asyncio.Event()
mb3_is_clear = asyncio.Event()
cond = asyncio.Event()

cond_pusher_1 = asyncio.Event()
cond_pusher_2 = asyncio.Event()
cond_pusher_3 = asyncio.Event()

