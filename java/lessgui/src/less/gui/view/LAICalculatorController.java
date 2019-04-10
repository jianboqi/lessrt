package less.gui.view;

import java.io.IOException;
import java.lang.reflect.Array;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

import javafx.collections.ObservableFloatArray;
import javafx.collections.ObservableList;
import javafx.fxml.FXML;
import javafx.geometry.Insets;
import javafx.geometry.Point3D;
import javafx.scene.Node;
import javafx.scene.control.CheckBox;
import javafx.scene.control.TextField;
import javafx.scene.layout.AnchorPane;
import javafx.scene.layout.VBox;
import javafx.scene.shape.Mesh;
import javafx.scene.shape.ObservableFaceArray;
import javafx.scene.shape.TriangleMesh;
import javafx.stage.Stage;
import less.gui.display3D.DrawElement;
import less.gui.helper.LAICaculatorThread;
import less.gui.helper.PoissonThread;
import less.gui.helper.RunningStatusThread;
import less.gui.model.LSBoundingbox;
import less.gui.model.OpticalThermalProperty;
import less.gui.model.PositionXY;

public class LAICalculatorController {
	@FXML
	private CheckBox selectAllChecbox;
	
	@FXML
	public TextField LAITextField;
	
	@FXML
	public TextField textFieldRows;
	@FXML
	public TextField textFieldCols;
	@FXML
	public TextField textFieldHeight;

	@FXML
	public VBox componentVBox;
	
	private Stage parentStage;
	public LessMainWindowController mwController;
	
	public void setParentStage(Stage parentStage) {
		this.parentStage = parentStage;
	}
	
	public void setmwController(LessMainWindowController mwController){
		this.mwController = mwController;
	}
	
	public void initView(){
		if(this.mwController.simulation_path == null){
			return;
		}
		
		componentVBox.setPadding(new Insets(10, 10, 10, 10));
		componentVBox.setSpacing(10);
		
		//iterate all components
		for(Map.Entry<String, ObservableList<String>> entry: this.mwController.objectsAndCompomentsMap.entrySet()){
			ObservableList<String> compList = entry.getValue();
			if(compList.size()==0){
				return;
			}
			AnchorPane spacer = new AnchorPane();
			spacer.setPrefSize(100, 10);
			componentVBox.getChildren().add(spacer);
			for(int i=0;i<compList.size();i++){ //component
				String compName = compList.get(i);
				CheckBox checkBox = new CheckBox();
				checkBox.setMnemonicParsing(false);
				checkBox.setText(compName);
				checkBox.setSelected(true);
				checkBox.setUserData(compName);
				componentVBox.getChildren().add(checkBox);
				
			}
			
		}
	}
	

	
	@FXML
	private void selectAll(){
		for (Node checkbox : componentVBox.getChildren()) {
			if (checkbox instanceof CheckBox){
				CheckBox checkBox2 = (CheckBox)checkbox;
				if(this.selectAllChecbox.isSelected())
					checkBox2.setSelected(true);
				else
					checkBox2.setSelected(false);
			}
		}
	}
	
	
	@FXML
	private void run_lai(){
		LAICaculatorThread laiThread = new LAICaculatorThread();
		laiThread.prepare(this,this.mwController.outputConsole);
		RunningStatusThread runningStatusThread = new RunningStatusThread(laiThread, this.mwController.outputConsole, this.mwController.runBtn);
		runningStatusThread.setMainController(this.mwController);
		runningStatusThread.start();
	}
	
	
	
}
