package less.gui.view;

import java.io.File;
import java.util.ArrayList;
import java.util.List;

import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.fxml.FXML;
import javafx.scene.control.Alert;
import javafx.scene.control.CheckBox;
import javafx.scene.control.TextField;
import javafx.stage.Stage;
import less.gui.helper.PyLauncher;
import less.gui.model.FacetOptical;
import less.gui.model.ProspectDParams;
import less.gui.utils.Const;

public class ProspectDController {
	
	private LessMainWindowController mwController;
	private Stage parentStage;
	
	@FXML
	public TextField textFieldOpName;
	@FXML
	public TextField textFieldN;
	@FXML
	public TextField textFieldCar;
	@FXML
	public TextField textFieldBP;
	@FXML
	public TextField textFieldCm;
	@FXML
	public TextField textFieldCab;
	@FXML
	public TextField textFieldAnth;
	@FXML
	public TextField textFieldCw;
	@FXML
	public CheckBox checkboxIsProspect5;
	
	public boolean isEditing = false;
	public FacetOptical facetOptical=null; //current selected row
	
	public void setMainWindowController(LessMainWindowController mWindowController){
		this.mwController = mWindowController;
	}
	
	public void setParentStage(Stage parentStage) {
		this.parentStage = parentStage;
	}
	
	
	public void initView(){
		//show parameters of a optical
		facetOptical = (FacetOptical) this.mwController.opticalTable.getSelectionModel().getSelectedItem();
		if(facetOptical != null){
			if(facetOptical.getOpType() == Const.LESS_OP_TYPE_PROSPECT_D && this.mwController.projManager.prospectDParamsMap.containsKey(facetOptical.getOpticalName())) {
				ProspectDParams prospectDParams = this.mwController.projManager.prospectDParamsMap.get(facetOptical.getOpticalName());
				this.textFieldOpName.setText(prospectDParams.opName);
				this.textFieldN.setText(prospectDParams.N+"");
				this.textFieldCar.setText(prospectDParams.Car+"");
				this.textFieldBP.setText(prospectDParams.BP+"");
				this.textFieldCm.setText(prospectDParams.Cm+"");
				this.textFieldCab.setText(prospectDParams.Cab+"");
				this.textFieldAnth.setText(prospectDParams.Anth+"");
				this.textFieldCw.setText(prospectDParams.Cw+"");
				if(prospectDParams.isProsect5) {
					textFieldAnth.setDisable(true);
				}
				this.checkboxIsProspect5.setSelected(prospectDParams.isProsect5);
				isEditing = true;
			}else {
				isEditing = false;
			}
		}	
	}
	
	@FXML
	private void onOK() {
		String opName = textFieldOpName.getText();
		if(opName.equals("")) {
			Alert alert = new Alert(Alert.AlertType.ERROR);
		    alert.setTitle("Error...");
		    alert.setHeaderText("Error");
		    alert.setContentText("Optical Property Name is empty!");
		    alert.showAndWait();
		}else {
			ObservableList<String> opticalNamesTmp = FXCollections.observableArrayList();
			for(int i=0;i<this.mwController.opticalData.size();i++){
				String opticalName = this.mwController.opticalData.get(i).getOpticalName();
				opticalNamesTmp.add(opticalName);
			}
			
			if(opticalNamesTmp.contains(opName) && isEditing == false) {
				Alert alert = new Alert(Alert.AlertType.ERROR);
			    alert.setTitle("Error...");
			    alert.setHeaderText("Error");
			    alert.setContentText(opName + " already exists!");
			    alert.showAndWait();
			}else {
				ProspectDParams prospectDParams = new ProspectDParams();
				prospectDParams.opName = opName;
				prospectDParams.N = Double.parseDouble(textFieldN.getText());
				prospectDParams.Car = Double.parseDouble(textFieldCar.getText());
				prospectDParams.BP = Double.parseDouble(textFieldBP.getText());
				prospectDParams.Cm = Double.parseDouble(textFieldCm.getText());
				prospectDParams.Cab = Double.parseDouble(textFieldCab.getText());
				prospectDParams.Anth = Double.parseDouble(textFieldAnth.getText());
				prospectDParams.Cw = Double.parseDouble(textFieldCw.getText());
				prospectDParams.isProsect5 = checkboxIsProspect5.isSelected();
				this.mwController.projManager.prospectDParamsMap.put(opName, prospectDParams);
				
				//Calculate Optical Properties
				ArrayList<String> list = new ArrayList<String>();
				String[] wAbarr = this.mwController.sensorBandsField.getText().split(",");
				for(int i=0;i<wAbarr.length;i++){
					String[] wb = wAbarr[i].split(":");
					list.add(wb[0]);
				}
				ProcessBuilder pd = new ProcessBuilder(PyLauncher.getPyexe(),
	        			PyLauncher.getUtilityScriptsPath(Const.LESS_UTILITY_SCRIPT_PROSPECT5D),"--wl",String.join(",", list),
	        			"--N", prospectDParams.N+"", "--Car",prospectDParams.Car+"","--BP",prospectDParams.BP+"",
	        			"--Cm",prospectDParams.Cm+"","--Cab",prospectDParams.Cab+"","--Anth",prospectDParams.Anth+"",
	        			"--Cw",prospectDParams.Cw+"");
				if(prospectDParams.isProsect5) {
					pd = new ProcessBuilder(PyLauncher.getPyexe(),
		        			PyLauncher.getUtilityScriptsPath(Const.LESS_UTILITY_SCRIPT_PROSPECT5D),"--wl",String.join(",", list),
		        			"--N", prospectDParams.N+"", "--Car",prospectDParams.Car+"","--BP",prospectDParams.BP+"",
		        			"--Cm",prospectDParams.Cm+"","--Cab",prospectDParams.Cab+"","--Cw",prospectDParams.Cw+"","--isProspect5");
				}
				
	        	String param_path = this.mwController.projManager.getParameterDirPath();
	        	pd.directory(new File(param_path));
	        	ArrayList<String> reList = PyLauncher.runUtilityscripts(pd, this.mwController.outputConsole, "PROSPECT5D");
	        	String [] r_and_t = reList.get(0).split(";");
	        	String ref_str = r_and_t[0];
	        	String t_String = r_and_t[1];
				if(isEditing == false) { //add new 
					//add to the optical database table
					this.mwController.opticalData.add(new FacetOptical(
							opName,
							ref_str,
							ref_str,
							t_String, Const.LESS_OP_TYPE_PROSPECT_D));
					this.mwController.terrainOpticalData.add(opName);
				}else {//editing optical databse table
					facetOptical.setReflectanceFront(ref_str);
					facetOptical.setReflectanceBack(ref_str);
					facetOptical.setTransmittance(t_String);
					facetOptical.setOpType(Const.LESS_OP_TYPE_PROSPECT_D);
					this.mwController.opticalTable.refresh();
				}	
				
				parentStage.close();
			}
			
		}
		
		
	}
	
	@FXML
	private void onChecked() {
		if(checkboxIsProspect5.isSelected()) {
			textFieldAnth.setDisable(true);
		}else {
			textFieldAnth.setDisable(false);
		}
	}
	
	@FXML
	private void onCancel() {
		parentStage.close();
	}
}
