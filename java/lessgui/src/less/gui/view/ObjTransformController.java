package less.gui.view;

import javafx.fxml.FXML;
import javafx.scene.control.CheckBox;
import javafx.scene.control.TextField;
import javafx.stage.Stage;

public class ObjTransformController {
	@FXML
	TextField scaleXField;
	@FXML
	TextField scaleYField;
	@FXML
	TextField scaleZField;
	@FXML
	CheckBox TranslateToOriginCheckBox;
	
	private Stage parentStage;
	
	private ObjectsDefineWindowViewController objDefController;
	
	
    public void setParentStage(Stage stage){
    	this.parentStage = stage;
    }
    
    public void setObjDefController(ObjectsDefineWindowViewController objDefController){
    	this.objDefController = objDefController;
    }
    
    @FXML
    private void onOK(){
    	this.objDefController.fx = Double.parseDouble(this.scaleXField.getText());
    	this.objDefController.fy = Double.parseDouble(this.scaleYField.getText());
    	this.objDefController.fz = Double.parseDouble(this.scaleZField.getText());
    	if(this.TranslateToOriginCheckBox.isSelected()) {
    		this.objDefController.isTranslate2Origin = true;
    	}else {
    		this.objDefController.isTranslate2Origin = false;
    	}
    	this.parentStage.close();
    }
	
}
