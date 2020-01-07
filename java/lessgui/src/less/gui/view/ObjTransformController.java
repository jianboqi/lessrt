package less.gui.view;

import javafx.fxml.FXML;
import javafx.scene.control.CheckBox;
import javafx.scene.control.RadioButton;
import javafx.scene.control.TextField;
import javafx.scene.control.ToggleGroup;
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
	@FXML
	RadioButton radiobtnXYZ;
	@FXML
	RadioButton radiobtnXY;
	
	private Stage parentStage;
	
	private ObjectsDefineWindowViewController objDefController;
	
	private ToggleGroup group;
	
	public void initView() {
		group = new ToggleGroup();
		radiobtnXYZ.setToggleGroup(group);
		radiobtnXY.setToggleGroup(group);
		radiobtnXYZ.setDisable(true);
		radiobtnXYZ.setUserData("xyz");
		radiobtnXY.setDisable(true);
		radiobtnXY.setUserData("xy");
	}
	
	
    public void setParentStage(Stage stage){
    	this.parentStage = stage;
    }
    
    public void setObjDefController(ObjectsDefineWindowViewController objDefController){
    	this.objDefController = objDefController;
    }
    
    @FXML
    private void enableTransform() {
    	if(this.TranslateToOriginCheckBox.isSelected()) {
    		radiobtnXYZ.setDisable(false);
    		radiobtnXY.setDisable(false);
    	}else {
    		radiobtnXYZ.setDisable(true);
    		radiobtnXY.setDisable(true);
    	}
    }
    
    @FXML
    private void onOK(){
    	this.objDefController.fx = Double.parseDouble(this.scaleXField.getText());
    	this.objDefController.fy = Double.parseDouble(this.scaleYField.getText());
    	this.objDefController.fz = Double.parseDouble(this.scaleZField.getText());
    	if(this.TranslateToOriginCheckBox.isSelected()) {
    		String selected = group.getSelectedToggle().getUserData().toString();
    		if(selected.equals("xyz")) {
    			this.objDefController.isTranslate2Origin_xyz = true;
    			this.objDefController.isTranslate2Origin_xy = false;
    		}else if(selected.equals("xy")) {
    			this.objDefController.isTranslate2Origin_xy = true;
    			this.objDefController.isTranslate2Origin_xyz = false;
    		}
    	}else {
    		this.objDefController.isTranslate2Origin_xy = false;
    		this.objDefController.isTranslate2Origin_xyz = false;
    	}
    	this.parentStage.close();
    }
	
}
