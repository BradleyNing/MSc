/* Assignment 1, Name: Bradley Ning Zili, URN: 6455442 */
/* As1-uIP-Server.c  for client */
/* Assignment 1 - Check, Alarm with uIP server processes. */
/* There is another file of Check, Alarm, Calibrating and Powertrace, as it looks too big  for all functions fitting into one task for XM1000 */   

#include <stdio.h>
#include <string.h>

#include "contiki.h"
//#include "contiki-lib.h"
#include "contiki-net.h"
#include "dev/leds.h"
#include "dev/button-sensor.h"

#define DEBUG DEBUG_PRINT
#include "net/uip-debug.h"

#define UIP_IP_BUF   ((struct uip_ip_hdr *)&uip_buf[UIP_LLH_LEN])

#define SEND_BUF_LEN	15
#define STATE_NORMAL	0
#define STATE_ALARM		1

static struct uip_udp_conn *g_server_conn;

void print_ip_address()
{
  int i;
  uint8_t state;

  printf("My IPv6 addresses: ");
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

PROCESS(As1_server, "Assignment1 alarm server");
AUTOSTART_PROCESSES(&As1_server);

PROCESS_THREAD(As1_server, ev, data)
{
	uip_ipaddr_t	ipaddr;
 	static int 		s_alarm_status;
	static int		s_alarm_counter=0, s_alarm_cancel_counter=0;
	char 			buf[SEND_BUF_LEN];
	char 			*str;
	
	PROCESS_BEGIN();
	printf("UDP server started\n");

  	// set local IP address
  	uip_ip6addr(&ipaddr, 0xfe80, 0, 0, 0, 0, 0, 0, 0);
  	uip_ds6_set_addr_iid(&ipaddr, &uip_lladdr);
  	uip_ds6_addr_add(&ipaddr, 0, ADDR_AUTOCONF);

	print_ip_address();

 	g_server_conn = udp_new(NULL, UIP_HTONS(3001), NULL);
 	if (g_server_conn == NULL) printf("server_conn new error !!!!!!!!!!!!!!!!\n");

 	udp_bind(g_server_conn, UIP_HTONS(3000));

 	leds_init();
	leds_on(LEDS_GREEN);    // switch on green led in normal state
	SENSORS_ACTIVATE(button_sensor);

	s_alarm_status = STATE_NORMAL;
	s_alarm_counter = 0;
	s_alarm_cancel_counter = 0;

 	while(1) 
	{
 		PROCESS_WAIT_EVENT();
    	if(ev == tcpip_event) 
		{
		 	if(uip_newdata()) 
			{
				str = uip_appdata;
				str[uip_datalen()] = '\0';
				printf("Server received: '%s' from ", str);
			    PRINT6ADDR(&UIP_IP_BUF->srcipaddr);
    			printf("\n");
				
				if(strcmp(str, "STATE_ALARM") == 0)
				{
					s_alarm_status = STATE_ALARM;
					s_alarm_counter++;
					leds_off(LEDS_ALL);
					leds_on(LEDS_RED);
					str[0] = 0;
					printf("\nIt's #%d alarm from the client\n", s_alarm_counter);
					printf("If you want client to action, please press button ...\n");   //wait for a command 
				}
				else
				{
					s_alarm_status = STATE_NORMAL;
					s_alarm_cancel_counter++;
					leds_off(LEDS_ALL);
					leds_on(LEDS_GREEN);
					str[0] = 0;
					printf("\nAlarm canceled, It's # %d alarm cancel from the client\n", s_alarm_cancel_counter);
					printf("If you want client to stop action, please press button\n");
				}
			}
		}
		if( (ev==sensors_event) && (data==&button_sensor) )
		{
			if(s_alarm_status == STATE_ALARM)
			{				
				printf("Button pressed ...\n");
				uip_ipaddr_copy(&g_server_conn->ripaddr, &UIP_IP_BUF->srcipaddr);
				sprintf(buf, "ACTION_ALARM");
				printf("Send ACTION_ALARM to the client!\n");

				uip_udp_packet_send(g_server_conn, buf, strlen(buf));
				/* Restore server connection to allow data from any node */
//				memset(&g_server_conn->ripaddr, 0, sizeof(g_server_conn->ripaddr));
			}
			else
			{
				printf("Button pressed ...\n");
				uip_ipaddr_copy(&g_server_conn->ripaddr, &UIP_IP_BUF->srcipaddr);
				sprintf(buf, "ACTION_CANCEL");
				printf("Send ACTION_CANCEL to the client!\n");

				uip_udp_packet_send(g_server_conn, buf, strlen(buf));
				/* Restore server connection to allow data from any node */
//				memset(&g_server_conn->ripaddr, 0, sizeof(g_server_conn->ripaddr));
			}
		}
    }
	PROCESS_END();
}
