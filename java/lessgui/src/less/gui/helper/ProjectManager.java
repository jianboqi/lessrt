package less.gui.helper;

import java.awt.Desktop;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.CopyOption;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.concurrent.CountDownLatch;

import com.terminalfx.TerminalBuilder;
import com.terminalfx.TerminalTab;
import com.terminalfx.config.TerminalConfig;

import javafx.beans.value.ChangeListener;
import javafx.beans.value.ObservableValue;
import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.fxml.FXMLLoader;
import javafx.geometry.Insets;
import javafx.scene.Scene;
import javafx.scene.control.Button;
import javafx.scene.control.ComboBox;
import javafx.scene.control.Label;
import javafx.scene.control.ListView;
import javafx.scene.control.Tab;
import javafx.scene.control.TextField;
import javafx.scene.control.ToggleGroup;
import javafx.scene.image.Image;
import javafx.scene.layout.AnchorPane;
import javafx.scene.layout.BorderPane;
import javafx.scene.layout.HBox;
import javafx.scene.layout.VBox;
import javafx.scene.paint.Color;
import javafx.stage.FileChooser;
import javafx.stage.Modality;
import javafx.stage.Stage;
import less.LessMainApp;
import less.gui.model.PositionXY;
import less.gui.model.SunPos;
import less.gui.server.PyServer;
import less.gui.utils.Const;
import less.gui.view.BatchController;
import less.gui.view.HelpViewerController;
import less.gui.view.LAICalculatorController;
import less.gui.view.LessMainWindowController;
import less.gui.view.RunningOnClusterController;
import less.gui.view.SunPostionCalculatorController;

/**
 * Management about the project
 * @author Jim
 *
 */
public class ProjectManager {
	private LessMainWindowController mwController;
	private Button lcImportBtn=null;
	private ListView<String> landcoverTypeListview=null;
	private ComboBox<String> typeOpticalCombobox = null;
	
	private AnchorPane opticalThermalPane = null;
	public ObservableList<String> temperatureList = FXCollections.observableArrayList();
	public Label terrainTemperLabel = null;
	public ComboBox<String> comboBoxTerrainTemper = null;
	private TerminalTab terminal=null;
	
	
	private AnchorPane virtualPlanePane = null;
	public TextField xpos = null;
	public TextField ypos = null;
	public TextField zpos = null;
	public TextField xsizepos = null;
	public TextField ysizepos = null;
	
	/*************
	 * some status
	 *
	 */
	public boolean isNetworkSim = false; //
	public boolean isServerStarted = false; //
	public Process p;// 
	
	public SunPos sunpos = null;// 
	
	
	
	public ProjectManager(LessMainWindowController mwController){
		this.mwController = mwController;
	}
	
	public String getParameterDirPath(){
		String param_path = Paths.get(this.mwController.simulation_path, 
				this.mwController.constConfig.data.getString("input_dir")).toString();
		return param_path;
	}
	
	public String getResultsDirPath(){
		String result_path = Paths.get(this.mwController.simulation_path,
				this.mwController.constConfig.data.getString("output_dir")).toString();
		return result_path;
	}
	
	public void openResultFolder() {
		if (this.mwController.simulation_path == null){
			return;
		}
		if (Desktop.isDesktopSupported()) {
		    try {
				Desktop.getDesktop().open(new File(getResultsDirPath()));
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}
	}
	
	public void OpenBatchTool(){
		try {
			FXMLLoader loader = new FXMLLoader();
			loader.setLocation(BatchController.class.getResource("BatchController.fxml"));
			BorderPane rootLayout = (BorderPane) loader.load();
			Scene scene = new Scene(rootLayout);
			Stage subStage = new Stage();
			subStage.setScene(scene);
			subStage.setTitle("Batch Tool");
			BatchController btController = loader.getController();
			btController.setMainWindowController(this.mwController);
			btController.setParentStage(subStage);
			btController.initView();
			subStage.getIcons().add(new Image(LessMainApp.class.getResourceAsStream("LESS16_16.png")));
			subStage.getIcons().add(new Image(LessMainApp.class.getResourceAsStream("LESS32_32.png")));
			subStage.initOwner(this.mwController.mainApp.getPrimaryStage());
			subStage.show();
			
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
	
	public void copyDefaultConfigfile(){
		String defaultcfg = PyLauncher.getDefaultConf();
		String parameter_file_path = Paths.get(this.mwController.simulation_path,
				this.mwController.constConfig.data.getString("input_dir"),
				this.mwController.constConfig.data.getString("config_file")).toString();
		try {
			CopyOption[] options = new CopyOption[]{
                    StandardCopyOption.REPLACE_EXISTING,
                    StandardCopyOption.COPY_ATTRIBUTES
            };
			Files.copy(new File(defaultcfg).toPath(), new File(parameter_file_path).toPath(), options);
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
	
	public boolean isAreadyASimulation(){
		String parameter_file_path = Paths.get(this.mwController.simulation_path,
				this.mwController.constConfig.data.getString("input_dir"),
				this.mwController.constConfig.data.getString("config_file")).toString();
		if(new File(parameter_file_path).exists()){
			return true;
		}else{
			return false;
		}
	}
	
	public void clear_proj(){
		for(Map.Entry<String, ObservableList<PositionXY>> entry: this.mwController.objectAndPositionMap.entrySet()){
			entry.getValue().clear();
		}
		this.mwController.objectAndPositionMap.clear();
		this.mwController.objectsList.clear();
		this.mwController.objectsAndCompomentsMap.clear();
		this.mwController.reDrawAll();
	}
	
	
	
	/*****************************************************
	 * import tree positions from CHM map
	 */
	
	public void treePosFromCHM(){
		//
		ObservableList<String> selectedObjs = this.mwController.objectLV.getSelectionModel().getSelectedItems();
		if(selectedObjs.size() == 0){//
			System.out.println("Please choose at least one object to populate.");
			return;
		}
		
		
		FileChooser fileChooser = new FileChooser();
		String lastOpened = this.mwController.getLastOpenedPath(Const.LAST_OPNED_CHM_FILE_PATH);
		if (lastOpened != null && new File(lastOpened).exists()){
			fileChooser.setInitialDirectory(new File(lastOpened));
		}
		fileChooser.getExtensionFilters().add(new FileChooser.ExtensionFilter("ENVI Standard", "*.*"));
		fileChooser.getExtensionFilters().add(new FileChooser.ExtensionFilter("Geotiff", "*.tif"));
		File file = fileChooser.showOpenDialog(this.mwController.mainApp.getPrimaryStage());
        if(file !=null)
        {
        	this.mwController.setLastOpenedPath(Const.LAST_OPNED_CHM_FILE_PATH,file.getParent().toString());
        	//object name list
        	String tString = "";
        	String tStringRadius = "";//object radius list
        	String tStringHeights = "";//height list
        	for(int i=0;i<selectedObjs.size();i++){
        		tString += selectedObjs.get(i) + "*";
        		tStringRadius += this.mwController.objectAndBoundingboxMap.get(selectedObjs.get(i)).getMaxDiameter() + "*";
        		tStringHeights += this.mwController.objectAndBoundingboxMap.get(selectedObjs.get(i)).getHeight() + "*";
        	}
        	tString = tString.substring(0, tString.length()-1);
        	tStringRadius = tStringRadius.substring(0, tStringRadius.length()-1);
        	tStringHeights = tStringHeights.substring(0,tStringHeights.length()-1);
        	CountDownLatch latch = new CountDownLatch(1);
    		this.mwController.currentPyLaucherThread = new PyLauncher();
    		this.mwController.currentPyLaucherThread.setLessMainController(this.mwController);
    		this.mwController.currentPyLaucherThread.prepare(this.mwController.simulation_path, PyLauncher.Operation.RUN_TREE_DETECTION, latch, this.mwController.outputConsole);
    		this.mwController.currentPyLaucherThread.setTmpData(file.toString());
    		this.mwController.currentPyLaucherThread.setTmpData2(tString);
    		this.mwController.currentPyLaucherThread.setTmpData3(tStringRadius);
    		this.mwController.currentPyLaucherThread.setTmpData4(tStringHeights);
    		this.mwController.currentRunningStatusThread = new RunningStatusThread(this.mwController.currentPyLaucherThread, this.mwController.outputConsole, this.mwController.runBtn);
    		this.mwController.currentRunningStatusThread.setMainController(this.mwController);
    		this.mwController.currentRunningStatusThread.start();
        }	
	}
	public void treePosFromCHM_PostProcessing(){
		for(Map.Entry<String, ObservableList<PositionXY>> entry: this.mwController.objectAndPositionMap.entrySet()){
			entry.getValue().clear();
		}	
		this.mwController.load_instances_file();
	}
	
	public void onDisplayPosOn2DCheck(){
		this.mwController.reDrawAll();
	}
	
	public void onHideSelectedOn2DCheck(){
		this.mwController.reDrawAll();
	}
	
	public void OpenAboutDialog(){
		FXMLLoader loader = new FXMLLoader();
		loader.setLocation(LessMainWindowController.class.getResource("About.fxml"));
		try {
			BorderPane rootLayout = (BorderPane) loader.load();
			Scene scene = new Scene(rootLayout);
			Stage aboutStage = new Stage();
			aboutStage.setScene(scene);
			aboutStage.setTitle("About");
			aboutStage.getIcons().add(new Image(LessMainApp.class.getResourceAsStream("LESS16_16.png")));
			aboutStage.getIcons().add(new Image(LessMainApp.class.getResourceAsStream("LESS32_32.png")));
			aboutStage.initOwner(this.mwController.mainApp.getPrimaryStage());
			aboutStage.setResizable(false);
			aboutStage.initModality(Modality.WINDOW_MODAL);
			aboutStage.showAndWait();
			
			
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
	
	/*****************************************************
	 * Terrain and LandCover
	 */
	public void selectTerrainFile(){
		if(this.mwController.simulation_path == null){
			this.mwController.outputConsole.log("Please create a simulation first.\n");
			   return;
			}
			Path initPath = Paths.get(this.mwController.simulation_path);
			FileChooser fileChooser = new FileChooser();
			File initDirectory = new File(initPath.normalize().toString());
			fileChooser.setInitialDirectory(initDirectory);
	        // Set extension filter
	        if(this.mwController.comboBoxDEMType.getSelectionModel().getSelectedItem().equals(Const.LESS_TERRAIN_RASTER)){
//	        	fileChooser.getExtensionFilters().add(new FileChooser.ExtensionFilter("Geotiff", "*.tif"));
	        	fileChooser.getExtensionFilters().add(new FileChooser.ExtensionFilter("ENVI Standard", "*.*"));
	        }
	        if(this.mwController.comboBoxDEMType.getSelectionModel().getSelectedItem().equals(Const.LESS_TERRAIN_MESH)){
	        	fileChooser.getExtensionFilters().add(new FileChooser.ExtensionFilter("OBJ Mesh", "*.obj"));
	        }
	        // Show open file dialog
	        File file = fileChooser.showOpenDialog(this.mwController.mainApp.getPrimaryStage());
	        if(file !=null)
	        {
	        	//copy this to the folder of paramters
	        	String param_path = this.getParameterDirPath();
	        	CopyOption[] options = new CopyOption[]{
	                    StandardCopyOption.REPLACE_EXISTING,
	                    StandardCopyOption.COPY_ATTRIBUTES
	            };
	        	try {
					Files.copy(file.toPath(), Paths.get(param_path,file.getName()), options);
					if(fileChooser.getSelectedExtensionFilter().getExtensions().get(0).equals("*.*")){
						Files.copy(Paths.get(file.toString()+".hdr"), Paths.get(param_path,file.getName()+".hdr"), options);
					}
				} catch (IOException e) {
					e.printStackTrace();
				}
	        	this.mwController.terrFileField.setText(file.getName());
	        }
	}
	
	//�ر���
	public void handleLandcoverCheckbox(){
		if(this.mwController.simulation_path == null){
			 this.mwController.outputConsole.log("Please create a simulation first.\n");
			   return;
		}
		if(this.mwController.landcoverCheckbox.isSelected()){
			// add new controller
			lcImportBtn = new Button();
			lcImportBtn.setText("Import");
			this.mwController.landcoverAnchorPane.getChildren().add(lcImportBtn);
			AnchorPane.setTopAnchor(lcImportBtn, 45.0);
			landcoverTypeListview = new ListView<String>();
			this.mwController.landcoverAnchorPane.getChildren().add(landcoverTypeListview);
			AnchorPane.setTopAnchor(landcoverTypeListview, 85.0);
			
			typeOpticalCombobox = new ComboBox<String>();
			typeOpticalCombobox.setItems(this.mwController.terrainOpticalData);
			typeOpticalCombobox.getSelectionModel().select(Const.LESS_DEFAULT_OPTICAL2);
			this.mwController.landcoverAnchorPane.getChildren().add(typeOpticalCombobox);
			AnchorPane.setTopAnchor(typeOpticalCombobox, 85.0);
			AnchorPane.setLeftAnchor(typeOpticalCombobox, 270.0);
			typeOpticalCombobox.setDisable(true);
			
			this.mwController.landcoverTypesOpticalMap = new HashMap<String, String>();
			
			
			lcImportBtn.setOnAction((event) -> {
				FileChooser fileChooser = new FileChooser();
				String lastOpened = this.mwController.getLastOpenedPath(Const.LAST_OPNED_CHOOSE_LANDCOVER);
				if (lastOpened != null && new File(lastOpened).exists()){
					fileChooser.setInitialDirectory(new File(lastOpened));
				}
				fileChooser.getExtensionFilters().add(new FileChooser.ExtensionFilter("ENVI Standard", "*.*"));
				File file = fileChooser.showOpenDialog(this.mwController.mainApp.getPrimaryStage());
				if(file !=null)
		        {
					this.mwController.setLastOpenedPath(Const.LAST_OPNED_CHOOSE_LANDCOVER,file.getParent().toString());
					//copy this to the folder of paramters
		        	String param_path = this.getParameterDirPath();
		        	CopyOption[] options = new CopyOption[]{
		                    StandardCopyOption.REPLACE_EXISTING,
		                    StandardCopyOption.COPY_ATTRIBUTES
		            };
		        	try {
						Files.copy(file.toPath(), Paths.get(param_path,this.mwController.constConfig.data.getString("imported_landcover_raster_name")), options);
						if(fileChooser.getSelectedExtensionFilter().getExtensions().get(0).equals("*.*")){
							Files.copy(Paths.get(file.toString()+".hdr"), Paths.get(param_path,this.mwController.constConfig.data.getString("imported_landcover_raster_name")+".hdr"), options);
						}
					} catch (IOException e) {
						e.printStackTrace();
					}
		        	landcoverTypeListview.getItems().clear();
		        	//read file using python extract land cover types
		        	ProcessBuilder pd = new ProcessBuilder(PyLauncher.getPyexe(),
		        	PyLauncher.getUtilityScriptsPath(Const.LESS_UTILITY_SCRIPT_LCTYPES),"-i",file.toString());
		        	pd.directory(new File(param_path));
		        	ArrayList<String> typeNames = PyLauncher.runUtilityscripts(pd, this.mwController.outputConsole, "LandCoverTypes");       	
		        	landcoverTypeListview.getItems().addAll(typeNames);
		        	for(int i=0;i<typeNames.size();i++){
		        		this.mwController.landcoverTypesOpticalMap.put(typeNames.get(i), typeOpticalCombobox.getSelectionModel().getSelectedItem());
		        	}
		        	
		        }  
			});
			
			//listview event
			landcoverTypeListview.getSelectionModel().selectedItemProperty().addListener(new ChangeListener<String>() {
				
			    @SuppressWarnings("unchecked")
				@Override
			    public void changed(ObservableValue<? extends String> observable, String oldValue, String newValue) {
			    	if(newValue != null){
			    		typeOpticalCombobox.setDisable(false);
			    		typeOpticalCombobox.getSelectionModel().select(mwController.landcoverTypesOpticalMap.get(newValue));
			    	}
			    }
			});
			
			//combobox event
			typeOpticalCombobox.valueProperty().addListener(new ChangeListener<String>() {
				@Override 
				public void changed(ObservableValue ov, String oldVal, String newVal) {
					if(newVal != null){
						String typeName = landcoverTypeListview.getSelectionModel().getSelectedItem();
						if(typeName != null){
							mwController.landcoverTypesOpticalMap.put(typeName, newVal);
						}
					}
				}
			});
				
		}else{
			if(lcImportBtn !=null)
				this.mwController.landcoverAnchorPane.getChildren().remove(lcImportBtn);
			if(landcoverTypeListview !=null)
				this.mwController.landcoverAnchorPane.getChildren().remove(landcoverTypeListview);
			if(typeOpticalCombobox !=null)
				this.mwController.landcoverAnchorPane.getChildren().remove(typeOpticalCombobox);
			String param_path = this.getParameterDirPath();
			File landcoverFile = Paths.get(param_path, Const.LESS_TERRAIN_LANDCOVER_FILE).toFile();
			if(landcoverFile.exists()){
				try {
					Files.delete(landcoverFile.toPath());
				} catch (IOException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
			}
		}
		
		
	}
	
	//save landcover
	public void saveLandcover2File(){
		if(this.mwController.landcoverCheckbox.isSelected()){
			String param_path = this.getParameterDirPath();
			File landcoverFile = Paths.get(param_path, Const.LESS_TERRAIN_LANDCOVER_FILE).toFile();
			BufferedWriter writer = null;
			try {
				writer = new BufferedWriter( new FileWriter(landcoverFile));
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
			
			for(Iterator<Map.Entry<String, String>> iterator = this.mwController.landcoverTypesOpticalMap.entrySet().iterator();iterator.hasNext();){
				Map.Entry<String,String> entry = iterator.next();
				String typeName = entry.getKey();
				String opticalName = entry.getValue();
				try {
					writer.write(typeName+" "+opticalName+"\n");
				} catch (IOException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
			}
			try {
				writer.close();
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
			
			
		}
	}
	
	//�Ƿ񸲸�ȫ������
	public void handleWholeSceneCheckbox(){
		if(this.mwController.CoverWholeSceneCheckbox.isSelected()){
			this.mwController.sensorXExtentField.setDisable(true);
			this.mwController.sensorYExtentField.setDisable(true);
		}
		else{
			this.mwController.sensorXExtentField.setDisable(false);
			this.mwController.sensorYExtentField.setDisable(false);
		}
		this.mwController.sensorXExtentField.setText(this.mwController.sceneXSizeField.getText());
		this.mwController.sensorYExtentField.setText(this.mwController.sceneYSizeField.getText());
	}
	
	//����virtual plane
	public void handlePlaneCheckbox(){
		if(this.mwController.virtualPlaneCheckbox.isSelected()){
			if (virtualPlanePane != null)
				return;
			
			virtualPlanePane = new AnchorPane();
			virtualPlanePane.setPrefHeight(60);
			this.mwController.sensorVbox.getChildren().add(this.mwController.sensorVbox.getChildren().size()-1, virtualPlanePane);
			Label labelCenter = new Label("Center:");
			AnchorPane.setTopAnchor(labelCenter, 10.0);
			AnchorPane.setLeftAnchor(labelCenter, 5.0);
			virtualPlanePane.getChildren().add(labelCenter);
			Label labelX = new Label("X:");
			AnchorPane.setTopAnchor(labelX, 10.0);
			AnchorPane.setLeftAnchor(labelX, 150.0);
			virtualPlanePane.getChildren().add(labelX);
			
			xpos = new TextField();
			xpos.setPrefWidth(70);
			AnchorPane.setTopAnchor(xpos, 5.0);
			AnchorPane.setLeftAnchor(xpos, 200.0);
			virtualPlanePane.getChildren().add(xpos);
			
			Label labelY = new Label("Y:");
			AnchorPane.setTopAnchor(labelY, 10.0);
			AnchorPane.setLeftAnchor(labelY, 290.0);
			virtualPlanePane.getChildren().add(labelY);
			
			ypos = new TextField();
			ypos.setPrefWidth(70);
			AnchorPane.setTopAnchor(ypos, 5.0);
			AnchorPane.setLeftAnchor(ypos, 340.0);
			virtualPlanePane.getChildren().add(ypos);
			
			Label labelZ = new Label("Z:");
			AnchorPane.setTopAnchor(labelZ, 10.0);
			AnchorPane.setLeftAnchor(labelZ, 450.0);
			virtualPlanePane.getChildren().add(labelZ);
			
			zpos = new TextField();
			zpos.setPrefWidth(70);
			AnchorPane.setTopAnchor(zpos, 5.0);
			AnchorPane.setLeftAnchor(zpos, 510.0);
			virtualPlanePane.getChildren().add(zpos);
			
			//seize
			Label labelSize = new Label("Size:");
			AnchorPane.setTopAnchor(labelSize, 50.0);
			AnchorPane.setLeftAnchor(labelSize, 5.0);
			virtualPlanePane.getChildren().add(labelSize);
			
			Label labelXSize = new Label("XSize:");
			AnchorPane.setTopAnchor(labelXSize, 50.0);
			AnchorPane.setLeftAnchor(labelXSize, 150.0);
			virtualPlanePane.getChildren().add(labelXSize);
			
			xsizepos = new TextField();
			xsizepos.setPrefWidth(70);
			AnchorPane.setTopAnchor(xsizepos, 45.0);
			AnchorPane.setLeftAnchor(xsizepos, 200.0);
			virtualPlanePane.getChildren().add(xsizepos);
			
			Label labelYSize = new Label("YSize:");
			AnchorPane.setTopAnchor(labelYSize, 50.0);
			AnchorPane.setLeftAnchor(labelYSize, 290.0);
			virtualPlanePane.getChildren().add(labelYSize);
			
			ysizepos = new TextField();
			ysizepos.setPrefWidth(70);
			AnchorPane.setTopAnchor(ysizepos, 45.0);
			AnchorPane.setLeftAnchor(ysizepos, 340.0);
			virtualPlanePane.getChildren().add(ysizepos);
			
			double xExtend = Double.parseDouble(this.mwController.sceneXSizeField.getText().replaceAll(",", ""));
			double yExtend = Double.parseDouble(this.mwController.sceneYSizeField.getText().replaceAll(",", ""));
			xsizepos.setText(this.mwController.sensorXExtentField.getText().replaceAll(",", ""));
			ysizepos.setText(this.mwController.sensorYExtentField.getText().replaceAll(",", ""));
			xpos.setText(""+xExtend*0.5);
			ypos.setText(""+yExtend*0.5);
			zpos.setText("MAX");
			
			if(this.mwController.comboBoxSensorType.getSelectionModel().getSelectedItem().equals(Const.LESS_SENSOR_TYPE_ORTH)){				
				this.mwController.sensorXExtentField.setDisable(true);
				this.mwController.sensorYExtentField.setDisable(true);
				this.mwController.CoverWholeSceneCheckbox.setDisable(true);
				this.xpos.setDisable(true);
				this.ypos.setDisable(true);
				xsizepos.textProperty().addListener((observable, oldValue, newValue) -> {
				    if(!newValue.equals("")){
				    	this.mwController.sensorXExtentField.setText(newValue);
				    }
				});
				
				ysizepos.textProperty().addListener((observable, oldValue, newValue) -> {
				    if(!newValue.equals("")){
				    	this.mwController.sensorYExtentField.setText(newValue);
				    }
				});
			}	
			
			
		}else{
			if(this.virtualPlanePane != null){
				this.mwController.sensorVbox.getChildren().remove(virtualPlanePane);
				virtualPlanePane = null;
				if(this.mwController.comboBoxSensorType.getSelectionModel().getSelectedItem().equals(Const.LESS_SENSOR_TYPE_ORTH)){				
					this.mwController.sensorXExtentField.setDisable(false);
					this.mwController.sensorYExtentField.setDisable(false);
					this.mwController.CoverWholeSceneCheckbox.setDisable(false);
					this.xpos.setDisable(false);
					this.ypos.setDisable(false);
				}
			}
		}
	}
	
	
	//�����ȷ���
	public void handleThermalRadiationCheckbox(){
		
		if(this.mwController.ThermalCheckbox.isSelected()){
			
			opticalThermalPane = new AnchorPane();
			this.mwController.opticalAnchorPane.getChildren().addAll(opticalThermalPane);
			AnchorPane.setLeftAnchor(opticalThermalPane, 0.0);
			AnchorPane.setRightAnchor(opticalThermalPane, 0.0);
			AnchorPane.setTopAnchor(opticalThermalPane, 400.0);
			
			Button addBtn = new Button("Add");
			Button delBtn = new Button("Del");
			AnchorPane.setLeftAnchor(addBtn, 180.0);
			AnchorPane.setTopAnchor(addBtn, 30.0);
			AnchorPane.setLeftAnchor(delBtn, 260.0);
			AnchorPane.setTopAnchor(delBtn, 30.0);
			TextField temperNameField = new TextField();
			temperNameField.setPrefWidth(150);
			temperNameField.setPromptText("Name");
			AnchorPane.setTopAnchor(temperNameField, 30.0);
			AnchorPane.setLeftAnchor(temperNameField, 0.0);
			
			Label tempLabel = new Label("Temperature Definition[K]:");
			AnchorPane.setLeftAnchor(tempLabel, 0.0);
			AnchorPane.setTopAnchor(tempLabel, 0.0);
			
			ListView<String> temperListView = new ListView<String>();
			temperListView.setPrefHeight(200);
			AnchorPane.setLeftAnchor(temperListView, 0.0);
			AnchorPane.setTopAnchor(temperListView, 80.0);
			temperListView.setItems(this.temperatureList);
			this.temperatureList.clear();
			this.temperatureList.add("T300");
			this.mwController.temperatureMap.put("T300", "300");
			
			
			TextField temperValField = new TextField();
			temperValField.setPromptText("300");
			temperValField.setPrefWidth(150);
			AnchorPane.setLeftAnchor(temperValField, 260.0);
			AnchorPane.setTopAnchor(temperValField, 80.0);
		
			opticalThermalPane.getChildren().addAll(tempLabel, addBtn,delBtn,temperNameField,temperListView,temperValField);
			
			//show for terrain
			terrainTemperLabel = new Label("Temperature: ");
			comboBoxTerrainTemper = new ComboBox<String>();
			comboBoxTerrainTemper.setPrefWidth(224);
			comboBoxTerrainTemper.setItems(this.temperatureList);
			comboBoxTerrainTemper.getSelectionModel().select(Const.LESS_DEFAULT_TEMPERATURE);
			this.mwController.terrainOpticalAnchorPane.getChildren().addAll(terrainTemperLabel, comboBoxTerrainTemper);
			AnchorPane.setLeftAnchor(terrainTemperLabel, 0.0);
			AnchorPane.setTopAnchor(terrainTemperLabel, 50.0);
			AnchorPane.setLeftAnchor(comboBoxTerrainTemper, 150.0);
			AnchorPane.setTopAnchor(comboBoxTerrainTemper, 45.0);
			
			
			temperListView.getSelectionModel().selectedItemProperty().addListener(new ChangeListener<String>() {
				@Override
			    public void changed(ObservableValue<? extends String> observable, String oldValue, String newValue) {
			    	if(newValue != null){
			    		temperValField.setText(mwController.temperatureMap.get(newValue));
			    	}
			    }
			});
			
			addBtn.setOnAction((event) -> {
				String temperName = temperNameField.getText();
				if(!temperName.equals("") && !temperatureList.contains(temperName)){
					temperatureList.add(temperName);
					mwController.temperatureMap.put(temperName, "300");
				}
			});
			
			delBtn.setOnAction((event) -> {
				String temperName = temperListView.getSelectionModel().getSelectedItem();
				if(!temperName.equals("")){
					temperatureList.remove(temperName);
					mwController.temperatureMap.remove(temperName);
				}
			});
			
			temperValField.textProperty().addListener((observable, oldValue, newValue) -> {
				mwController.temperatureMap.put(temperListView.getSelectionModel().getSelectedItem(), newValue);
			});
			
			
		}else{
			if(opticalThermalPane !=null){
				this.mwController.opticalAnchorPane.getChildren().remove(opticalThermalPane);
			}
			if (terrainTemperLabel != null){
				this.mwController.terrainOpticalAnchorPane.getChildren().remove(terrainTemperLabel);
			}
			if (comboBoxTerrainTemper != null){
				this.mwController.terrainOpticalAnchorPane.getChildren().remove(comboBoxTerrainTemper);
			}
		}
		
		
	}
	
	public void save_hidden_object_list(){
		String param_path = this.mwController.projManager.getParameterDirPath();
		String hidden_file = Paths.get(param_path, Const.LESS_HIDE_OBJECT_FILE_NAME).toString();
		
		if(!new File(hidden_file).getParentFile().exists())
			return;
		
		BufferedWriter writer = null;
		try {
			writer = new BufferedWriter( new FileWriter(hidden_file));
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		if(this.mwController.HideSelectedCheck.isSelected()){
			ObservableList<String>  tobeHide = this.mwController.objectLV.getSelectionModel().getSelectedItems();
			for (String objName : tobeHide) {
				try {
					writer.write(objName + System.lineSeparator());
				} catch (IOException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
			}
			
		}
		try {
			writer.close();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
	
	
	public void readLandcover2File(){
		String param_path = this.getParameterDirPath();
		File landcoverFile = Paths.get(param_path, Const.LESS_TERRAIN_LANDCOVER_FILE).toFile();
		if(landcoverFile.exists()){
			try (BufferedReader reader = new BufferedReader(new FileReader(landcoverFile))) {
		        String line;
		        int objnum = 0;
		        while ((line = reader.readLine()) != null){
		        	String [] arr = line.split(" ");    
		        	this.landcoverTypeListview.getItems().add(arr[0]);
		        	this.mwController.landcoverTypesOpticalMap.put(arr[0], arr[1]);
		        }
		} catch (FileNotFoundException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
	}
	
	}
	
	
	
	/**
	 *
	 */
	public void RunOnCluster(){
		FXMLLoader loader = new FXMLLoader();
		loader.setLocation(RunningOnClusterController.class.getResource("RunningOnClusterView.fxml"));
		try {
			BorderPane rootLayout = (BorderPane) loader.load();
			Scene scene = new Scene(rootLayout);
			Stage clusterStage = new Stage();
			clusterStage.setScene(scene);
			clusterStage.setTitle("Server Setting");
			RunningOnClusterController clusterController = loader.getController();
			clusterController.setLessMainController(this.mwController);
			clusterController.setParentStage(clusterStage);
			clusterController.initView();
			
			clusterStage.getIcons().add(new Image(LessMainApp.class.getResourceAsStream("LESS16_16.png")));
			clusterStage.getIcons().add(new Image(LessMainApp.class.getResourceAsStream("LESS32_32.png")));
			clusterStage.initOwner(this.mwController.mainApp.getPrimaryStage());
			clusterStage.setResizable(false);
			clusterStage.show();
			
			
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
	
	/**
	 * 
	 */
	public void RunPythonConsole(){		
		TerminalConfig pythonConfig = new TerminalConfig();
		String startup_scripts = PyLauncher.getScriptsPath(Const.LESS_PYTHON_STARTUP_SCRIPT);
		String cmd = PyLauncher.getPyexe();
		String params = " -i "+startup_scripts + " -p "+ this.mwController.simulation_path;
		params += " -x " + this.mwController.sceneXSizeField.getText().replaceAll(",", "");
		params += " -y " + this.mwController.sceneYSizeField.getText().replaceAll(",", "");
		
		pythonConfig.setWindowsTerminalStarter(cmd+params);
		pythonConfig.setFontSize(16);
		pythonConfig.setForegroundColor(Color.rgb(0, 0, 255));
		TerminalBuilder terminalBuilder = new TerminalBuilder(pythonConfig);
		if(this.mwController.simulation_path!=null)
			terminalBuilder.setTerminalPath(Paths.get(this.mwController.simulation_path));
		
		if(this.mwController.ConsoleTabPane.getTabs().contains(terminal)){
			terminal.closeTerminal();
			this.mwController.ConsoleTabPane.getTabs().remove(terminal);
		}
		terminal = terminalBuilder.newTerminal();
		terminal.setText("Python Console");

		this.mwController.ConsoleTabPane.getTabs().add(terminal);
		this.mwController.ConsoleTabPane.getSelectionModel().select(terminal);
	}
	
	public void closingAllPyConsole(){
		ObservableList<Tab> tabs = FXCollections.observableArrayList(this.mwController.ConsoleTabPane.getTabs());
        for (Tab tab : tabs) {
            if (tab instanceof TerminalTab) {
                 ((TerminalTab) tab).closeTerminal();
            }
        }
	}
	
	/**
	 * 
	 */
	public void RunLAICalculator(){
		FXMLLoader loader = new FXMLLoader();
		loader.setLocation(LAICalculatorController.class.getResource("LAICalculatorView.fxml"));
		try {
			BorderPane rootLayout = (BorderPane) loader.load();
			Scene scene = new Scene(rootLayout);
			Stage laiStage = new Stage();
			laiStage.setScene(scene);
			laiStage.setTitle("LAI Calculator");
			LAICalculatorController laiCalculatorController = loader.getController();
			laiCalculatorController.setParentStage(laiStage);
			laiCalculatorController.setmwController(this.mwController);
			laiCalculatorController.initView();
			laiStage.getIcons().add(new Image(LessMainApp.class.getResourceAsStream("LESS16_16.png")));
			laiStage.getIcons().add(new Image(LessMainApp.class.getResourceAsStream("LESS32_32.png")));
			laiStage.initOwner(this.mwController.mainApp.getPrimaryStage());
			laiStage.show();
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
	
	
	public void OpenSunPosCalculator(){
		FXMLLoader loader = new FXMLLoader();
		loader.setLocation(SunPostionCalculatorController.class.getResource("SunPositionCalculatorView.fxml"));
		try {
			BorderPane rootLayout = (BorderPane) loader.load();
			Scene scene = new Scene(rootLayout);
			Stage sunStage = new Stage();
			sunStage.setScene(scene);
			sunStage.setTitle("Sun Position Calculator");
			SunPostionCalculatorController sunPostionCalculatorController = loader.getController();
			sunPostionCalculatorController.setParentStage(sunStage);
			sunPostionCalculatorController.setmwController(this.mwController);
			sunPostionCalculatorController.initView();
			sunStage.getIcons().add(new Image(LessMainApp.class.getResourceAsStream("LESS16_16.png")));
			sunStage.getIcons().add(new Image(LessMainApp.class.getResourceAsStream("LESS32_32.png")));
			sunStage.initOwner(this.mwController.mainApp.getPrimaryStage());
			sunStage.setResizable(false);
			sunStage.show();
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
	
	//start helpviwer
	public void startHelpViewer(){
		
		String url = "http://ramm.bnu.edu.cn/projects/less/Documentation/#observation";
		
		
		FXMLLoader loader = new FXMLLoader();
		loader.setLocation(HelpViewerController.class.getResource("HelpViewer.fxml"));
		try {
			BorderPane rootLayout = (BorderPane) loader.load();
			Scene scene = new Scene(rootLayout);
			Stage helpStage = new Stage();
			helpStage.setScene(scene);
			helpStage.setTitle("Helper");
			HelpViewerController helpViewerController = loader.getController();
//			helpViewerController.setParentStage(helpStage);
//			helpViewerController.setmwController(this.mwController);
			helpViewerController.initView(url);
			helpStage.getIcons().add(new Image(LessMainApp.class.getResourceAsStream("LESS16_16.png")));
			helpStage.getIcons().add(new Image(LessMainApp.class.getResourceAsStream("LESS32_32.png")));
			helpStage.initOwner(this.mwController.mainApp.getPrimaryStage());
			helpStage.setResizable(false);
			helpStage.show();
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
	
	private void createPhotonTracingConfigPanel(){
		mwController.ptConfigPanel = new AnchorPane();
		Label illumResolution = new Label("Illumination Resolution:");
		mwController.ptConfigPanel.getChildren().add(illumResolution);
		AnchorPane.setLeftAnchor(illumResolution, 0.0);
		mwController.illumResTextField = new TextField("0.02");
		mwController.ptConfigPanel.getChildren().add(mwController.illumResTextField);
		AnchorPane.setLeftAnchor(mwController.illumResTextField, 150.0);
		AnchorPane.setRightAnchor(mwController.illumResTextField, 20.0);
		AnchorPane.setTopAnchor(illumResolution, 5.0);
	}

	//sensor
	public void initSensor(){
		
		createPhotonTracingConfigPanel();
					
		//init radio button for rgb and spectrum
		this.mwController.ImageFormatRadioroup = new ToggleGroup();
		this.mwController.spectrumRadio.setToggleGroup(this.mwController.ImageFormatRadioroup);
		this.mwController.spectrumRadio.setSelected(true);
		this.mwController.spectrumRadio.setUserData(Const.LESS_OUT_IMAGEFORMAT_SPECTRUM);
		this.mwController.rgbRadio.setToggleGroup(this.mwController.ImageFormatRadioroup);
		this.mwController.rgbRadio.setSelected(false);
		this.mwController.rgbRadio.setUserData(Const.LESS_OUT_IMAGEFORMAT_RGB);
		
		this.mwController.sensorVbox.getChildren().remove(this.mwController.perspectivePane);
		this.mwController.obsVbox.getChildren().remove(this.mwController.obsPerspectivePane);
		this.mwController.comboBoxSensorType.valueProperty().addListener(new ChangeListener<String>() {
			@Override 
			public void changed(ObservableValue ov, String oldVal, String newVal) {
				if (newVal.equals(Const.LESS_SENSOR_TYPE_ORTH)){
					mwController.sensorVbox.getChildren().remove(mwController.perspectivePane);
					mwController.sensorVbox.getChildren().add(mwController.orthographicPane);
					mwController.obsVbox.getChildren().remove(mwController.obsPerspectivePane);
					mwController.obsVbox.getChildren().add(mwController.obsOrthographicPane);
					mwController.pixelUnitLabel.setText("Samples [m-2]:");
					mwController.sensorVbox.getChildren().remove(mwController.ptConfigPanel);
					mwController.reDrawAll();
				}
				if(newVal.equals(Const.LESS_SENSOR_TYPE_PER)){
					mwController.sensorVbox.getChildren().remove(mwController.orthographicPane);
					mwController.sensorVbox.getChildren().add(mwController.perspectivePane);
					mwController.obsVbox.getChildren().remove(mwController.obsOrthographicPane);
					mwController.obsVbox.getChildren().add(mwController.obsPerspectivePane);
					mwController.pixelUnitLabel.setText("Samples [/pixel]:");
					mwController.sensorVbox.getChildren().remove(mwController.ptConfigPanel);
					mwController.reDrawAll();
				}
				if(newVal.equals(Const.LESS_SENSOR_TYPE_PT)){
					mwController.sensorVbox.getChildren().remove(mwController.orthographicPane);
					mwController.sensorVbox.getChildren().remove(mwController.perspectivePane);
					mwController.obsVbox.getChildren().remove(mwController.obsPerspectivePane);
					mwController.obsVbox.getChildren().remove(mwController.obsOrthographicPane);
					mwController.sensorVbox.getChildren().add(mwController.ptConfigPanel);
					VBox.setMargin(mwController.ptConfigPanel, new Insets(15,0,0,0));
					mwController.reDrawAll();
				}
			}
		});
	}
		
	
	//lab 
	public void PyJavaCommunication(){
		PyServer pyServer = new PyServer();
		pyServer.setMainConroller(this.mwController);
		Thread testA=new Thread(pyServer);  
        testA.start();  
	}
}
