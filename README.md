# 2024 Supercon 8 -- 2025 Hackaday Europe -- Simple Add-On Badge

![Badge Glamour Shot](resources/badge_photos/supercon8_sao_badge_featured.png)

The badge, on the surface, is a simple hub for six SAOs.  But behind the scenes it is an attempt to unleash the power of I2C that lies within many.

It runs Micropython, so getting started is as easy as plugging it in to your computer and opening a serial terminal.  Or go the fancy route and use Thonny or VSCode.  The fun is going to be in how you combine whatever SAOs you've got on hand to make something greater than the sum of their parts.

I2C basically pretends that every device is a memory, so you're looking at read and write commands. Maybe get started with the LED and Touchwheel petals, using Python's `writeto_mem()` and `readfrom_mem()` functions.  Check out the `boot.py` and `main.py` files on the badge itself for a quick-and-dirty demo.  Check out the docs on the Touchwheel add-on [for the memory map](https://github.com/todbot/TouchwheelSAO/blob/aa99cc62883fd20384521d5f405f3abf2ee274b1/firmware/TouchwheelSAO_attiny816/TouchwheelSAO_attiny816.ino#L40).  Or start writing arbitrary bytes to the LED petal's first eight registers and see what you get!

One of the Add-ons that come with the badge is a [protoboard](https://github.com/Hack-a-Day/2024-Supercon-8-Add-On-Badge/tree/main/hardware/sao/i2c_proto_petal) to [make your own arbitrary I2C device](https://github.com/Hack-a-Day/2024-Supercon-8-Add-On-Badge/tree/main/i2c_proto_petal_tutorial) using a CH32v003 RISC-V chip, using the badge itself to program the chip. We piggyback strongly on [Charles Lohr]'s [marvelous CH32fun library](https://github.com/cnlohr/ch32fun). Check out the I2C demos in the examples library. 

If you need to connect multiple badges together, we really like [Aask]'s framework that piggybacks the I2C channels over MQTT that she and a team wrote during Supercon: Super-8.  It requires blowing away the stock software, but you can always download that again anyway.

