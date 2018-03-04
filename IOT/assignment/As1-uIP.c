/* Assignment 1, Name: Bradley Ning Zili, URN: 6455442 */
/* As1-uIP.c  for client */
/* Assignment 1 - Check, Alarm with uIP client processes. */
/* There is another file of Check, Alarm uIP process, as it looks too big */
/* for all functions fitting into one task for XM1000 */
    
#include "contiki.h"
#include "contiki-net.h"
#include "dev/light-sensor.h"
#include "dev/sht11-sensor.h"
#include "dev/leds.h"

#include "As1-uIP.h"

PROCESS(Check, "Check temprature and light");
PROCESS(Alarm, "Local alarm and interact with the server");

AUTOSTART_PROCESSES(&Check, &Alarm);

PROCESS_THREAD(Check, ev, data)
{
	static struct etimer 	timer;
	static struct T_Alarm   s_AlarmData;   //s_: static variables
	static int 				s_calibrate_flag, s_counter;
	static float			s_temp, s_light;
	float 					temp, light;
  	
	PROCESS_BEGIN();
	
	s_temp  = 0;
	s_light = 0;
	s_calibrate_flag = 0;
	s_counter = 0;

	SENSORS_ACTIVATE(light_sensor);  
  	SENSORS_ACTIVATE(sht11_sensor);

	etimer_set(&timer, CLOCK_CONF_SECOND);
  	EVENT_FIRE_ALARM = process_alloc_event();
	printf("Check process will calibrate for 10s at the begining ... \n");

  	while(1)
  	{
		PROCESS_WAIT_EVENT();
		if(ev == PROCESS_EVENT_TIMER)
		{
			if(s_calibrate_flag == 0)   // after calibrated, the flag will be 1
			{
				temp = 0.01*sht11_sensor.value(SHT11_SENSOR_TEMP)-39.6;
				light = GetLight();

				s_temp += temp;
				s_light += light;			
				s_counter++;

				//printf("No.%u calibrating: ", s_counter);
				//printf("Temperature: %u.%03uC", d1(temp), d2(temp));
				//printf(", Light: %u.%03ulux\n", d1(light), d2(light));
				if(s_counter==10)
				{
					g_t_calibrate = s_temp/10.0;
					g_l_calibrate = s_light/10.0;
					s_calibrate_flag = 1;

					//printf("\nCalibrated result, ");
					//printf("Temperature: %u.%03uC", d1(g_t_calibrate), d2(g_t_calibrate));
					//printf(", Light: %u.%03ulux\n", d1(g_l_calibrate), d2(g_l_calibrate));

					//printf("\nCalibrated alert threshold: ");
					//printf("Temperature > %u.%03uC", d1(g_t_calibrate*TEMP_THRESHOLD), d2(g_t_calibrate*TEMP_THRESHOLD));
					//printf(" or Light > %u.%03ulux\n", d1(g_l_calibrate*LIGHT_THRESHOLD), d2(g_l_calibrate*LIGHT_THRESHOLD));
				}
				etimer_reset(&timer);
			}
			else
			{
				temp = 0.01*sht11_sensor.value(SHT11_SENSOR_TEMP)-39.6;
				light = GetLight();			
				if((temp > (g_t_calibrate*TEMP_THRESHOLD)) || (light > (g_l_calibrate*LIGHT_THRESHOLD)))
				{ // g_ : global variables, alert threshold = calibrated value * a threhold ratio
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
				etimer_reset(&timer);
			}
		}	
	}
	PROCESS_END();
}

PROCESS_THREAD(Alarm, ev, data)
{
	static int 				s_alarm_status, s_alarm_counter;
	static int		    	s_action_status, s_send_counter=0;
	static struct etimer 	link_check_timer;

	struct T_Alarm			*pAlarmData;
	float 					temperature, light;
  	uip_ipaddr_t 		 	ipaddr;
	char 				 	*str;


	PROCESS_BEGIN();  	

	leds_init();
  	leds_off(LEDS_ALL);  
	leds_on(LEDS_GREEN);  // in normal state, switch on green light

	s_alarm_status  = STATE_NORMAL;
	s_action_status = ACTION_NORMAL;

	s_alarm_counter = 0;   
	s_send_counter  = 0;   // data send to server counter
// set and print IP address  
	set_ip_address();
	print_ip_address();	
  
//	set_server_address and bind 
	uip_ip6addr(&ipaddr,0xfe80,0,0,0,0x0212,0x7400,0x13cb,0x05a9);

  	g_client_conn = udp_new(&ipaddr, UIP_HTONS(3000), NULL);  //setup connection
  	if (g_client_conn == NULL)
		printf("client_conn new error !!!!!!!!!!!!!!!!!!!!!!\n"); 

  	udp_bind(g_client_conn, UIP_HTONS(3001));
  
  	PRINTF("Created a connection with server ");
  	PRINT6ADDR(&g_client_conn->ripaddr);
  	PRINTF(" local/remote port %u/%u\n", UIP_HTONS(g_client_conn->lport), UIP_HTONS(g_client_conn->rport));
	
	while(1)
	{
		PROCESS_WAIT_EVENT();
		if(ev == EVENT_FIRE_ALARM)  // receive event from the Check process
		{
			pAlarmData=(struct T_Alarm *)data;
			if(pAlarmData->state == STATE_ALARM)   // temp or light above the alert threshold 
			{
				//leds_off(LEDS_ALL);	
				leds_off(LEDS_GREEN);
				leds_blink();
				//leds_on(LEDS_BLUE);    
				temperature = pAlarmData->temperature;
				light = pAlarmData->light;
				s_alarm_status = STATE_ALARM;
				s_alarm_counter++;	

				printf("\n# %u Alarm!!!\n", s_alarm_counter);
				printf("Temperature: %u.%03uC", d1(temperature), d2(temperature));
				printf(", Light: %u.%03ulux\n", d1(light), d2(light));
				// send to server
				SendtoServer(STATE_ALARM);				
			}
			else   //temperature or light back to normal 
			{
				leds_on(LEDS_GREEN);
				printf("\nBack to normal state, alarm cancelled\n");
				temperature = pAlarmData->temperature;
				light = pAlarmData->light;
				printf("Temperature: %u.%03uC", d1(temperature), d2(temperature));
				printf(", Light: %u.%03ulux\n", d1(light), d2(light));
				s_alarm_status = STATE_NORMAL;
				// send to server
				SendtoServer(STATE_NORMAL);
			}
			etimer_set(&link_check_timer, CLOCK_CONF_SECOND*2);
		}
		if(ev == tcpip_event)  //get command from the server
		{
		 	if(uip_newdata()) 
			{
				str = uip_appdata;
				str[uip_datalen()] = '\0';
				printf("Command from the server: %s\n", str);
				if(strcmp(str, "ACTION_ALARM") == 0)     
				{ //send string from the server rather than concised numbers just for demo
					s_action_status = ACTION_ALARM;
					leds_on(LEDS_RED);    // if get ACTION_ALARM from the server, switch on RED led
				}
				else   
				{
					s_action_status = ACTION_NORMAL;
					leds_off(LEDS_RED);
				}				
			}
		}
		if(ev == PROCESS_EVENT_TIMER)   
        //link check timer, in case msg lost between the client and server result in state confustion
		{
			if( (s_alarm_status == STATE_ALARM) && (s_action_status == ACTION_NORMAL) )
			{  // means the client is alarming, while sever not send action command or server may lost the alarm notic
				SendtoServer(STATE_ALARM);	
				etimer_set(&link_check_timer, CLOCK_CONF_SECOND*2);
			}
			if(	(s_alarm_status == STATE_NORMAL) && (s_action_status == ACTION_ALARM) )
			{  //means the client is back to normal, while it still in ACTION_ALARM state which command by the server
				SendtoServer(STATE_NORMAL);	
				etimer_set(&link_check_timer, CLOCK_CONF_SECOND*2);
			}
		}
	}
	PROCESS_END();
}



