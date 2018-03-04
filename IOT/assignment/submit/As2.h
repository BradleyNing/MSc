/* Assignment 2, Name: Bradley Ning Zili, URN: 6455442 */
/* As2.h  */
#include <stdio.h>
#include "contiki.h"
#include "dev/light-sensor.h"

#define DEV_AGGREGATE_ALL	0
#define DEV_AGGREGATE_6		(15*15)
#define DEV_AGGREGATE_4		(22*22)
#define DEV_AGGREGATE_2		(29*29)

#define BUF_LEN				12
#define THRESHOLD_LEVEL 	1.5

struct T_Data_Buf{
float 		data[BUF_LEN];
unsigned 	wait_counter;
};
;
static struct T_Data_Buf 	g_m_buf;  //g_:globle variables, m: measurement buf;
static float 				g_Weighted_Average;
static int					g_counter=0;

unsigned short 	d1(float);
unsigned short 	d2(float);
void			BufInit();
float			GetLight();
float 			GetWightedAverage();
void 			UpdateMeasureBuf(float);
float 			Get_sigma();
void 			Aggregate(int); 
void			Treshold_alert(float);
void			Data_send(float);

unsigned short d1(float f) // Integer part
{
  return((unsigned short)f);
}

unsigned short d2(float f) // Fractional part
{
  return(1000*(f-d1(f)));
}

void BufInit()
{
	int i;
	for(i=0; i<BUF_LEN; i++) 
		g_m_buf.data[i]=GetLight();

	g_m_buf.wait_counter = 0;	
}

float GetLight()
{
	float V_sensor, I, light_lx;
	
	V_sensor = 1.5 * light_sensor.value(LIGHT_SENSOR_PHOTOSYNTHETIC)/4096.0;
	I = V_sensor/100000.0;
	light_lx = 0.625*1e6*I*1000.0;
	return light_lx;
}

float GetWightedAverage()
{
	float denominator=0, sum=0;
	int i;
	
	for(i=0; i< BUF_LEN; i++)
	{
		denominator = denominator+i+1;   //Y = (1*X[0]+2*X[1]+...+N*X[N-1])/(1+...+N)
		sum = sum+(i+1)*g_m_buf.data[i];
	}
	g_Weighted_Average = sum/denominator;
	return g_Weighted_Average;
}

void Treshold_alert(float v_light)
{
	printf("Alert output, Light is above THRESHOLD * Weighted Average! It's value: %u.%03u\n", d1(v_light), d2(v_light));
	printf("Thereshold Ratio: %u.%03u\n", d1(THRESHOLD_LEVEL), d2(THRESHOLD_LEVEL));
	printf("The weighted average: %u.%03u\n", d1(g_Weighted_Average), d2(g_Weighted_Average));
	printf("Alert thereshold: %u.%03u\n", d1(THRESHOLD_LEVEL*g_Weighted_Average), d2(THRESHOLD_LEVEL*g_Weighted_Average));
    //In the real situation will send the data, here just print;
}

/*Add the new measured value to the end of the buf*/
void UpdateMeasureBuf(float v_light)
{
	int i;

	for(i=1; i<BUF_LEN; i++)
		g_m_buf.data[i-1]=g_m_buf.data[i];

	g_m_buf.data[BUF_LEN-1] = v_light;
}

float Get_sigma()
{
	float sum=0, average=0, sigma_pwr2=0;
	int i;

	for(i=0; i<BUF_LEN; i++)
		sum = sum + g_m_buf.data[i];
	average = sum/BUF_LEN;

	sum = 0;
	for(i=0; i<BUF_LEN; i++)
		sum = sum + (g_m_buf.data[i]-average)*(g_m_buf.data[i]-average);
	
	sigma_pwr2 = sum/BUF_LEN;  //divided by n according to our lectures, can use n-1 as well if needed
//	sigma = sqrt(sigma_pwr2);   
	return sigma_pwr2;			//as difficult to get sqrt function, so use sigma*sigma;
}

/* according to the agg_mode, excute different aggeration */
void Aggregate(int agg_mode)
{ 
	float send_value;
	int	  i=0, waitings, j;
	
	waitings = g_m_buf.wait_counter;
	switch(agg_mode)
	{	
		case DEV_AGGREGATE_2:
			for (i=0; i<waitings/2; i++)	
			{		
				send_value = (g_m_buf.data[BUF_LEN-waitings+i*2]+g_m_buf.data[BUF_LEN-waitings+i*2+1])/2.0;
				printf("Aggregate2, Output: %u.%03u\n", d1(send_value), d2(send_value));
				g_m_buf.wait_counter = waitings - 2*(waitings/2);
			}
			break;
		
		case DEV_AGGREGATE_4:
			for (i=0; i<waitings/4; i++)	
			{	
				send_value = 0;	
				for (j=0; j<4; j++)
					send_value = send_value + g_m_buf.data[BUF_LEN-waitings+i*4+j];
				send_value = send_value/4.0;
				printf("Aggregate4, Output: %u.%03u\n", d1(send_value), d2(send_value));
				g_m_buf.wait_counter = waitings - 4*(waitings/4);
			}
			break;

		case DEV_AGGREGATE_6:
			for (i=0; i<waitings/6; i++)	
			{	
				send_value = 0;	
				for (j=0; j<6; j++)
					send_value = send_value + g_m_buf.data[BUF_LEN-waitings+i*6+j];
				send_value = send_value/6.0;
				printf("Aggregate6, Output: %u.%03u\n", d1(send_value), d2(send_value));
				g_m_buf.wait_counter = waitings - 6*(waitings/6);
			}
			break;

		case DEV_AGGREGATE_ALL:
			for(i=0; i<waitings/12; i++) 
 			{
				send_value = 0;	
				for (j=0; j<12; j++)
					send_value = send_value + g_m_buf.data[BUF_LEN-waitings+i*12+j];
				send_value = send_value/12.0;
				printf("Aggregate12, Output: %u.%03u\n", d1(send_value), d2(send_value));
				g_m_buf.wait_counter = waitings - 12*(waitings/12);				
			}
			break;
			
		default:
			printf("Error in Aggregate\n"); // only print for debug;
			// other error management
	}
}
 

