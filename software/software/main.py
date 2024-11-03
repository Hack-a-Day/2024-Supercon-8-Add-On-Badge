from machine import I2C, Pin
import time
import math
import random



max_mode = 13
mode = max_mode - 1
counter = 0.0
delay_time = 100
direction = 1
velocity = 0
location = 0
smoothed_loc = 0
c2 = 0
tw = 0
prev_tw = 0
vel_array = [1,2,4,8,16,32,64]
loc_array = [0,0,0,0,0,0,0]
rot_count = 0
timeout = 8000
countdown = timeout
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
        countdown = timeout
        c2 = 0
        print("mode:", mode)
     
    countdown = countdown - timestep
    if countdown < 0:
        next_mode = mode
        while next_mode == mode:
            next_mode = random.randint(0,max_mode-1)
        mode = next_mode
        c2 = 0
        countdown = timeout
        print("mode:", mode)
        
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
                              
        
        for i in range(7):
            loc_array[i] += vel_array[i]
            if loc_array[i] >= 1024:
                loc_array[i] = loc_array[i] - 1024
                
        c2 = c2 + 1
        limit = 10
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
        for i in range(8):
            display[i] = 0
        c2 = c2 + 1
        phase = (c2 >> 3) % 24
        phase2 = (-c2 >> 5) % 8
        for i in range(8):
            intensity_vals[i] = 9
            if int(phase / 3) == i:
                display[i] = display[i] | 1 << (6 - (phase % 3))
        for i in range(8):
            if phase2 == i:
                display[i] = display[i] | 1
        
                  
                
    elif mode == 5:
        for i in range(8):
            display[i] = random.getrandbits(7) & random.getrandbits(7) & random.getrandbits(7) & random.getrandbits(7) & random.getrandbits(7) & random.getrandbits(7)
            intensity_vals[i] = random.randint(1,10) 
            
    elif mode == 6:
        c2 = c2 + 1
        phase = (c2 >> 3) % (7+8)
        for i in range(8):
            intensity_vals[i] = 9
            display[i] = 0
            for j in range(7):
                if phase == j+i:
                    display[i] = display[i] | 1 << j
                
    
    elif mode == 7:
        c2 = c2 + 1
        t1 = c2 / 30
        t2 = t1 - math.pi / 8
        t3 = t2 - math.pi / 8
        count = int(t1 / (math.pi * 2))

        p1 = (count + int((math.sin(t1) + 1) * 4)) % 8
        p2 = (count + int((math.sin(t2) + 1) * 4)) % 8
        p3 = (count + int((math.sin(t3) + 1) * 4)) % 8
        
        for i in range(8):
            if i == p1:
                display[i] = 0x7f
                intensity_vals[i] = 15
            elif i == p2:
                display[i] = 0x78
                intensity_vals[i] = 7
            elif i == p3:
                display[i] = 0x60
                intensity_vals[i] = 0
            else:
                display[i] = 0x00
        
    elif mode == 8:
        c2 = c2 + 1
        pattern = 0xff00ff
        for i in range(8):
            phase = ((c2 >> 4) + i) % 8
            display[i] = (pattern << phase) & 0x7f
            intensity_vals[i] = 9            
     
    elif mode == 9:
        step = int((math.sin(c2 / 900) + 2) * 10) 
        c2 = c2 + step
        phase = (c2 >> 8) % 4
        for i in range(8):
            pd = (phase - i) % 4
            intensity_vals[i] = min(15,max(0, (4 - pd * 3) * 4))
            if pd < 3:
                display[i] = 0x7f
            else:
                display[i] = 0x00
    
    elif mode == 10:
        for i in range(8):
            pattern = 0
            for j in range(7):
                if random.randint(0,1000) < 20 * (8 - j):
                    pattern = pattern | 1 << j
            display[i] = pattern
            intensity_vals[i] = random.randint(1,10) 
    
    elif mode == 11:
        c2 = c2 + 1
        
        phase = (c2 * 3 >> 5) % 8
        stepx = (c2 * 5 >> 10) % 16 + 1
        
        for i in range(8):
            intensity_vals[i] = 9
            display[i] = 0
            for j in range(7):
                if (phase + j * 8 + i) % stepx == 0:
                    display[i] = 1 << j
            
    elif mode == 12:
        for i in range(8):
            display[i] = 0
        c2 = c2 + 1
        phase = (c2 >> 3) % 24
        phase2 = (-c2 >> 5) % 8
        for loc in range(4):
        
            for i in range(8):
                intensity_vals[i] = 9
                if int(phase / 3) == i:
                    display[i] = display[i] | 1 << (6 - (phase % 3))
            phase = (phase + 1) % 24
            
        for i in range(8):
            if phase2 == i:
                display[i] = display[i] | 1
            if (phase2 + 1) % 8 == i:
                display[i] = display[i] | 2
                    
                    
            
    for i in range(4):
        base_reg = 0x10
        reg_byte = intensity_vals[i*2+1] << 4 | intensity_vals[i*2]
        petal_bus.writeto_mem(PETAL_ADDRESS, base_reg + i, bytes([reg_byte])) 

            
    for i in range(8):
        base_reg = 0x01
        petal_bus.writeto_mem(PETAL_ADDRESS, base_reg + i, bytes([display[i]]))
 
    time.sleep_ms(timestep)
    bootLED.off()






    
