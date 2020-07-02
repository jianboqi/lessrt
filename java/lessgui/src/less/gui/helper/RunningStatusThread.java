package less.gui.helper;

import java.util.List;
import java.util.Map;
import java.util.concurrent.ThreadLocalRandom;

import javafx.application.Platform;
import javafx.collections.ObservableList;
import javafx.scene.control.Button;
import javafx.scene.image.Image;
import less.LessMainApp;
import less.gui.model.PositionXY;
import less.gui.view.LessMainWindowController;
import za.co.luma.geom.Vector2DDouble;

public class RunningStatusThread extends Thread{
		
	private Thread t;
	private Thread monitorThread;
	private OutputConsole console;
	private Button runBtn;
	
	private LessMainWindowController mwController;
	
	public RunningStatusThread(Thread moniterThread, OutputConsole console, Button runBtn){
		this.monitorThread = moniterThread;
		this.console = console;
		this.runBtn = runBtn;
	}
	
	public void setMainController(LessMainWindowController mWindowController){
		this.mwController = mWindowController;
	}
	
	private void runButtonStart(){
		runBtn.setDisable(false);
		runBtn.setStyle("-fx-background-color:e8343b;");
		this.mwController.isRunning = true;
		
		this.mwController.mainApp.getPrimaryStage().getIcons().clear();
		this.mwController.mainApp.getPrimaryStage().getIcons().addAll(this.mwController.mainApp.getIconListRed());
	}
	
	private void runButtonEnd(){
		runBtn.setDisable(true);
		runBtn.setStyle("-fx-background-color:#888;");
		this.mwController.isRunning = false;
		this.mwController.mainApp.getPrimaryStage().getIcons().clear();
		this.mwController.mainApp.getPrimaryStage().getIcons().addAll(this.mwController.mainApp.getIconList());
	}
	
	public void stop_current_job(){
		if(this.monitorThread instanceof PyLauncher){
			((PyLauncher)monitorThread).stop_current_job();
		}
		if(this.monitorThread instanceof PoissonThread){
			((PoissonThread)monitorThread).stop_current_job();
		}
		
		if(this.monitorThread instanceof LAICaculatorThread){
			((LAICaculatorThread)monitorThread).stop_current_job();
		}
		
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
