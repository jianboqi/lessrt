package less.gui.view;

import java.util.ArrayList;

import javafx.beans.value.ChangeListener;
import javafx.beans.value.ObservableValue;
import javafx.fxml.FXML;
import javafx.scene.chart.LineChart;
import javafx.scene.chart.NumberAxis;
import javafx.scene.chart.XYChart;
import javafx.scene.control.CheckBox;
import javafx.stage.Stage;
import less.gui.model.FacetOptical;

public class PlotSpectraController {
	@FXML
	LineChart<Number,Number> spectraLineChart;
	
	@FXML
	CheckBox FrontCheckBox;
	
	@FXML
	CheckBox BackCheckBox;
	
	@FXML
	CheckBox TransCheckBox;
	
	private XYChart.Series<Number,Number> series1 = new XYChart.Series<Number,Number>(); //front ref
	private XYChart.Series<Number,Number> series2 = new XYChart.Series<Number,Number>(); //back ref
	private XYChart.Series<Number,Number> series3 = new XYChart.Series<Number,Number>(); // trans
	
	private Stage parentStage;
	private LessMainWindowController mwController;
	
	public void setParentStage(Stage parentStage) {
		this.parentStage = parentStage;
	}
	
	public void setmwController(LessMainWindowController mwController){
		this.mwController = mwController;
	}
	
	public void initView(){
		spectraLineChart.setAnimated(false);		
		FacetOptical facetOptical = (FacetOptical) this.mwController.opticalTable.getSelectionModel().getSelectedItem();
		if(facetOptical != null) {
			parentStage.setTitle("Spectra-"+facetOptical.getOpticalName());
			NumberAxis xAxis = (NumberAxis)spectraLineChart.getXAxis();
			NumberAxis yAxis = (NumberAxis)spectraLineChart.getYAxis();
			
			spectraLineChart.setTitle(facetOptical.getOpticalName());
			xAxis.setLabel("Wavelength [nm]");
			xAxis.setForceZeroInRange(false);
			yAxis.setLabel("Reflectance/Transmittance");
			
			//Get wavelength
			ArrayList<Double> wavelengths = new ArrayList<Double>();
			String [] waveArr = this.mwController.sensorBandsField.getText().split(",");
			for(int i=0;i<waveArr.length;i++) {
				wavelengths.add(Double.parseDouble(waveArr[i].split(":")[0]));
			}
			
			
			series1.setName("Front Reflectance");
			ArrayList<Double> refFront = facetOptical.getReflectanceFrontAsList();
			for(int i=0;i<refFront.size();i++) {
				series1.getData().add(new XYChart.Data<Number,Number>(wavelengths.get(i), refFront.get(i)));
			}
			spectraLineChart.getData().add(series1);
			
			
			series2.setName("Back Reflectance");
			ArrayList<Double> refBack = facetOptical.getReflectanceBackAsList();
			for(int i=0;i<refFront.size();i++) {
				series2.getData().add(new XYChart.Data<Number,Number>(wavelengths.get(i), refBack.get(i)));
			}
			spectraLineChart.getData().add(series2);
			
			
			series3.setName("Transmittance");
			ArrayList<Double> refTrans = facetOptical.getTransmittanceAsList();
			for(int i=0;i<refTrans.size();i++) {
				series3.getData().add(new XYChart.Data<Number,Number>(wavelengths.get(i), refTrans.get(i)));
			}
			spectraLineChart.getData().add(series3);
		}
		
		RegisterCheckBoxEvents();
	}
	
	private void RegisterCheckBoxEvents() {
		FrontCheckBox.selectedProperty().addListener(new ChangeListener<Boolean>() {
			@Override
			public void changed(ObservableValue<? extends Boolean> observable, Boolean oldval, Boolean newVal) {
				if(!newVal) {
					spectraLineChart.getData().remove(series1);
				}else {
					spectraLineChart.getData().add(series1);
				}
			}
		});
		
		BackCheckBox.selectedProperty().addListener(new ChangeListener<Boolean>() {
			@Override
			public void changed(ObservableValue<? extends Boolean> observable, Boolean oldval, Boolean newVal) {
				if(!newVal) {
					spectraLineChart.getData().remove(series2);
				}else {
					spectraLineChart.getData().add(series2);
				}
				
			}
		});
		
		TransCheckBox.selectedProperty().addListener(new ChangeListener<Boolean>() {
			@Override
			public void changed(ObservableValue<? extends Boolean> observable, Boolean oldval, Boolean newVal) {
				if(!newVal) {
					spectraLineChart.getData().remove(series3);
				}else {
					spectraLineChart.getData().add(series3);
				}
				
			}
		});
	}
	
}
