/* Assignment 1, Name: Bradley Ning Zili, URN: 6455442 */
/* As1-cal-pwr.h  */
#include "dev/light-sensor.h"

#define STATE_NORMAL	0
#define STATE_ALARM		1

#define MODE_CALIBRATE	0
#define MODE_PWRTRACE	1
#define MODE_WAIT		2

#define TEMP_THRESHOLD	1.2
#define LIGHT_THRESHOLD 1.4

static process_event_t EVENT_FIRE_ALARM;

struct T_Alarm{
	float 	temperature;
	float 	light;
	int		state;
};

static float 	g_t_calibrate = 21.0;     // initial temperature 
static float 	g_l_calibrate = 300.0;    // initial light
static float	g_sample_freq = 16;		  // initial sample frequence, one time per 16 seconds

unsigned short 	d1(float);
unsigned short 	d2(float);
float GetLight();

unsigned short d1(float f) // Integer part
{
  return((unsigned short)f);
}

unsigned short d2(float f) // Fractional part
{
  return(1000*(f-d1(f)));
}

float GetLight()
{
	float V_sensor, I, light_lx;
	
	V_sensor = 1.5 * light_sensor.value(LIGHT_SENSOR_PHOTOSYNTHETIC)/4096.0;
	I = V_sensor/100000.0;
	light_lx = 0.625*1e6*I*1000.0;
	return light_lx;
}


