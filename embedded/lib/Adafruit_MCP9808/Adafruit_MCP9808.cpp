/**************************************************************************/
/*! 
    @file     Adafruit_MCP9808.cpp
    @author   K.Townsend (Adafruit Industries)
    @license  BSD (see license.txt)
    
    I2C Driver for Microchip's MCP9808 I2C Temp sensor

    This is a library for the Adafruit MCP9808 breakout
    ----> http://www.adafruit.com/products/1782
        
    Adafruit invests time and resources providing this open source code, 
    please support Adafruit and open-source hardware by purchasing 
    products from Adafruit!

    @section  HISTORY

    v1.0 - First release
*/
/**************************************************************************/

// This is an edited version of the Adafruit file configured to work with ESP8266

#include <Wire.h>

#include "Adafruit_MCP9808.h"

/**************************************************************************/
/*! 
    @brief  Instantiates a new MCP9808 class
*/
/**************************************************************************/
Adafruit_MCP9808::Adafruit_MCP9808() {
}

/**************************************************************************/
/*! 
    @brief  Setups the HW
*/
/**************************************************************************/
bool Adafruit_MCP9808::begin(int sda, int scl, uint8_t addr) {

  _i2caddr = addr;
  Wire.begin(sda, scl);
  
  if (read16(MCP9808_REG_MANUF_ID) != 0x0054) return false;
  
  if (read16(MCP9808_REG_DEVICE_ID) != 0x0400) return false;

  write16(MCP9808_REG_CONFIG, 0x0);

  return true;
}
 
/**************************************************************************/
/*! 
    @brief  Reads the 16-bit temperature register and returns the Centigrade
            temperature as a float.

*/
/**************************************************************************/
float Adafruit_MCP9808::readTempC( void )
{
  uint16_t t = read16(MCP9808_REG_AMBIENT_TEMP);

  float temp = t & 0x0FFF;
  temp /=  16.0;
  if (t & 0x1000) temp -= 256;

  return temp;
}



//*************************************************************************
// Set Sensor to Shutdown-State or wake up (Conf_Register BIT8)
// 1= shutdown / 0= wake up
//*************************************************************************

void Adafruit_MCP9808::shutdown_wake( uint8_t sw_ID )
{
    uint16_t conf_shutdown ;
    uint16_t conf_register = read16(MCP9808_REG_CONFIG);
    if (sw_ID == 1)
    {
       conf_shutdown = conf_register | MCP9808_REG_CONFIG_SHUTDOWN ;
       write16(MCP9808_REG_CONFIG, conf_shutdown);
    }
    if (sw_ID == 0)
    {
       conf_shutdown = conf_register & ~MCP9808_REG_CONFIG_SHUTDOWN ;
       write16(MCP9808_REG_CONFIG, conf_shutdown);
    }
}

void Adafruit_MCP9808::shutdown(void)
{
  shutdown_wake(1);
}

void Adafruit_MCP9808::wake(void)
{
  shutdown_wake(0);
//  delay(250);
}



/**************************************************************************/
/*! 
    @brief  Low level 16 bit read and write procedures!
*/
/**************************************************************************/

void Adafruit_MCP9808::write16(uint8_t reg, uint16_t value) {
    Wire.beginTransmission(_i2caddr);
    Wire.write((uint8_t)reg);
    Wire.write(value >> 8);
    Wire.write(value & 0xFF);
    Wire.endTransmission();
}

uint16_t Adafruit_MCP9808::read16(uint8_t reg) {
  uint16_t val;

  Wire.beginTransmission(_i2caddr);
  Wire.write((uint8_t)reg);
  Wire.endTransmission();
  
  Wire.requestFrom((uint8_t)_i2caddr, (uint8_t)2);
  val = Wire.read();
  val <<= 8;
  val |= Wire.read();  
  return val;  
}
