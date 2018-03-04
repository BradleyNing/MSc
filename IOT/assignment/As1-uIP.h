#include <string.h>

#define DEBUG DEBUG_PRINT
#include "net/uip-debug.h"
#include "dev/light-sensor.h"

#define STATE_NORMAL	0   // flag for client's local alarm or not status
#define STATE_ALARM		1

#define	ACTION_NORMAL	0    // flag for in what state commmanded by the server
#define	ACTION_ALARM	1

#define TEMP_THRESHOLD	1.2  // this ratio * calibrated value = alert threthold
#define LIGHT_THRESHOLD 1.4
#define SEND_BUF_LEN	15     // data buf for communication between server and client, 1 byte is enough, 
// while to make it more readable for a demo, so will use a string to interact with server

static process_event_t EVENT_FIRE_ALARM;

struct T_Alarm{
	float 	temperature;
	float 	light;
	int		state;
};

static float 				       g_t_calibrate = 21.0;
static float 				       g_l_calibrate = 300.0;
static struct uip_udp_conn *g_client_conn;
static char     		       g_send_buf[SEND_BUF_LEN];
static int 					       g_alarm_seq=0, g_alarm_cancel_seq=0;

static unsigned short 	d1(float);
static unsigned short 	d2(float);
static float 			      GetLight(void);
static void 			      set_ip_address(void);
static void  			      print_ip_address(void);	
static void 			      SendtoServer(int);

static unsigned short d1(float f) // Integer part
{
  return((unsigned short)f);
}

static unsigned short d2(float f) // Fractional part
{
  return(1000*(f-d1(f)));
}

static float GetLight(void)
{
	float V_sensor, I, light_lx;
	
	V_sensor = 1.5 * light_sensor.value(LIGHT_SENSOR_PHOTOSYNTHETIC)/4096.0;
	I = V_sensor/100000.0;
	light_lx = 0.625*1e6*I*1000.0;
	return light_lx;
}

static void print_ip_address(void)
{
  int i;
  uint8_t state;

  PRINTF("My IPv6 addresses: ");
  for(i = 0; i < UIP_DS6_ADDR_NB; i++) 
  {
    state = uip_ds6_if.addr_list[i].state;
    if(uip_ds6_if.addr_list[i].isused && (state == ADDR_TENTATIVE || state == ADDR_PREFERRED)) 
	{
      PRINT6ADDR(&uip_ds6_if.addr_list[i].ipaddr);
      PRINTF("\n");
    }
  }
}

static void set_ip_address(void)
{
  uip_ipaddr_t ipaddr;

  uip_ip6addr(&ipaddr, 0xfe80, 0, 0, 0, 0, 0, 0, 0);
  uip_ds6_set_addr_iid(&ipaddr, &uip_lladdr);
  uip_ds6_addr_add(&ipaddr, 0, ADDR_AUTOCONF);
}

static void SendtoServer(int state)
{
	if(state == STATE_ALARM)
	{
		g_alarm_seq++; 		
		printf("(# %d) Client send alarm to server: ", g_alarm_seq);
  	PRINT6ADDR(&g_client_conn->ripaddr);
 		sprintf(g_send_buf, "STATE_ALARM");
  	printf(": %s, lenth:%d\n", g_send_buf, strlen(g_send_buf));
  		
		uip_udp_packet_send(g_client_conn, g_send_buf, strlen(g_send_buf));
	}
	else
	{
		g_alarm_cancel_seq++;		
		PRINTF("(# %d) Alarm cancelled, send to server: ", g_alarm_cancel_seq);
  	PRINT6ADDR(&g_client_conn->ripaddr);
  	sprintf(g_send_buf, "STATE_NORMAL");
  	PRINTF(": %s, lenth:%d\n", g_send_buf, strlen(g_send_buf));
  		
		uip_udp_packet_send(g_client_conn, g_send_buf, strlen(g_send_buf));
	}
}




