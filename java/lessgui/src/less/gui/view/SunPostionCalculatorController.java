package less.gui.view;

import java.util.GregorianCalendar;
import java.util.TimeZone;

import javafx.fxml.FXML;
import javafx.scene.control.TextField;
import javafx.stage.Stage;
import less.gui.model.SunPos;
import net.e175.klaus.solarpositioning.AzimuthZenithAngle;
import net.e175.klaus.solarpositioning.DeltaT;
import net.e175.klaus.solarpositioning.SPA;

public class SunPostionCalculatorController {
	@FXML
	private TextField yearTextField;
	@FXML
	private TextField monthTextField;
	@FXML
	private TextField dayTextField;
	@FXML
	private TextField hourTextField;
	@FXML
	private TextField minuteTextField;
	@FXML
	private TextField secondTextField;
	@FXML
	private TextField latTextField;
	@FXML
	private TextField lonTextField;
	@FXML
	private TextField timezoneTextField;
	@FXML
	private TextField AltitudeTextField;
	
	private Stage parentStage;
	private LessMainWindowController mwController;
	
	public void setParentStage(Stage parentStage) {
		this.parentStage = parentStage;
	}
	
	public void setmwController(LessMainWindowController mwController){
		this.mwController = mwController;
	}
	
	public void initView(){
		if(this.mwController.projManager.sunpos != null){
			SunPos sunPos = this.mwController.projManager.sunpos;
			this.yearTextField.setText(sunPos.year+"");
			this.monthTextField.setText(sunPos.month+"");
			this.dayTextField.setText(sunPos.day+"");
			this.hourTextField.setText(sunPos.hour+"");
			this.minuteTextField.setText(sunPos.minute+"");
			this.secondTextField.setText(sunPos.second+"");
			this.timezoneTextField.setText(sunPos.timezone+"");
			this.latTextField.setText(sunPos.lat+"");
			this.lonTextField.setText(sunPos.lon+"");
			this.AltitudeTextField.setText(sunPos.altitude+"");
		}
	}
	
	@FXML
	private void onOK(){
		SunPos sunPos = new SunPos();
		sunPos.year = Integer.parseInt(this.yearTextField.getText());
		sunPos.month = Integer.parseInt(this.monthTextField.getText());
		sunPos.day = Integer.parseInt(this.dayTextField.getText());
		sunPos.hour = Integer.parseInt(this.hourTextField.getText());
		sunPos.minute = Integer.parseInt(this.minuteTextField.getText());
		sunPos.second = Integer.parseInt(this.secondTextField.getText());
		sunPos.timezone = Integer.parseInt(this.timezoneTextField.getText());
		sunPos.lat = Double.parseDouble(this.latTextField.getText());
		sunPos.lon = Double.parseDouble(this.lonTextField.getText());
		sunPos.altitude = Double.parseDouble(this.AltitudeTextField.getText());
		this.mwController.projManager.sunpos = sunPos;
		
		GregorianCalendar gregorianCalendar = new GregorianCalendar(sunPos.year,
				sunPos.month, sunPos.day, sunPos.hour-sunPos.timezone, sunPos.minute,sunPos.second);
		gregorianCalendar.setTimeZone(TimeZone.getTimeZone("GMT"));
		AzimuthZenithAngle position = SPA.calculateSolarPosition(gregorianCalendar,
				sunPos.lat, sunPos.lon, sunPos.altitude, DeltaT.estimate(gregorianCalendar));
		
		this.mwController.sunAzimuthField.setText(position.getAzimuth()+"");
		this.mwController.sunZenithField.setText(position.getZenithAngle()+"");
		
		parentStage.close();
	}
	
	@FXML
	private void onCancel(){
		parentStage.close();
	}
}
