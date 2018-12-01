package less.gui.view;

import java.util.ArrayList;

import javafx.beans.value.ChangeListener;
import javafx.beans.value.ObservableValue;
import javafx.fxml.FXML;
import javafx.scene.control.Button;
import javafx.scene.control.ListView;
import javafx.stage.Stage;
import less.gui.model.FacetOptical;
import less.gui.utils.Const;
import less.gui.utils.DBReader;

public class DBChooserController {
	
	@FXML
	private ListView<String> LambertListView;
	@FXML
	private Button dbOKBtn;
	
	private LessMainWindowController mwController;
	
	private Stage parentStage;
	
	private DBReader dbReader = new DBReader();
	
	public void setMainWindowController(LessMainWindowController mWindowController){
		this.mwController = mWindowController;
	}
	
	public void setParentStage(Stage parentStage) {
		this.parentStage = parentStage;
	}
	
	
	public void initView(){
		dbReader.connect();
		this.LambertListView.setItems(dbReader.getTableList());
		
		this.LambertListView.getSelectionModel().selectedItemProperty().addListener(new ChangeListener<String>() {
			
		    @SuppressWarnings("unchecked")
			@Override
		    public void changed(ObservableValue<? extends String> observable, String oldValue, String newValue) {
		    	if(newValue != null){
		    		dbOKBtn.setDisable(false);
			        
		    	}else{
		    		dbOKBtn.setDisable(true);
		    	}
		    }
		});
	}
	
	@FXML
	public void dbOK(){
		String objName = LambertListView.getSelectionModel().getSelectedItem();
		String waveLength_and_bandwidth = this.mwController.sensorBandsField.getText().trim();
		ArrayList<String> opticalArr = dbReader.getOpticalByName(objName, waveLength_and_bandwidth);
		this.mwController.opticalData.add(new FacetOptical(
				objName,
				opticalArr.get(0),
				opticalArr.get(1),
				opticalArr.get(2),
				Const.LESS_OP_TYPE_DB));
		this.mwController.terrainOpticalData.add(objName);
		this.parentStage.close();
	}
	
	@FXML
	public void cancel(){
		this.parentStage.close();
	}
	
}
