from machine import I2C, Pin
import time

counter = 0
delay_time = 100
direction = 1
velocity = 0
location = 0
smoothed_loc = 0
step = 1000
step_change = -1
c2 = 0
tw = 0
prev_tw = 0
vel_array = [1,2,4,8,16,32,64]
loc_array = [0,0,0,0,0,0,0]
rot_count = 0

intensity_regs = [0x00,0x00,0x00,0x00, 0x00,0x00,0x00,0x00]


while True:

    ## display button status on RGB
    if False:
        if not buttonA.value():
            petal_bus.writeto_mem(PETAL_ADDRESS, 2, bytes([0x80]))
        else:
            petal_bus.writeto_mem(PETAL_ADDRESS, 2, bytes([0x00]))

        if not buttonB.value():
            petal_bus.writeto_mem(PETAL_ADDRESS, 3, bytes([0x80]))
        else:
            petal_bus.writeto_mem(PETAL_ADDRESS, 3, bytes([0x00]))

        if not buttonC.value():
            petal_bus.writeto_mem(PETAL_ADDRESS, 4, bytes([0x80]))
        else:
            petal_bus.writeto_mem(PETAL_ADDRESS, 4, bytes([0x00]))

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
    if step > 2000 or step < 400:
        step_change = -step_change
        
    
    if tw > 0:
        delay_time = 10 + tw
    
    for i in range(7):
        loc_array[i] += vel_array[i]
        if loc_array[i] >= 1024:
            loc_array[i] = loc_array[i] - 1024
            
            
    
    c2 = c2 + (step >> 3)
    limit = 1000
    if c2 >= limit:
        
        #print(velocity)
        c2 = c2 - limit
        counter = counter + direction
        if counter == 18 or counter == 0:
            direction = -direction
            #print(velocity)
        
        rot_count = (rot_count + 1) % 8
        for i in range(8):
            if (i % 4) == (rot_count % 4):
                intensity_regs[i] = 0x0F
            elif (i+1 % 4) == (rot_count % 4) or (i-1 % 4) == (rot_count % 4):
                intensity_regs[i] = 0x07
            else:                
                intensity_regs[i] = 0x00
                
        ## display touchwheel on petal
        if petal_bus and touchwheel_bus:
            for i in range(4):im
                base_addr = 0x10
                #intensity_byte = (intensity_regs[i*2+1] << 4) | intensity_regs[i*2]
                intensity = int(15.5 * (step - 400) / (2000 - 400))
                intensity_byte = intensity << 4 | intensity
                
                petal_bus.writeto_mem(PETAL_ADDRESS, base_addr+i, bytes([intensity_byte]))
            
            bitmap = 0
            for i in range(counter):
                bitmap = ((0x7f << counter) & 0x7f00) >> 8 
            for i in range(1,9):
                petal_bus.writeto_mem(PETAL_ADDRESS, i, bytes([bitmap]))
            #if i == petal:
            #    petal_bus.writeto_mem(0, i, bytes([0x3F]))
            #else:
            #    petal_bus.writeto_mem(0, i, bytes([0x00]))


    
    time.sleep_ms(10)
    bootLED.off()






