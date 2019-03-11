package less.gui.view;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;

import javafx.beans.value.ChangeListener;
import javafx.beans.value.ObservableValue;
import javafx.fxml.FXML;
import javafx.scene.chart.LineChart;
import javafx.scene.chart.NumberAxis;
import javafx.scene.chart.XYChart;
import javafx.scene.chart.XYChart.Data;
import javafx.scene.control.Button;
import javafx.scene.control.CheckBox;
import javafx.scene.control.ListView;
import javafx.scene.layout.AnchorPane;
import javafx.scene.layout.StackPane;
import javafx.stage.Stage;
import less.gui.model.FacetOptical;
import less.gui.utils.Const;
import less.gui.utils.DBReader;

public class DBChooserController {
	
	@FXML
	private ListView<String> LambertListView;
	@FXML
	private Button dbOKBtn;
	
	@FXML
	LineChart<Number, Number> DBSpectraLineChart;
	
	@FXML
	CheckBox FrontCheckBox;
	
	@FXML
	CheckBox BackCheckBox;
	
	@FXML
	CheckBox TransCheckBox;
	
	@FXML
	CheckBox ShowFigureCheckBox;
	
	@FXML
	AnchorPane FigureAnchorPane;
	
	@FXML
	StackPane chartStackPane;
	
	private XYChart.Series<Number,Number> series1 = new XYChart.Series<Number,Number>(); //front ref
	private XYChart.Series<Number,Number> series2 = new XYChart.Series<Number,Number>(); //back ref
	private XYChart.Series<Number,Number> series3 = new XYChart.Series<Number,Number>(); // trans
	
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
		
		NumberAxis xAxis = (NumberAxis)DBSpectraLineChart.getXAxis();
		NumberAxis yAxis = (NumberAxis)DBSpectraLineChart.getYAxis();
		DBSpectraLineChart.setAnimated(false);
		DBSpectraLineChart.setCreateSymbols(false);
		
		xAxis.setLabel("Wavelength [nm]");
		xAxis.setForceZeroInRange(false);
		yAxis.setLabel("Reflectance/Transmittance");
		
		RegisterCheckBoxEvents();
		
		this.LambertListView.getSelectionModel().selectedItemProperty().addListener(new ChangeListener<String>() {
			
		    @SuppressWarnings("unchecked")
			@Override
		    public void changed(ObservableValue<? extends String> observable, String oldValue, String newValue) {
		    	if(newValue != null){
		    		dbOKBtn.setDisable(false);
		    		
		    		if(!ShowFigureCheckBox.isSelected()) {
		    			DBSpectraLineChart.getData().clear();
		    			return;
		    		}
		    			
		    		FrontCheckBox.setSelected(true);
		    		BackCheckBox.setSelected(true);
		    		TransCheckBox.setSelected(true);
		    		
		    		DBSpectraLineChart.getData().clear();
		    		//plot the selected spectra
		    		String objName = LambertListView.getSelectionModel().getSelectedItem();
		    		
		    		series1.getData().clear();
		    		series2.getData().clear();
		    		series3.getData().clear();
					String waveLength_and_bandwidth = mwController.sensorBandsField.getText().trim();
					ResultSet opticalSet = dbReader.getFullSpectraByName(objName);
					//ArrayList<Double> wavelengths = opticalArr.get(3);
					
					try {
						while(opticalSet.next()) {
							double front_ref = opticalSet.getDouble("front_ref");
							double back_ref = opticalSet.getDouble("back_ref");
							double transmittance = opticalSet.getDouble("transmittance");
							double wavelength = opticalSet.getDouble("wavelength");
							series1.getData().add(new XYChart.Data<Number,Number>(wavelength, front_ref));
							series2.getData().add(new XYChart.Data<Number,Number>(wavelength, back_ref));
							series3.getData().add(new XYChart.Data<Number,Number>(wavelength, transmittance));
						}
					} catch (SQLException e) {
						// TODO Auto-generated catch block
						e.printStackTrace();
					}
										
					series1.setName("Front Reflectance");
					DBSpectraLineChart.getData().add(series1);		
					
					series2.setName("Back Reflectance");
					DBSpectraLineChart.getData().add(series2);
							
					series3.setName("Transmittance");
					DBSpectraLineChart.getData().add(series3);
					
			        
		    	}else{
		    		dbOKBtn.setDisable(true);
		    	}
		    }
		});
	}
	
	private void RegisterCheckBoxEvents() {
		FrontCheckBox.selectedProperty().addListener(new ChangeListener<Boolean>() {
			@Override
			public void changed(ObservableValue<? extends Boolean> observable, Boolean oldval, Boolean newVal) {
				if(!newVal) {
					DBSpectraLineChart.getData().remove(series1);
				}else {
					DBSpectraLineChart.getData().add(series1);
				}
			}
		});
		
		BackCheckBox.selectedProperty().addListener(new ChangeListener<Boolean>() {
			@Override
			public void changed(ObservableValue<? extends Boolean> observable, Boolean oldval, Boolean newVal) {
				if(!newVal) {
					DBSpectraLineChart.getData().remove(series2);
				}else {
					DBSpectraLineChart.getData().add(series2);
				}
				
			}
		});
		
		TransCheckBox.selectedProperty().addListener(new ChangeListener<Boolean>() {
			@Override
			public void changed(ObservableValue<? extends Boolean> observable, Boolean oldval, Boolean newVal) {
				if(!newVal) {
					DBSpectraLineChart.getData().remove(series3);
				}else {
					DBSpectraLineChart.getData().add(series3);
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
