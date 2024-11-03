from machine import I2C, Pin
import time
import math
import random


mode = 6
max_mode = 8
counter = 0.0
delay_time = 100
direction = 1
velocity = 0
location = 0
smoothed_loc = 0
step = 1500
step_change = -1
c2 = 0
tw = 0
prev_tw = 0
vel_array = [1,2,4,8,16,32,64]
loc_array = [0,0,0,0,0,0,0]
rot_count = 0
timeout = 5000
timestep = 5

display = bytearray(8)


debounce = { buttonA : 0, buttonB : 0 , buttonC : 0 }
clicked = { buttonA : False, buttonB : False , buttonC : False }

debounce_max = 8

intensity_vals = bytearray(8)


while True:

    for button in [buttonA, buttonB, buttonC]:
        clicked[button] = False
        if not button.value() and debounce[button] < debounce_max:
            debounce[button] = debounce[button] + 1
            if debounce[button] == 4:
                clicked[button] = True
        elif debounce[button] > 0:
            debounce[button] = debounce[button] - 1
         
    if clicked[buttonA]:
        mode = (mode + 1) % max_mode
        timeout = 5000
        print("mode:", mode)
     
    timeout = timeout - timestep
    if timeout < 0:
        mode = random.randint(0,max_mode)
        timeout = 5000
        
    if mode == 0:
        ## see what's going on with the touch wheel
        if touchwheel_bus:
            
            tw = touchwheel_read(touchwheel_bus)
            if tw != 0:
                
                #temploc = location % 256
                if (prev_tw - tw) % 256 < (tw - prev_tw) % 256:
                    velocity = (prev_tw - tw) % 256
                else:
                    velocity =  -((tw - prev_tw) % 256)
                location = location + velocity
                smoothed_loc = (location + smoothed_loc * 3) >> 2 
                print(smoothed_loc)
                prev_tw = tw
                
              
        step = step + step_change      
        if step > 2000 or step < 1000:
            step_change = -step_change
            
        
        if tw > 0:
            delay_time = 10 + tw
        
        for i in range(7):
            loc_array[i] += vel_array[i]
            if loc_array[i] >= 1024:
                loc_array[i] = loc_array[i] - 1024
                
                
        
        
        c2 = c2 + (step >> 3)
        limit = 2000
        if c2 >= limit:
            
            #print(velocity)
            c2 = c2 - limit
            counter = counter + math.pi/16
            if counter > 2 * math.pi:
                counter = counter - 2 * math.pi
                                
            ## display touchwheel on petal
            if petal_bus and touchwheel_bus:
                phase = int((math.sin(counter) + 1) * 9)
                phase2 = int((math.sin(counter) + 1) * 4)
                if phase <= 1:
                    bitmap = ((0x7f << phase) & 0x7f00) >> 8 | 0x80
                else:                
                    bitmap = ((0x7f << phase) & 0x7f00) >> 8
                    
                for i in range(8):
                    display[i] = bitmap
                    intensity_vals[i] = phase2
                #if i == petal:
                #    petal_bus.writeto_mem(0, i, bytes([0x3F]))
                #else:
                #    petal_bus.writeto_mem(0, i, bytes([0x00]))
    elif mode == 1:
             
        c2 = c2 + 1
        
        intensity = int((math.sin(c2 / 30.0) + 1) * 8)
        intensity = min(max(intensity, 0), 15)
        for i in range(8):
            display[i] = 0x7f
            intensity_vals[i] = intensity
 
    elif mode == 2:
        
        c2 = c2 + 1
        phase = (c2 >> 4) % 8
        for i in range(8):
            pd = (phase - i) % 8
            intensity_vals[i] = min(15,max(0, (7 - pd * 2) * 2))
            if pd <= 4:
                display[i] = 0x7f
            else:
                display[i] = 0x00
    
    elif mode == 3:
        for i in range(8):
            if random.randint(0,1000) < 20:
                intensity_vals[i] = max(0,min(15,intensity_vals[i] + random.randint(-1,2)))
            for j in range(7):
                if random.randint(0,1000) < 10:
                    display[i] = display[i] ^ 1 << j
    elif mode == 4:
        c2 = c2 + 1
        phase = (c2 >> 3) % 24
        for i in range(8):
            intensity_vals[i] = 9
            if int(phase / 3) == i:
                display[i] = 1 << (6 - (phase % 3))
            else:
                display[i] = 0x00
                
    elif mode == 5:
        for i in range(8):
            display[i] = random.getrandbits(7)
            intensity_vals[i] = random.randint(1,10)
            
    elif mode == 6:
        c2 = c2 + 1
        phase = (c2 >> 4) % (7 * 8 + 1)
        for i in range(8):
            intensity_vals[i] = 9
            display[i] = 0
            for j in range(7):
                idx = i*7 + j
                if phase == (idx * (j+i)) % (7 * 8):
                    display[i] = display[i] | 1 << j

        
            
    for i in range(4):
        base_reg = 0x10
        reg_byte = intensity_vals[i*2+1] << 4 | intensity_vals[i*2]
        petal_bus.writeto_mem(PETAL_ADDRESS, base_reg + i, bytes([reg_byte])) 

            
    for i in range(8):
        base_reg = 0x01
        petal_bus.writeto_mem(PETAL_ADDRESS, base_reg + i, bytes([display[i]]))
 
    time.sleep_ms(timestep)
    bootLED.off()






    
