package less.gui.view;

import javafx.collections.FXCollections;
import javafx.fxml.FXML;
import javafx.scene.control.ComboBox;
import javafx.stage.Stage;
import less.gui.model.AtmosphereParams;
import less.gui.model.SunPos;
import less.gui.utils.Const;

public class AtmosphereEditorController {
	@FXML
	private ComboBox<String> atsComboxCalculationMode;
	
	
	private Stage parentStage;
	private LessMainWindowController mwController;
	
	public void setParentStage(Stage parentStage) {
		this.parentStage = parentStage;
	}
	
	public void setmwController(LessMainWindowController mwController){
		this.mwController = mwController;
	}
	
	public void initView(){
		
		atsComboxCalculationMode.setItems(FXCollections.observableArrayList(
				Const.LESS_ATS_CAL_MODE_TWOSTEP, Const.LESS_ATS_CAL_MODE_ONESTEP
				));
		atsComboxCalculationMode.setValue(Const.LESS_ATS_CAL_MODE_TWOSTEP);
		
		if(this.mwController.projManager.atmosphereParams != null){
			AtmosphereParams atsParams = this.mwController.projManager.atmosphereParams;	
			atsComboxCalculationMode.setValue(atsParams.calculationMode);			
		}
	}
	
	@FXML
	private void onOK() {
		AtmosphereParams atmosphereParams = new AtmosphereParams();
		atmosphereParams.calculationMode = atsComboxCalculationMode.getSelectionModel().getSelectedItem();
		this.mwController.projManager.atmosphereParams = atmosphereParams;
		parentStage.close();
	}
	@FXML
	private void onCancel() {
		parentStage.close();
	}
	
}
