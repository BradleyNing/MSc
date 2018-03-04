#include "contiki.h"

#include <stdio.h> /* For printf() */
//#include "dev/light-sensor.h"
#include "dev/sht11-sensor.h"
static process_event_t event_data_ready;
static float At=0;


unsigned short d1(float f) // Integer part
{
  return((unsigned short)f);
}
unsigned short d2(float f) // Fractional part
{
  return(1000*(f-d1(f)));
}

/*---------------------------------------------------------------------------*/
PROCESS(Average, "Average process");
PROCESS(Print, "Print process");
AUTOSTART_PROCESSES(&Average, &Print);
/*---------------------------------------------------------------------------*/

PROCESS_THREAD(Average, ev, data)
{
  static struct etimer timer;
  static unsigned counter=0;

  PROCESS_BEGIN();

  printf("Average process started\n");

  etimer_set(&timer, CLOCK_CONF_SECOND/4);
//  SENSORS_ACTIVATE(light_sensor);  
  SENSORS_ACTIVATE(sht11_sensor);
  event_data_ready = process_alloc_event();

  while(1)
  {
    PROCESS_WAIT_EVENT_UNTIL(ev=PROCESS_EVENT_TIMER);

    float temp = 0.01*sht11_sensor.value(SHT11_SENSOR_TEMP)-39.6;
    At = At+temp;
    counter++;
    if((counter%4) == 0)
    {
    At=At/4;
    counter=0;
    process_post(&Print, event_data_ready, &At);
    printf("Averaged temperature1:%u.%03u C\n", d1(At), d2(At));
    
    At = 0;
     }

//    printf("%u.%03u C\n", d1(temp), d2(temp));
//    printf("%u.%03u lux\n", d1(light_lx), d2(light_lx));

    etimer_reset(&timer);
   }
  PROCESS_END();
}

PROCESS_THREAD(Print, ev, data)
{
  PROCESS_BEGIN();

  printf("Print process started\n");

  while(1)
  {
    PROCESS_WAIT_EVENT_UNTIL(ev == event_data_ready);
    printf("Averaged temperature2:%u.%03u C\n", d1(*(float *)data), d2(*(float *)data));
   }
  PROCESS_END();
}
