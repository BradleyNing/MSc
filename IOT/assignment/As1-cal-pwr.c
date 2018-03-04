/* Assignment 1, Name: Bradley Ning Zili, URN: 6455442 */
/* As1-cal-pwr.c  */
/* Assignment 1 - Check, Alarm, Calibrate, Powertrace processes. */
/* There is another file of Check, Alarm uIP process, as it looks too big */
/* for all functions fitting into one task for XM1000 */
#include <stdio.h>
#include "contiki.h"
#include "dev/light-sensor.h"
#include "dev/sht11-sensor.h"
#include "dev/button-sensor.h"
#include "dev/leds.h"
#include "powertrace.h"
#include "As1-cal-pwr.h"

PROCESS(Check, "Check temprature and light");
PROCESS(Alarm, "Local alam and interact with the server");
PROCESS(Calibrate, "Calibrating");
PROCESS(Power, "Power trace ...");

//AUTOSTART_PROCESSES(&Check, &Alarm, &Calibrate);
AUTOSTART_PROCESSES(&Check, &Alarm, &Calibrate, &Power);

PROCESS_THREAD(Check, ev, data)
{
	static struct etimer 	timer;
	static struct T_Alarm   s_AlarmData;
	float 					temp, light;
  	
	PROCESS_BEGIN();

	SENSORS_ACTIVATE(light_sensor);  
  	SENSORS_ACTIVATE(sht11_sensor);

	etimer_set(&timer, CLOCK_CONF_SECOND);
  	EVENT_FIRE_ALARM = process_alloc_event();
  	while(1)
  	{
		PROCESS_WAIT_EVENT();
		if(ev == PROCESS_EVENT_TIMER)
		{
			temp = 0.01*sht11_sensor.value(SHT11_SENSOR_TEMP)-39.6;
			light = GetLight();			
			if((temp > (g_t_calibrate*TEMP_THRESHOLD)) || (light > (g_l_calibrate*LIGHT_THRESHOLD)))
			{
				s_AlarmData.temperature = temp;
				s_AlarmData.light = light;	
				s_AlarmData.state = STATE_ALARM;			
				process_post(&Alarm, EVENT_FIRE_ALARM, &s_AlarmData);
			}
			else if(s_AlarmData.state == STATE_ALARM)
			{
				s_AlarmData.state = STATE_NORMAL;
				s_AlarmData.temperature = temp;
				s_AlarmData.light = light;	
				process_post(&Alarm, EVENT_FIRE_ALARM, &s_AlarmData);				
			}
			//etimer_set(&timer, CLOCK_CONF_SECOND);
			etimer_set(&timer, CLOCK_CONF_SECOND*g_sample_freq);  //will change sample frequence when running
		}	
	}
	PROCESS_END();
}

PROCESS_THREAD(Alarm, ev, data)
{
	static int 			s_alarm_status, s_alarm_counter;
	struct T_Alarm* 	pAlarmData;
	float 				temperature, light;

	PROCESS_BEGIN();  	

	leds_init();
  	leds_off(LEDS_ALL);  
	leds_on(LEDS_GREEN);

	s_alarm_status = STATE_NORMAL;

	s_alarm_counter = 0;

	while(1)
	{
		PROCESS_WAIT_EVENT();
		if(ev == EVENT_FIRE_ALARM)  // receive event from the check process
		{
			pAlarmData=(struct T_Alarm *)data;
			if(pAlarmData->state == STATE_ALARM)   // temperature or light above the alert threshold 
			{
				s_alarm_counter++;	
				leds_off(LEDS_GREEN);	
				leds_blink();
				temperature = pAlarmData->temperature;
				light = pAlarmData->light;

				printf("\n# %u Alarm!!!\n", s_alarm_counter);
				printf("Temperature: %u.%03uC", d1(temperature), d2(temperature));
				printf(", Light: %u.%03ulux\n", d1(light), d2(light));
				s_alarm_status = STATE_ALARM;
				//SendtoServer(STATE_ALARM);
			}
			else   //temperatue and light back to normal 
			{
				leds_on(LEDS_GREEN);
				printf("\nBack to normal state, alarm cancelled\n");
				temperature = pAlarmData->temperature;
				light = pAlarmData->light;
				printf("Temperature: %u.%03uC", d1(temperature), d2(temperature));
				printf(", Light: %u.%03ulux\n", d1(light), d2(light));
				s_alarm_status = STATE_NORMAL;
				//SendtoServer(STATE_NORMAL);
			}
		}
	}
	PROCESS_END();
}

PROCESS_THREAD(Calibrate, ev, data)
{
	static struct etimer timer;

	static float s_temp=0, s_light=0;
	static int 	 s_counter=0;
	static int   s_cal_pwr_mode;
	float 		 temp, light;

	PROCESS_BEGIN();
	printf("\nIf you want to calibrate or change the sample freq, please press button\n");

	printf("\nDefault calibrating result, ");
	printf("Temperature: %u.%03uC", d1(g_t_calibrate), d2(g_t_calibrate));
	printf(", Light: %u.%03ulux\n", d1(g_l_calibrate), d2(g_l_calibrate));

	printf("\nDefault alert threshold: ");
	printf("Temperature > %u.%03uC", d1(g_t_calibrate*TEMP_THRESHOLD), d2(g_t_calibrate*TEMP_THRESHOLD));
	printf(" or Light > %u.%03ulux\n", d1(g_l_calibrate*LIGHT_THRESHOLD), d2(g_l_calibrate*LIGHT_THRESHOLD));

	printf("default sample freq is one sample per %u.%03u seconds\n", d1(g_sample_freq), d2(g_sample_freq));

	SENSORS_ACTIVATE(light_sensor);  
  	SENSORS_ACTIVATE(sht11_sensor);
	SENSORS_ACTIVATE(button_sensor);
	s_cal_pwr_mode = MODE_CALIBRATE;
	//as button is co-used by the calibrating and changing the sample frequence, so add this flag
	while(1)
	{
		PROCESS_WAIT_EVENT();
		if( (ev==sensors_event) && (data==&button_sensor) && (s_cal_pwr_mode==MODE_CALIBRATE) )
		{ 
			printf("\nButton pressed, begin to recalibrate!!!\n");
			s_counter = 0;
			s_temp    = 0;
			s_light   = 0;
			s_cal_pwr_mode = MODE_WAIT;  // after calibrating will change the flag to allow sample frequence change
			etimer_set(&timer, CLOCK_CONF_SECOND);
		}

		if(ev == PROCESS_EVENT_TIMER)
		{
			temp = 0.01*sht11_sensor.value(SHT11_SENSOR_TEMP)-39.6;
			light = GetLight();

			s_temp += temp;
			s_light += light;			
			s_counter++;

			printf("No.%u calibrating: ", s_counter);
			printf("Temperature: %u.%03uC", d1(temp), d2(temp));
			printf(", Light: %u.%03ulux\n", d1(light), d2(light));
			if(s_counter==10)
			{
				g_t_calibrate = s_temp/10.0;
				g_l_calibrate = s_light/10.0;
				s_cal_pwr_mode = MODE_PWRTRACE;

				printf("\nCalibrated result, ");
				printf("Temperature: %u.%03uC", d1(g_t_calibrate), d2(g_t_calibrate));
				printf(", Light: %u.%03ulux\n", d1(g_l_calibrate), d2(g_l_calibrate));

				printf("\nCalibrated alert threshold: ");
				printf("Temperature > %u.%03uC", d1(g_t_calibrate*TEMP_THRESHOLD), d2(g_t_calibrate*TEMP_THRESHOLD));
				printf(" or Light > %u.%03ulux\n", d1(g_l_calibrate*LIGHT_THRESHOLD), d2(g_l_calibrate*LIGHT_THRESHOLD));
			}
			if(s_counter < 10)
				etimer_reset(&timer);
		}
		if( (ev==sensors_event) && (data==&button_sensor) && (s_cal_pwr_mode==MODE_PWRTRACE) )	
		{
			printf("Button pressed, will change the sample freq ...\n");
			printf("Current sample freq is one sample per %u.%03u seconds\n", d1(g_sample_freq), d2(g_sample_freq));
			g_sample_freq = g_sample_freq/2.0;
			//every button will sample the sensor data two times quickly
			s_cal_pwr_mode = MODE_CALIBRATE;
			// to share the button, calibrating and changing sample frequence are interwaved 
			printf("I has been changed to one sample per %u.%03u seconds\n", d1(g_sample_freq), d2(g_sample_freq));
		}	
	}
	PROCESS_END();
}

PROCESS_THREAD(Power, ev, data)
{
	static struct etimer 	et;
	static unsigned 		s_pwr_seq=0;
	PROCESS_BEGIN();

	/* Start powertracing */
	unsigned n = 8; // 8 second reporting cycle
	powertrace_start(CLOCK_SECOND * n);
	printf("Ticks per second: %u\n", RTIMER_SECOND);
	printf("Output power trace per %d seconds, total %d ticks per power cycle\n", n, n*RTIMER_SECOND);
  	
	etimer_set(&et, CLOCK_CONF_SECOND*n); // output power trace per 8 seconds

	while(1) 
	{
		PROCESS_WAIT_EVENT();
		if(ev==PROCESS_EVENT_TIMER)
		{	
			s_pwr_seq++;
			printf("# %u power trace, one trace per %u seconds, one sample per %u.%03u seconds\n", s_pwr_seq, n, d1(g_sample_freq), d2(g_sample_freq));
			etimer_reset(&et);
		}
	}
	PROCESS_END();
}

