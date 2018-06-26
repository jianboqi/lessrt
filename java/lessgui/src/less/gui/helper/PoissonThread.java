package less.gui.helper;

import java.util.List;
import java.util.concurrent.ThreadLocalRandom;

import javafx.application.Platform;
import javafx.collections.ObservableList;
import less.gui.model.PositionXY;
import less.gui.view.LessMainWindowController;
import za.co.luma.geom.Vector2DDouble;
import za.co.luma.math.sampling.Sampler;
import za.co.luma.math.sampling.UniformPoissonDiskSampler;

public class PoissonThread extends Thread{
	private Thread t;
	private OutputConsole bdConsole;
	
	private double minDist;
	private double xExtent;
	private double yExtent;
	public int objNum;
	public double objectHeight;
	public LessMainWindowController mwController;
	List<Vector2DDouble> pointList;
	
	public RunningMode runningMode = RunningMode.RUNNING;
	
	enum RunningMode{
		RUNNING, POST_PROCESSING
	}
	
	public void prepare(OutputConsole bdConsole,double minDist,double xExtent,double yExtent,int objNum,
			LessMainWindowController mwController, double objectHeight){
		this.bdConsole = bdConsole;
		this.bdConsole.setNormalMode();
		this.minDist = minDist;
		this.xExtent = xExtent;
		this.yExtent = yExtent;
		this.objNum = objNum;
		this.mwController = mwController;
		this.objectHeight = objectHeight;
	}
	
	public void run(){
		synchronized (this) {
			
			switch (runningMode) {
			case RUNNING:
				do_sampling();
				break;
			case POST_PROCESSING:
				//do_post_processing();
				break;
			default:
				break;
			}			
			notify();
		}
		
	}
	
	public void start () {
	      if (t == null) {
	         t = new Thread (this, "samplingthread");
	         t.setUncaughtExceptionHandler((thread, throwable) -> {
	        	 bdConsole.setErrorMode();
	 			 bdConsole.log(throwable.getMessage());
	 			synchronized (this) {
	 				 notify();
	 			}
	         });
	         t.start ();
	      }
	   }
	
	public List<Vector2DDouble> getResults(){
		return pointList;
	}
	
	public void stop_current_job(){
//		this.interrupt();
//		synchronized (this) {
//			 notify();
//		}
	}
	
	/**
	 * generate poisson
	 */
	public void do_sampling(){
		bdConsole.log("Generating random numbers, Please wait...\n");
		Sampler<Vector2DDouble> sampler = new UniformPoissonDiskSampler(0, 0, xExtent, yExtent, minDist);
		pointList = sampler.sample();
		int treeNum = pointList.size();
	
		bdConsole.log("Finished.\n");
		bdConsole.log("Total number of generated trees: "+treeNum+"\n");
		do_post_processing();
	}
	
	/**
	 * after generation of points, add to file
	 */
	public void do_post_processing(){
//		for(Map.Entry<String, ObservableList<PositionXY>> entry: this.mwController.objectAndPositionMap.entrySet()){
//			entry.getValue().removeListener(this.mwController.tree_pos_change_listener);
//		}
		
		this.mwController.StopDrawTree = true;
		ObservableList<String> selectedObjs = this.mwController.objectLV.getSelectionModel().getSelectedItems();
		for(int i=0;i<pointList.size();i++){
			int randomNum = ThreadLocalRandom.current().nextInt(0, objNum);
			Vector2DDouble vec = pointList.get(i);
			this.mwController.objectAndPositionMap.get(selectedObjs.get(randomNum)).add(new PositionXY(vec.x+"", vec.y+"",objectHeight+""));
		}
//		for(Map.Entry<String, ObservableList<PositionXY>> entry: this.mwController.objectAndPositionMap.entrySet()){
//			entry.getValue().addListener(this.mwController.tree_pos_change_listener);
//		}
		this.mwController.StopDrawTree = false;
		Platform.runLater(() -> this.mwController.reDrawAll());
	}
	
}
