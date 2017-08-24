package less.gui.view;

import javax.print.CancelablePrintJob;

import javafx.fxml.FXML;
import javafx.scene.control.CheckBox;
import javafx.scene.control.TextField;
import javafx.scene.control.TextFormatter;
import javafx.stage.Stage;
import less.gui.utils.CommonUitls;
import less.gui.utils.NumberStringFilteredConverter;

public class SpectralBandsDefineController {
	@FXML
	private TextField FromTextField;
	@FXML
	private TextField ToTextField;
	@FXML
	private TextField BandNumTextField;
	@FXML
	private TextField BandWidthTextField;
	@FXML
	private CheckBox appendCheckBox;
	
	
	private LessMainWindowController mwController;
	private Stage parentStage;
	
	public void setMainWindowController(LessMainWindowController mWindowController){
		this.mwController = mWindowController;
	}
	
	public void setParentStage(Stage parentStage) {
		this.parentStage = parentStage;
	}
	
	public void initView(){
		//this.inputValidation();
	}
	
	public void inputValidation(){
		NumberStringFilteredConverter converter = new NumberStringFilteredConverter();
		FromTextField.setTextFormatter(new TextFormatter<>(converter,600.0,converter.getFilter()));
		ToTextField.setTextFormatter(new TextFormatter<>(converter,900.0,converter.getFilter()));
		BandNumTextField.setTextFormatter(new TextFormatter<>(converter,2,converter.getFilter()));
	}
	
	@FXML
	public void cancel(){
		this.parentStage.close();
	}
	
	/**
	 * save the bands
	 */
	@FXML
	public void OK(){
		double fromw = Double.parseDouble(this.FromTextField.getText().replaceAll(",", ""));
		double tow = Double.parseDouble(this.ToTextField.getText().replaceAll(",", ""));
		int bandnum = Integer.parseInt(this.BandNumTextField.getText().replaceAll(",", ""));
		String bandwidth = this.BandWidthTextField.getText().replaceAll(",", "");
		if (!bandwidth.equals("") && !CommonUitls.isNumeric(bandwidth))
		{
			System.out.println("Bandwidth is not a number.");
			return;
		}
		
		double interval = (tow-fromw)/(bandnum);
		String totalStr = "";
		
		for(int i=0;i<bandnum;i++){
			double centerband = fromw + i*interval + 0.5*interval;
			totalStr += Double.toString(centerband)+":";
			if(bandwidth.equals("")){
				totalStr += Double.toString(interval);
			}else{
				totalStr += bandwidth;
			}
			totalStr += ",";
		}
		totalStr = totalStr.substring(0, totalStr.length()-1);
		if(this.appendCheckBox.isSelected()){
			this.mwController.sensorBandsField.setText(this.mwController.sensorBandsField.getText()+","+totalStr);
		}
		else{
			this.mwController.sensorBandsField.setText(totalStr);
		}
		
		this.parentStage.close();
		
	}
	
	
}
