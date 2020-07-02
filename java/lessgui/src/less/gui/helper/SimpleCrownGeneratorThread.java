package less.gui.helper;

import java.io.File;
import java.util.Arrays;
import java.util.concurrent.CountDownLatch;

import less.gui.utils.Const;
import less.gui.view.LAICalculatorController;
import less.gui.view.LessMainWindowController;
import less.gui.view.SimpleCrownGeneratorController;

public class SimpleCrownGeneratorThread extends Thread{
	private Thread t;
	private OutputConsole bdConsole;
	public SimpleCrownGeneratorController scController;
	private LessMainWindowController mwController;
	
	private CountDownLatch latch;
	
	public void setLessMainController(LessMainWindowController mwController){
		this.mwController = mwController;
	}
	
	public void prepare(SimpleCrownGeneratorController scController,OutputConsole bdConsole, CountDownLatch latch){
		this.scController = scController;
		this.bdConsole = bdConsole;
		this.latch = latch;
	}
	
	
	public void run(){
		synchronized (this) {
			CrownGenerate();
			this.latch.countDown();
			notify();
		}
	}
	
	public void start () {
      if (t == null) {
         t = new Thread (this, "SimpleCrownGenerator");
         t.setUncaughtExceptionHandler((thread, throwable) -> {
        	 bdConsole.setErrorMode();
 			 bdConsole.log(throwable.getMessage());
 			// notify to finish
 			synchronized (this) {
 				 notify();
 			}
         });
         t.start ();
      }
   }

	private void CrownGenerate() {
		ProcessBuilder pd = new ProcessBuilder(PyLauncher.getPyexe(),
    			PyLauncher.getUtilityScriptsPath(Const.LESS_UTILITY_SCRIPT_SIMPLE_CROWN_GENERATOR),
    			"--crown_shape",scController.combCrownShape.getSelectionModel().getSelectedItem(), 
    			"--crown_height",scController.tfCrownHeight.getText(),
    			"--crown_diameter_sn",scController.tfCrownDiameterSN.getText(),
    			"--crown_diameter_ew",scController.tfCrownDiameterEW.getText(),
    			"--trunk_height",scController.tfTrunkHeight.getText(),
    			"--dbh",scController.tfDBH.getText(),
    			"--lad",scController.combLAD.getSelectionModel().getSelectedItem(),
    			"--leaf_numbers",scController.tfLeafNum.getText(),
    			"--leaf_shape", scController.combLeafShape.getSelectionModel().getSelectedItem(),
    			"--polygon_sides",scController.tfPolygonSides.getText(),
    			"--single_leaf_area",scController.tfSingleLeafArea.getText(),
    			"--out_obj_path",scController.tfOutObjPath.getText());
		this.mwController.outputConsole.log("INFO: Command " + Arrays.toString(pd.command().toArray()).replace(",", " "));
    	
    	PyLauncher.runUtilityscripts(pd, this.mwController.outputConsole, "");	
	}
}
