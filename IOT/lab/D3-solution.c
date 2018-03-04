#include "contiki.h"
#include "dev/light-sensor.h"
#include "dev/sht11-sensor.h"
#include <stdio.h> /* For printf() */

unsigned short d1(float f) // Integer part
{
  return((unsigned short)f);
}
unsigned short d2(float f) // Fractional part
{
  return(1000*(f-d1(f)));
}

/*---------------------------------------------------------------------------*/
PROCESS(sensor_reading_process, "Sensor reading process");
AUTOSTART_PROCESSES(&sensor_reading_process);
/*---------------------------------------------------------------------------*/
PROCESS_THREAD(sensor_reading_process, ev, data)
{
  static struct etimer timer;
  PROCESS_BEGIN();
  etimer_set(&timer, CLOCK_CONF_SECOND/4);
  SENSORS_ACTIVATE(light_sensor);  
  SENSORS_ACTIVATE(sht11_sensor);
  while(1) 
  {
    PROCESS_WAIT_EVENT_UNTIL(ev=PROCESS_EVENT_TIMER);

    float temp = 0.01*sht11_sensor.value(SHT11_SENSOR_TEMP)-39.6;

    float V_sensor = 1.5 * light_sensor.value(LIGHT_SENSOR_PHOTOSYNTHETIC)/4096;
    float I = V_sensor/100000;
    float light_lx = 0.625*1e6*I*1000;

    printf("%u.%03u C\n", d1(temp), d2(temp));
    printf("%u.%03u lux\n", d1(light_lx), d2(light_lx));

    etimer_reset(&timer);
  }
  PROCESS_END();
}
/*---------------------------------------------------------------------------*/