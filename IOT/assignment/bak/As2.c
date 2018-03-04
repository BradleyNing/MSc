#include <stdio.h>
#include "contiki.h"
#include "dev/light-sensor.h"
#include "As2.h"

PROCESS(As2, "Assignment2: Aggregation");
AUTOSTART_PROCESSES(&As2);

PROCESS_THREAD(As2, ev, data)
{
	static struct etimer 	v_timer;
	float 					light, sigma, WeightedAverage;

	PROCESS_BEGIN();
	etimer_set(&v_timer, CLOCK_SECOND);
	SENSORS_ACTIVATE(light_sensor);
	BufInit();
	
	while(1)
	{
		PROCESS_WAIT_EVENT();
		if (ev == PROCESS_EVENT_TIMER)
		{
			light = GetLight();
			WeightedAverage = GetWightedAverage();  // if the weighted average is too big will trigger an alert
			if(light > WeightedAverage*THRESHOLD_LEVEL)		
			{  
				Treshold_alert(light);   // if the value is too big will trigger an alert
				UpdateMeasureBuf(light); // insert the new measure to the buffer;
				g_m_buf.DataLen = 0;  // no need to send the old data, while keep it for weighted average
				etimer_reset(&v_timer);					
			}				
			else
			{
				UpdateMeasureBuf(light); // insert the new measure to the buffer
				if(g_m_buf.DataLen == BUF_LEN)
				{
					sigma = Get_sigma();  
					// according to sigma, select aggregate per 2/4/6 numbers into one number
					if(sigma > DEV_AGGREGATE_2)	 		Aggregate(DEV_AGGREGATE_2);  
					else if(sigma > DEV_AGGREGATE_4) 	Aggregate(DEV_AGGREGATE_4); 
					else if(sigma > DEV_AGGREGATE_6) 	Aggregate(DEV_AGGREGATE_6);  
					else 							 	Aggregate(DEV_AGGREGATE_ALL);   
			
					Data_send(sigma);   
					etimer_reset(&v_timer);
				}
				else
					etimer_reset(&v_timer);
			}
		}
	}
	PROCESS_END();
}



