package less.gui.view;

import java.util.Map;

import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.fxml.FXML;
import javafx.scene.control.ComboBox;
import javafx.scene.control.TextField;
import javafx.stage.Stage;
import less.gui.helper.PoissonThread;
import less.gui.helper.RunningStatusThread;
import less.gui.model.PositionXY;
import less.gui.utils.CommonUitls;
import less.gui.utils.Const;


public class TreePosGenerateController {
	
	@FXML
	private TextField minDistTextField;
	@FXML
	private ComboBox<String> disTypeComboBox;
	
	private LessMainWindowController mwController;
	
	private Stage parentStage;
	
	public void setMainWindowController(LessMainWindowController mWindowController){
		this.mwController = mWindowController;
	}
	
	public void setParentStage(Stage parentStage) {
		this.parentStage = parentStage;
	}
	
	@FXML
	public void cancel(){
		this.parentStage.close();
	}
	
	public void initView(){
		ObservableList<String> comboxValue = FXCollections.observableArrayList();
		comboxValue.add(Const.LESS_TREE_POS_DIS_POISSON);
		//comboxValue.add(Const.LESS_TREE_POS_DIS_UNIFORM);
		this.disTypeComboBox.getItems().setAll(comboxValue);
		this.disTypeComboBox.getSelectionModel().select(Const.LESS_TREE_POS_DIS_POISSON);
	}
	
	
	
	
	/**
	 * save the bands
	 */
	@FXML
	public void OK(){
		
		String minDiststr = this.minDistTextField.getText();
		if(!CommonUitls.isNumeric(minDiststr))
		{
			System.out.println("minimum distance a valid number.");
			return;
		}
		double minDist = Double.parseDouble(minDiststr);
		
		double xExtent = Double.parseDouble(this.mwController.sceneXSizeField.getText().trim().replaceAll(",", ""));
		double yExtent = Double.parseDouble(this.mwController.sceneYSizeField.getText().trim().replaceAll(",", ""));
		
		if(this.disTypeComboBox.getSelectionModel().getSelectedItem().equals(Const.LESS_TREE_POS_DIS_POISSON)){
			int objNum = this.mwController.objectsList.size();
			if(objNum == 0){
				System.out.println("No Objects are defined.");
				return;
			}
			//只生成那些被选中的
			ObservableList<String> selectedObjs = this.mwController.objectLV.getSelectionModel().getSelectedItems();
			if(selectedObjs.size() == 0){//当只选择部分时，则只对部分进行生成
				System.out.println("Please choose at least one object to populate.");
				return;
			}else{
				objNum = selectedObjs.size();
			}
			
			
			for (String objname : selectedObjs) {
				this.mwController.objectAndPositionMap.get(objname).clear();
			}
			
//			for(Map.Entry<String, ObservableList<PositionXY>> entry: this.mwController.objectAndPositionMap.entrySet()){
//				entry.getValue().clear();
//			}	
			
			PoissonThread poissonThread = new PoissonThread();
			poissonThread.prepare(this.mwController.outputConsole,minDist,xExtent,yExtent,objNum,this.mwController);
			RunningStatusThread runningStatusThread = new RunningStatusThread(poissonThread, this.mwController.outputConsole, this.mwController.runBtn);
			runningStatusThread.setMainController(this.mwController);
			runningStatusThread.start();
			
		}
		
		this.parentStage.close();
	}
	

	
}
