package less.gui.server;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.ServerSocket;
import java.net.Socket;

import less.gui.model.PositionXY;
import less.gui.view.LessMainWindowController;

public class PyServer implements Runnable{
	
	private LessMainWindowController mwController;
	
	public void setMainConroller(LessMainWindowController mwController){
		this.mwController = mwController;
	}

	@Override
	public void run() {
		
		String fromClient;
        String toClient;
 
        
		try {
			ServerSocket server = new ServerSocket(8080);
			System.out.println("wait for connection on port 8080");
			
            Socket client = server.accept();
            System.out.println("got connection on port 8080");
            BufferedReader in = new BufferedReader(new InputStreamReader(client.getInputStream()));
 
            fromClient = in.readLine();
            while(!fromClient.equals("bye")){
            //	System.out.println(fromClient);
            	
            	if(fromClient.startsWith("instance")){
            		String arr[] = fromClient.split("_");
            		String objName = this.mwController.objectLV.getSelectionModel().getSelectedItem();
            		mwController.objectAndPositionMap.get(objName).add(new PositionXY(arr[1], arr[2],arr[3]));
            	}
            	
                fromClient= in.readLine();
            }
            in.close();
            client.close();
            server.close();
            System.out.println("Bye");
			
		} catch (IOException e) {
			e.printStackTrace();
		}
        

	}	
}
