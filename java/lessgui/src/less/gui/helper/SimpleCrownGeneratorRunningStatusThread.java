package less.gui.helper;

import javafx.application.Platform;
import javafx.scene.control.Button;

public class SimpleCrownGeneratorRunningStatusThread extends Thread{
	
	private Thread t;
	private Thread monitorThread;
	private Button runBtn;
		
	public SimpleCrownGeneratorRunningStatusThread(Thread moniterThread, Button runBtn){
		this.monitorThread = moniterThread;
		this.runBtn = runBtn;
	}
	
	
	private void runButtonStart(){
		runBtn.setStyle("-fx-text-fill: #ff0000");
		runBtn.setDisable(true);
	}
	
	private void runButtonEnd(){
		runBtn.setStyle("-fx-text-fill: #000000");
		runBtn.setDisable(false);
	}
	
	public void run(){
		Platform.runLater(()->runButtonStart());
		monitorThread.start();
		synchronized (monitorThread) {
			try {
				monitorThread.wait();//waiting for complete
			} catch (InterruptedException e) {
				e.printStackTrace();
			}
			//when calculation ends
			Platform.runLater(()->runButtonEnd());
		}
	}
	
	@Override
	public void start () {
	      if (t == null) {
	         t = new Thread (this, "runningStatus");
	         t.start ();
	         
	      }
	   }
}
