//SnmpGetNext.java
import java.util.*;
import com.adventnet.snmp.snmp2.*;

public class SnmpGetNext
{
    static String MY_CONNSTATE = ".1.3.6.1.2.1.6.13.1.1";
    static String MY_LOCADDR = ".1.3.6.1.2.1.6.13.1.2";
    static String MY_LOCPORT = ".1.3.6.1.2.1.6.13.1.3";
    static String MY_REMADDR = ".1.3.6.1.2.1.6.13.1.4";
    static String MY_REMPORT = ".1.3.6.1.2.1.6.13.1.5";
 	
	public static void main(String args[]) 
	{    
	    if( args.length < 2)
	    {
	    	System.out.println("Usage : java SnmpGetNext hostname OID ");
	    	System.exit(0);
	    }
	        
		// Take care of getting the hostname and the OID
	    String remoteHost = args[0];   
		
	    // Start SNMP API
	    SnmpAPI api;
	    api = new SnmpAPI();
	    api.start();
	    api.setDebug( false );
		
	    // Open session
	    SnmpSession session = new SnmpSession(api); 
	
	    try 
	    {
	    	session.open();
	    }catch (SnmpException e ) 
	    {
	    	System.err.println("Error opening socket: "+e);
	    }
	
		// set remote Host 
	    session.setPeername(remoteHost);
	    session.setCommunity("teachinglabs");
	
	    // Build GetNext request PDU
	    
	    ArrayList<String>	list_query_oid = new ArrayList<String>();
	    SnmpPDU pdu = new SnmpPDU();	
	    SnmpOID oid = null;
	    int oidNum = args.length-1;
	    
	    for(int i=0;i<oidNum;i++)
	    {
		    String oidCheck; 
		    oidCheck=args[i+1];
		    if(!(oidCheck.equals(MY_CONNSTATE)|| oidCheck.equals(MY_LOCADDR) || oidCheck.equals(MY_LOCPORT)
		    		|| oidCheck.equals(MY_REMADDR) || oidCheck.equals(MY_REMPORT)))
		    {
		    	System.out.println("You have input invlide OID!"+oidCheck);
		    	System.exit(0);
		    }
	    	oid = new SnmpOID(args[i+1]);
	    	pdu.addNull(oid);
	    	list_query_oid.add(args[i+1]);
		    System.out.println("Input OID: "+list_query_oid.get(i));
	    }
	    System.out.println("OidNum: "+oidNum);

	    ArrayList<String>	list_conState = new ArrayList<String>();
	    ArrayList<String>	list_locAddr = new ArrayList<String>();
	    ArrayList<String>	list_locPort = new ArrayList<String>();
	    ArrayList<String>	list_remAddr = new ArrayList<String>();
	    ArrayList<String>	list_remPort = new ArrayList<String>();
	    
	    String stringOid = MY_CONNSTATE;
	    int tableEntries=0;
	    String stringValue;
	    list_conState.clear();list_locAddr.clear();
	    list_locPort.clear();list_remAddr.clear();list_remPort.clear();
	    boolean bExitFlag = false;
	    try
	    {
	        do
	        {
		        pdu.setCommand( api.GETNEXT_REQ_MSG );
	        	pdu = session.syncSend(pdu);
        	
	        	for(int i=0; i<oidNum; i++)
	        	{
	        		stringOid = pdu.getObjectID(i).toString();
					if(!stringOid.contains(list_query_oid.get(i)))  
					{
						System.out.println("End of the table, oid info when exit: "+stringOid); 
						bExitFlag = true;
						break;
					}	
	        		
	        		stringValue = pdu.getVariable(i).toString();
					
					if(stringOid.contains(MY_CONNSTATE))	list_conState.add(stringValue);
	        		else if(stringOid.contains(MY_LOCADDR)) list_locAddr.add(stringValue);
	        		else if(stringOid.contains(MY_LOCPORT)) list_locPort.add(stringValue);
	        		else if(stringOid.contains(MY_REMADDR)) list_remAddr.add(stringValue);
	        		else if(stringOid.contains(MY_REMPORT)) list_remPort.add(stringValue);
	        		else {System.out.println("Invalid oid exit: "+stringOid); break;}	    
					tableEntries++; 
	        	}
	        	
	        } while(!bExitFlag);
	        tableEntries = tableEntries/oidNum;
	        System.out.println("tableEntries: "+tableEntries);
	        
	        ArrayList<String> list_table_head = new ArrayList<String>();
	        if(list_conState.size()>0)	list_table_head.add("ConnState");
	        if(list_locAddr.size()>0)	list_table_head.add("LocAddr");
	        if(list_locPort.size()>0)	list_table_head.add("LocPort");
	        if(list_remAddr.size()>0)	list_table_head.add("RemoteAddr");
	        if(list_remPort.size()>0)	list_table_head.add("RemotePort");
			//debug output
	        System.out.println("list_conState.size()"+list_conState.size()); //
	        System.out.println("list_locAddr.size()"+list_locAddr.size()); //
	        System.out.println("list_locPort.size()"+list_locPort.size()); //
	        System.out.println("list_remAddr.size()"+list_remAddr.size()); //
	        System.out.println("list_remPort.size()"+list_remPort.size()); //
	        
	        System.out.printf("%-10s", "Seq.");
	        for(int i=0; i<list_table_head.size(); i++)
	        	System.out.printf("%-20s", list_table_head.get(i));
	        System.out.println("");
	        
	        for(int i=0; i<tableEntries; i++)
	        {
	        	System.out.printf("%-10d", i+1);
	        	if(list_conState.size()>0)	System.out.printf("%-20s", ReadableConState(list_conState.get(i)));
		        if(list_locAddr.size()>0)	System.out.printf("%-20s", list_locAddr.get(i));
		        if(list_locPort.size()>0)	System.out.printf("%-20s", list_locPort.get(i));
		        if(list_remAddr.size()>0)	System.out.printf("%-20s", list_remAddr.get(i));
		        if(list_remPort.size()>0)	System.out.printf("%-20s", list_remPort.get(i));    
		        System.out.println("");
	        }
	    }catch (SnmpException e) 
		{
	    	System.err.println("Error sending SNMP request: "+e);
		} 
	    
		session.close();
		api.close();	
	}
	
	public static String ReadableConState(String conState)
	{
		int state = Integer.parseInt(conState);
		switch (state)
		{
			case 1: return "closed(1)";
			case 2: return "listen(2)";
			case 3: return "synSent(3)";
			case 4: return "synReceived(4)";
			case 5: return "established(5)";
			case 6: return "finWait1(6)";
			case 7: return "finWait2(7)";
			case 8: return "closeWait(8)";
			case 9: return "lastAck(9)";
			case 10: return "closing(10)";
			case 11: return "timeWait(11)";
			case 12: return "deleteTCB(12)";
			default: return "NA";
		}
	}
}

/*
feps-teach01 
.1.3.6.1.2.1.6.13.1.1
.1.3.6.1.2.1.6.13.1.2
.1.3.6.1.2.1.6.13.1.3
.1.3.6.1.2.1.6.13.1.4
.1.3.6.1.2.1.6.13.1.5

0329
Input OID: .1.3.6.1.2.1.6.13.1.1
Input OID: .1.3.6.1.2.1.6.13.1.2
Input OID: .1.3.6.1.2.1.6.13.1.3
Input OID: .1.3.6.1.2.1.6.13.1.4
Input OID: .1.3.6.1.2.1.6.13.1.5
OidNum: 5
End of the table, oid info when exit: .1.3.6.1.2.1.6.13.1.2.0.0.0.0.22.0.0.0.0.0
                  
*/