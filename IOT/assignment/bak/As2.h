#include <stdio.h>
//#include <math.h>
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
unsigned 	DataLen;
unsigned	Sigma;
};

static struct T_Data_Buf 	g_m_buf, g_s_buf;  //g_:globle variables, m: measurement buf, s: data for send buf;
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
	{
		g_m_buf.data[i]=GetLight();
		g_s_buf.data[i]=0.0;
	}
	g_m_buf.DataLen = 1;	
	g_s_buf.DataLen = 0;
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
	printf("Alert!!! Light is above THRESHOLD of weighted average! It's value: %u.%03u\n", d1(v_light), d2(v_light));
	printf("Thereshold level: %u.%03u\n", d1(THRESHOLD_LEVEL), d2(THRESHOLD_LEVEL));
	printf("The weighted average: %u.%03u\n", d1(g_Weighted_Average), d2(g_Weighted_Average));
//In the real situation will send the data, here just print;
}

void UpdateMeasureBuf(float v_light)
{
	int i;
	if(g_m_buf.DataLen < BUF_LEN)
	{
		g_m_buf.data[g_m_buf.DataLen] = v_light;
		g_m_buf.DataLen++;
		if(g_m_buf.DataLen > BUF_LEN)   
			printf("Buffer Error\n");   //for debug, as it should less than BUF_LEN;
	}
	else
	{
		for(i=1; i<BUF_LEN; i++)
			g_m_buf.data[i-1]=g_m_buf.data[i];
		g_m_buf.data[BUF_LEN-1] = v_light;
	}
}

float Get_sigma()
{
	float sum=0, average=0, sigma=0;
	int i;

	for(i=0; i<BUF_LEN; i++)
		sum = sum + g_m_buf.data[i];
	average = sum/BUF_LEN;

	sum = 0;
	for(i=0; i<BUF_LEN; i++)
		sum = sum + (g_m_buf.data[i]-average)*(g_m_buf.data[i]-average);
	
	average = sum/BUF_LEN;  //divided by n according to our lectures, can use n-1 as well if needed
	sigma = average;
//	sigma = sqrt(average);   //as difficult to get sqrt function, so use sigma*sigma;
	return sigma;
}

/* according to the agg_mode, save the aggregated data into the send buffer */
void Aggregate(int agg_mode)
{ 
	float sum=0, average=0;
	int	  i;
	
	switch(agg_mode)
	{	
		case DEV_AGGREGATE_ALL:
			for(i=0; i<BUF_LEN; i++)  sum += g_m_buf.data[i];
			
			g_m_buf.DataLen = 0;

			average = sum/BUF_LEN;
			g_s_buf.data[0] = average;
			g_s_buf.DataLen = 1;
			break;

		case DEV_AGGREGATE_6:
			for(i=0; i<BUF_LEN/2; i++)  // BUF_LEN = 12 in this case, and can't be an odd number
				sum += g_m_buf.data[i];
			average=sum/(BUF_LEN/2);
			g_s_buf.data[0]=average;
			
			sum=0;
			average=0;
			for(i=BUF_LEN/2; i<BUF_LEN; i++)  
				sum += g_m_buf.data[i];

			g_m_buf.DataLen = 0;

			average=sum/(BUF_LEN/2);
			g_s_buf.data[1]=average;

			g_s_buf.DataLen = 2;
			break;

		case DEV_AGGREGATE_4: //As BUF_LEN=12, simplify code like this rather than use BUF_LEN as variable
			for(i=0; i<3; i++)
				g_s_buf.data[i] = (g_m_buf.data[i]+g_m_buf.data[i+1]+g_m_buf.data[i+2]+g_m_buf.data[i+3])/4; 

			g_m_buf.DataLen = 0;
			g_s_buf.DataLen = 3;
			break;

		case DEV_AGGREGATE_2:  //As BUF_LEN=12, simplify code like this
			for(i=0; i<6; i++)
				g_s_buf.data[i] = (g_m_buf.data[i]+g_m_buf.data[i+1])/2;

			g_m_buf.DataLen = 0;
			g_s_buf.DataLen = 6;
			break;

		default:
			printf("Error in Aggregate\n"); // only print for debug;
			// other error management
	}
}
 
//send out the data, print for debug
void Data_send(float sigma)
{
	int i;
	g_counter++;
	printf("\n#%d, The data to be sent: ", g_counter);	

	for(i=0; i<g_s_buf.DataLen; i++)
		printf(" %u.%03u ", d1(g_s_buf.data[i]), d2(g_s_buf.data[i]));  //send out the aggregated data;
	
	printf("\n");
	printf("Sigma*Sigma of the Data: %u.%03u\n", d1(sigma), d2(sigma));	//for debug;

//	printf("The raw Data: ");
//	for(i=0; i<BUF_LEN; i++)
//		printf(" %u.%03u ", d1(g_m_buf.data[i]), d2(g_m_buf.data[i]));  //for debug;
	
	g_s_buf.DataLen = 0;	

}


