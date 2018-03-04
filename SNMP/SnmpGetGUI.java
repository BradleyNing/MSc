
//SnmpGetGUI.jave
import javax.swing.JPanel;

import com.adventnet.snmp.snmp2.SnmpAPI;
import com.adventnet.snmp.snmp2.SnmpException;
import com.adventnet.snmp.snmp2.SnmpOID;
import com.adventnet.snmp.snmp2.SnmpPDU;
import com.adventnet.snmp.snmp2.SnmpSession;

//import java.awt.GridLayout;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.util.ArrayList;

import javax.swing.*;

/**
 *
 * @author Bradl
 */
public class SnmpGetGUI extends JPanel
                        implements ActionListener
{
    JButton btnStart, btnStop;
    //protected JLabel lblUnit1, lblUnit2;
    //protected JTextField txtUnit1, txtUnit2;
    boolean bRunning=true;
    static String remoteHost, OID_1, OID_2, unit1, unit2; 
	
    static double p_period;
    static int w_size ; 

    public SnmpGetGUI()
    {
        JFrame frame = new JFrame("Frame test");
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);

        btnStart = new JButton("Start");
        btnStart.setActionCommand("start");
        btnStop  = new JButton("Stop");
        btnStop.setActionCommand("stop");

        btnStart.addActionListener(this);
        btnStop.addActionListener(this);
        add(btnStart); 
        add(btnStop); 
        btnStop.setEnabled(false);
        
        //lblUnit1 = new JLabel("OID1 Unit: ");
        //lblUnit2 = new JLabel("OID2 Unit2");
        //txtUnit1 = new JTextField(10);
        //txtUnit2 = new JTextField(10);
        //add(lblUnit1); add(txtUnit1);
        //add(lblUnit2); add(txtUnit2);
    }

    @Override
    public void actionPerformed(ActionEvent e)
    {
        if ("start".equals(e.getActionCommand()))
        {
            bRunning=true;
            System.out.println("bRunning:" +bRunning);
            System.out.println("Start");
            
            btnStop.setEnabled(true);
            btnStart.setEnabled(false);
            GetDataThread getDataThread = new GetDataThread();
            getDataThread.start();
            
        }
        else
        {           
            bRunning=false;
            System.out.println("bRunning:" +bRunning);
            System.out.println("Stop");
            
            btnStart.setEnabled(true);
            btnStop.setEnabled(false);
        }
    }
    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) 
    {
        javax.swing.SwingUtilities.invokeLater(new Runnable() {
            public void run() {
                GUI();
            }
        });
        if( args.length < 7)
        {
            System.out.println("Usage : java SnmpGet hostname OID_1, OID_2, polling_period, window_size, oid1 unit, oid2 unit");
            System.exit(0);
        }

        remoteHost = args[0];
        OID_1 = args[1];
        OID_2 = args[2];

        p_period = Double.parseDouble(args[3]);
        w_size = Integer.parseInt(args[4]);

        unit1 = args[5];
        unit2 = args[6];

        if(p_period<=0 || w_size <=0)
        {
            System.out.println("polling_period, window_size should greater than 0");
            System.exit(0);
        }	                   
    }
    
    private static void GUI()
    {
        JFrame frame = new JFrame("SnmpGet");
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);

        //Create and set up the content pane.
        SnmpGetGUI newContentPane;
        newContentPane = new SnmpGetGUI();
        newContentPane.setOpaque(true); 
        frame.setContentPane(newContentPane);

        //Display the window.
        frame.pack();
        frame.setVisible(true);        
    }

    class GetDataThread extends Thread
    {
    	@Override
    	public void run()
    	{
            SnmpAPI api;
            api = new SnmpAPI();
            api.start();
            api.setDebug(false);

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

            // Build Get request PDU
            SnmpPDU pdu = new SnmpPDU();
            pdu.setCommand( api.GET_REQ_MSG );

            SnmpOID oid = new SnmpOID(OID_1);
            pdu.addNull(oid);
            oid = new SnmpOID(OID_2);
            pdu.addNull(oid);

            System.out.println("Input Oid1: "+ OID_1);
            System.out.println("Input Oid2: "+OID_2);
            System.out.println("Polling Period: "+p_period);
            System.out.println("Window size: "+w_size);


            ArrayList<Integer>	list_raw_values1 = new ArrayList<Integer>();
            ArrayList<Integer>	list_raw_values2 = new ArrayList<Integer>();

            //ArrayList<Double>	list_cal_values1 = new ArrayList<Double>();
            //ArrayList<Double>	list_cal_values2 = new ArrayList<Double>();

            long seqIndex = 0;  //Index for polling
            System.out.printf("%-10s%-25s%-20s%-20s%-25s%-20s%-20s%n", "Seq", "InSegs_OID", "Value",
                            unit1, "OutSegs_OID", "Value", unit2);

            String stringValue1, stringValue2;
            
            try 
            {
                seqIndex =0;
                do{
                    // Send PDU and receive response PDU
                    seqIndex++;
                    pdu.setCommand( api.GET_REQ_MSG );
                    pdu = session.syncSend(pdu);

                    stringValue1 = pdu.getVariable(0).toString();
                    if(stringValue1.equals(null)) //TODO
                    { 
                        System.out.printf("Something wrong with the OID");
                        System.exit(0);
                    }
                    stringValue2 = pdu.getVariable(1).toString();
                    list_raw_values1.add(Integer.parseInt(stringValue1));
                    list_raw_values2.add(Integer.parseInt(stringValue2));
                    if(list_raw_values1.size()>w_size+1)
                    {
                        list_raw_values1.remove(0);
                        list_raw_values2.remove(0);
                    }
                    
                    if(seqIndex<w_size+1)
                        System.out.printf("%-10d%-25s%-20s%-20s%-25s%-20s%-20s%n",seqIndex, OID_1, stringValue1, 
                                    "NA", OID_2, stringValue2, "NA");
                    else
                    {
                        double value1 = (list_raw_values1.get(w_size)-list_raw_values1.get(0))/(1.0*w_size*p_period);
                        double value2 = (list_raw_values2.get(w_size)-list_raw_values2.get(0))/(1.0*w_size*p_period);
                        System.out.printf("%-10d%-25s%-20s%-20.1f%-25s%-20s%-20.1f%n",seqIndex, OID_1, stringValue1, 
                                    value1, OID_2, stringValue2, value2);
                    }
                    Thread.sleep((int)p_period*1000);							
                }while(bRunning);		    	
            } catch (SnmpException e) 
            {
                System.err.println("Error sending SNMP request: "+e);
            } 
            catch (InterruptedException e) 
            {
                e.printStackTrace();
            }

            session.close();
            // stop api thread
            api.close();
    	}
    }
}
/*   
    public static double Calculate(String str, ArrayList<Integer> l_raw_value)
    {
        if (l_raw_value.size() == 1) return 0;
        else return (l_raw_value.get(1)-l_raw_value.get(0))/p_period;
    }

    public static void CalculateUWMA(Double Values[], ArrayList<Double> l_p_value1, ArrayList<Double> l_p_value2)
    {
        Values[0] = 0.0;
        Values[1] = 0.0;
        if(l_p_value1.size() != l_p_value2.size()) {System.out.println("Error in list"); return;}

        int size = l_p_value1.size();
        for(int loopIdx=0; loopIdx<size; loopIdx++)
        {
            Values[0] += l_p_value1.get(loopIdx);
            Values[1] += l_p_value2.get(loopIdx);
        }
        Values[0] = Values[0]/size;
        Values[1] = Values[1]/size;
    }
    */


/*
feps-teach01 
.1.3.6.1.2.1.6.10.0
.1.3.6.1.2.1.6.11.0
6
3
bytes/s
packets/s

feps-teach01 
.1.3.6.1.2.1.2.2.1.10
.1.3.6.1.2.1.2.2.1.16
6
3


feps-teach01 
.1.3.6.1.2.1.4.9.0
.1.3.6.1.2.1.4.10.0
6
3

*/