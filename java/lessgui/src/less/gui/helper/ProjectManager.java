package less.gui.helper;

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
import javafx.event.ActionEvent;
import javafx.event.EventHandler;
import javafx.fxml.FXMLLoader;
import javafx.geometry.Insets;
import javafx.scene.Scene;
import javafx.scene.control.Button;
import javafx.scene.control.CheckBox;
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
import less.gui.model.AtmosphereParams;
import less.gui.model.FacetOptical;
import less.gui.model.PositionXY;
import less.gui.model.ProspectDParams;
import less.gui.model.SunPos;
import less.gui.server.PyServer;
import less.gui.utils.Const;
import less.gui.view.AtmosphereEditorController;
import less.gui.view.BatchController;
import less.gui.view.DBChooserController;
import less.gui.view.HelpViewerController;
import less.gui.view.LAICalculatorController;
import less.gui.view.LessMainWindowController;
import less.gui.view.PlotSpectraController;
import less.gui.view.ProspectDController;
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
	
	public Label skyTemperatureLabel = null;
	public ComboBox<String> comboBoxSkyTemper = null;
	
	
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
	public AtmosphereParams atmosphereParams = null;//Atmosphere class for storing atmosphere parameters.
	public Map<String, ProspectDParams> prospectDParamsMap = new HashMap<String, ProspectDParams>();
	
	
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
		this.mwController.mainApp.getHostServices().showDocument(getResultsDirPath());
/*		
		if (Desktop.isDesktopSupported()) {
		    try {
				Desktop.getDesktop().open(new File(getResultsDirPath()));
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}*/
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
	
	public void onShowObjectDimensionCheck() {
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
	        	fileChooser.getExtensionFilters().add(new FileChooser.ExtensionFilter("ENVI Standard", "*"));
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
					if(fileChooser.getSelectedExtensionFilter().getExtensions().get(0).equals("*")){
						Files.copy(Paths.get(file.toString()+".hdr"), Paths.get(param_path,file.getName()+".hdr"), options);
					}
				} catch (IOException e) {
					e.printStackTrace();
				}
	        	this.mwController.terrFileField.setText(file.getName());
	        }
	}
	
	/**
	 * terrain: land albedo map
	 */
	public void selectLandAlbedoBtn() {
		if(this.mwController.simulation_path == null){
			this.mwController.outputConsole.log("Please create a simulation first.\n");
			   return;
			}
			Path initPath = Paths.get(this.mwController.simulation_path);
			FileChooser fileChooser = new FileChooser();
			File initDirectory = new File(initPath.normalize().toString());
			fileChooser.setInitialDirectory(initDirectory);
	        // Set extension filter
			fileChooser.getExtensionFilters().add(new FileChooser.ExtensionFilter("ENVI Standard", "*.*"));
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
	        	this.mwController.landAlbedoTextField.setText(file.getName());
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
	
	//include whole scene
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
	
	//virtual plane
	public void handlePlaneCheckbox(){
		if(this.mwController.virtualPlaneCheckbox.isSelected()){
			if (virtualPlanePane != null)
				return;
			
			virtualPlanePane = new AnchorPane();
			virtualPlanePane.setPrefHeight(60);
			this.mwController.sensorVbox.getChildren().add(this.mwController.sensorVbox.getChildren().size()-1, virtualPlanePane);
			Label labelCenter = new Label("Center[XY]:");
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
			
			Label labelZ = new Label("Z[0~Z]:");
			AnchorPane.setTopAnchor(labelZ, 50.0);
			AnchorPane.setLeftAnchor(labelZ, 450.0);
			virtualPlanePane.getChildren().add(labelZ);
			
			zpos = new TextField();
			zpos.setPrefWidth(70);
			AnchorPane.setTopAnchor(zpos, 45.0);
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
			xsizepos.setText(this.mwController.sceneXSizeField.getText().replaceAll(",", ""));
			ysizepos.setText(this.mwController.sceneYSizeField.getText().replaceAll(",", ""));
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
	
	
	//thermal
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
			this.mwController.temperatureMap.put("T300", "300:5");
			
			
			TextField temperValField = new TextField();
			temperValField.setPromptText("300:5");
			temperValField.setPrefWidth(150);
			AnchorPane.setLeftAnchor(temperValField, 260.0);
			AnchorPane.setTopAnchor(temperValField, 80.0);
			Label tipLabel = new Label("(Mean T:Delta T)");
			tipLabel.setTextFill(Color.web("#777777"));
			AnchorPane.setLeftAnchor(tipLabel, 420.0);
			AnchorPane.setTopAnchor(tipLabel, 85.0);
		
			opticalThermalPane.getChildren().addAll(tempLabel, addBtn,delBtn,temperNameField,temperListView,temperValField,tipLabel);
			
			//show for terrain
			terrainTemperLabel = new Label("Temperature: ");
			comboBoxTerrainTemper = new ComboBox<String>();
			//comboBoxTerrainTemper.setPrefWidth(224);
			comboBoxTerrainTemper.setItems(this.temperatureList);
			comboBoxTerrainTemper.getSelectionModel().select(Const.LESS_DEFAULT_TEMPERATURE);
			this.mwController.terrainOpticalAnchorPane.getChildren().addAll(terrainTemperLabel, comboBoxTerrainTemper);
			AnchorPane.setLeftAnchor(terrainTemperLabel, 0.0);
			AnchorPane.setTopAnchor(terrainTemperLabel, 100.0);
			AnchorPane.setLeftAnchor(comboBoxTerrainTemper, 110.0);
			AnchorPane.setTopAnchor(comboBoxTerrainTemper, 95.0);
			
			
			//show for sky
			skyTemperatureLabel = new Label("Temperature: ");
			comboBoxSkyTemper = new ComboBox<String>();
			comboBoxSkyTemper.setItems(this.temperatureList);
			comboBoxSkyTemper.getSelectionModel().select(Const.LESS_DEFAULT_TEMPERATURE);
			this.mwController.skyPane.getChildren().addAll(skyTemperatureLabel,comboBoxSkyTemper);
			AnchorPane.setLeftAnchor(skyTemperatureLabel, 5.0);
			AnchorPane.setTopAnchor(skyTemperatureLabel, 140.0);
			AnchorPane.setLeftAnchor(comboBoxSkyTemper, 150.0);
			AnchorPane.setTopAnchor(comboBoxSkyTemper, 135.0);
			
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
					mwController.temperatureMap.put(temperName, "300:5");
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
			if(skyTemperatureLabel != null) {
				this.mwController.skyPane.getChildren().remove(skyTemperatureLabel);
			}
			if(comboBoxSkyTemper != null) {
				this.mwController.skyPane.getChildren().remove(comboBoxSkyTemper);
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
	
	
	//Open Atmosphere editor
	public void OpenAtmosphereEditor() {
		FXMLLoader loader = new FXMLLoader();
		loader.setLocation(AtmosphereEditorController.class.getResource("AtmosphereEditor.fxml"));
		try {
			BorderPane rootLayout = (BorderPane) loader.load();
			Scene scene = new Scene(rootLayout);
			Stage atsStage = new Stage();
			atsStage.setScene(scene);
			atsStage.setTitle("Atmosphere Editor");
			AtmosphereEditorController atmosphereEditorController = loader.getController();
			atmosphereEditorController.setParentStage(atsStage);
			atmosphereEditorController.setmwController(this.mwController);
			atmosphereEditorController.initView();			
			atsStage.getIcons().add(new Image(LessMainApp.class.getResourceAsStream("LESS16_16.png")));
			atsStage.getIcons().add(new Image(LessMainApp.class.getResourceAsStream("LESS32_32.png")));
			atsStage.initOwner(this.mwController.mainApp.getPrimaryStage());
			atsStage.setResizable(false);
			atsStage.show();
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
	
	public void PlotSpectra() {
		FacetOptical facetOptical = (FacetOptical) this.mwController.opticalTable.getSelectionModel().getSelectedItem();
		if(facetOptical != null) {
			FXMLLoader loader = new FXMLLoader();
			loader.setLocation(PlotSpectraController.class.getResource("PlotSpectraView.fxml"));
			try {
				BorderPane rootLayout = (BorderPane) loader.load();
				Scene scene = new Scene(rootLayout);
				Stage spectraStage = new Stage();
				spectraStage.setScene(scene);
				spectraStage.setTitle("Spectra");
				PlotSpectraController plotspectraController = loader.getController();
				plotspectraController.setParentStage(spectraStage);
				plotspectraController.setmwController(this.mwController);
				plotspectraController.initView();
				spectraStage.getIcons().add(new Image(LessMainApp.class.getResourceAsStream("LESS16_16.png")));
				spectraStage.getIcons().add(new Image(LessMainApp.class.getResourceAsStream("LESS32_32.png")));
				//spectraStage.initOwner(this.mwController.mainApp.getPrimaryStage());
				//spectraStage.setResizable(false);
				spectraStage.show();
			} catch (IOException e) {
				e.printStackTrace();
			}
		}else {
			System.out.println("ERROR: Please Choose a optical property!");
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
		
		//products
		Label productsLabel = new Label("Products:");
		mwController.ptConfigPanel.getChildren().add(productsLabel);
		AnchorPane.setLeftAnchor(productsLabel, 0.0);
		AnchorPane.setTopAnchor(productsLabel, 45.0);
		mwController.productBRFCheckbox = new CheckBox("BRF");
		mwController.productUpDownRadiationCheckbox = new CheckBox("Up/Downwelling Radiation");
		mwController.ptConfigPanel.getChildren().add(mwController.productBRFCheckbox);
		mwController.ptConfigPanel.getChildren().add(mwController.productUpDownRadiationCheckbox);
		AnchorPane.setLeftAnchor(mwController.productBRFCheckbox, 150.0);
		AnchorPane.setLeftAnchor(mwController.productUpDownRadiationCheckbox, 220.0);
		AnchorPane.setTopAnchor(mwController.productBRFCheckbox, 45.0);
		AnchorPane.setTopAnchor(mwController.productUpDownRadiationCheckbox, 45.0);
		
		mwController.productfPARChecbox = new CheckBox("fPAR");
		mwController.ptConfigPanel.getChildren().add(mwController.productfPARChecbox);
		AnchorPane.setLeftAnchor(mwController.productfPARChecbox, 430.0);
		AnchorPane.setTopAnchor(mwController.productfPARChecbox, 45.0);
		
		mwController.productfPARChecbox.selectedProperty().addListener(new ChangeListener<Boolean>() {
		    @Override
		    public void changed(ObservableValue<? extends Boolean> observable, Boolean oldValue, Boolean newValue) {
		        if(newValue) {
		        	mwController.fPARLayerLabel = new Label("Layer definition:");
		        	mwController.ptConfigPanel.getChildren().add(mwController.fPARLayerLabel);
		    		AnchorPane.setLeftAnchor(mwController.fPARLayerLabel, 0.0);
		    		
		    		mwController.fPARLayerTextEdit = new TextField();
		    		mwController.fPARLayerTextEdit.setPromptText("Example: 0:2:20 or 10");
		    		mwController.ptConfigPanel.getChildren().add(mwController.fPARLayerTextEdit);
		    		AnchorPane.setLeftAnchor(mwController.fPARLayerTextEdit, 150.0);
		    		AnchorPane.setRightAnchor(mwController.fPARLayerTextEdit, 20.0);
		    		
		    		if(mwController.productBRFCheckbox.isSelected()) {
		    			AnchorPane.setTopAnchor(mwController.fPARLayerLabel, 210.0);
		    			AnchorPane.setTopAnchor(mwController.fPARLayerTextEdit, 205.0);
		    		}else {
		    			AnchorPane.setTopAnchor(mwController.fPARLayerLabel, 85.0);
		    			AnchorPane.setTopAnchor(mwController.fPARLayerTextEdit, 80.0);
		    		}		    		
		    		
		        }else {
		        	mwController.ptConfigPanel.getChildren().remove(mwController.fPARLayerTextEdit);
		        	mwController.ptConfigPanel.getChildren().remove(mwController.fPARLayerLabel);
		        	if(mwController.productBRFCheckbox.isSelected()) {
		        		mwController.productBRFCheckbox.setSelected(false);
		        		mwController.productBRFCheckbox.setSelected(true);
		        	}
		        }
		    }
		});
		
		mwController.productBRFCheckbox.selectedProperty().addListener(new ChangeListener<Boolean>() {
		    @Override
		    public void changed(ObservableValue<? extends Boolean> observable, Boolean oldValue, Boolean newValue) {
		        if(newValue) {
		        	double offset = 0.0;
		        	if(mwController.productfPARChecbox.isSelected()) {
		        		offset = 40.0;
		        	}
		        	
		        	//number of directions
		    		mwController.numOfDirectionLabel = new Label("Number of Directions:");
		    		mwController.ptConfigPanel.getChildren().add(mwController.numOfDirectionLabel);
		    		AnchorPane.setLeftAnchor(mwController.numOfDirectionLabel, 0.0);
		    		AnchorPane.setTopAnchor(mwController.numOfDirectionLabel, offset+85.0);
		    		mwController.numOfDirectionTextField = new TextField();
		    		mwController.ptConfigPanel.getChildren().add(mwController.numOfDirectionTextField);
		    		mwController.numOfDirectionTextField.setText("150");
		    		AnchorPane.setLeftAnchor(mwController.numOfDirectionTextField, 150.0);
		    		AnchorPane.setRightAnchor(mwController.numOfDirectionTextField, 20.0);
		    		AnchorPane.setTopAnchor(mwController.numOfDirectionTextField, offset+80.0);
		        	
		        	mwController.virtualLabel = new Label("Virutal Directions [\u00B0]:");
		        	mwController.ptConfigPanel.getChildren().add(mwController.virtualLabel);
		    		AnchorPane.setLeftAnchor(mwController.virtualLabel, 0.0);
		    		AnchorPane.setTopAnchor(mwController.virtualLabel, offset+125.0);
		    		mwController.virtualDirTextField = new TextField();
		    		mwController.virtualDirTextField.setPromptText("zenith:azimuth;zentih:azimuth or zenith1,zenith2;azimuth1,azimuth2");
		    		mwController.ptConfigPanel.getChildren().add(mwController.virtualDirTextField);
		    		AnchorPane.setLeftAnchor(mwController.virtualDirTextField, 150.0);
		    		AnchorPane.setRightAnchor(mwController.virtualDirTextField, 20.0);
		    		AnchorPane.setTopAnchor(mwController.virtualDirTextField, offset+120.0);
		    		
		    		mwController.virtualDetectorLabel = new Label("Virutal Detectors [\u00B0]:");
		        	mwController.ptConfigPanel.getChildren().add(mwController.virtualDetectorLabel);
		    		AnchorPane.setLeftAnchor(mwController.virtualDetectorLabel, 0.0);
		    		AnchorPane.setTopAnchor(mwController.virtualDetectorLabel, offset+170.0);
		    		mwController.virtualDetectorTextField = new TextField();
		    		mwController.virtualDetectorTextField.setPromptText("centerZenith,centerAzimuth,angleInterval;centerZenith,centerAzimuth,angleInterval");
		    		mwController.ptConfigPanel.getChildren().add(mwController.virtualDetectorTextField);
		    		AnchorPane.setLeftAnchor(mwController.virtualDetectorTextField, 150.0);
		    		AnchorPane.setRightAnchor(mwController.virtualDetectorTextField, 20.0);
		    		AnchorPane.setTopAnchor(mwController.virtualDetectorTextField, offset+165.0);
		    		
		        }else {
		        	mwController.ptConfigPanel.getChildren().remove(mwController.virtualLabel);
		        	mwController.ptConfigPanel.getChildren().remove(mwController.virtualDirTextField);
		        	mwController.ptConfigPanel.getChildren().remove(mwController.numOfDirectionLabel);
		        	mwController.ptConfigPanel.getChildren().remove(mwController.numOfDirectionTextField);
		        	mwController.ptConfigPanel.getChildren().remove(mwController.virtualDetectorLabel);
		        	mwController.ptConfigPanel.getChildren().remove(mwController.virtualDetectorTextField);
		        	if(mwController.productfPARChecbox.isSelected()) {
		        		mwController.productfPARChecbox.setSelected(false);
		        		mwController.productfPARChecbox.setSelected(true);
		        	}
		        }
		    }
		});
		mwController.productBRFCheckbox.setSelected(true);
		
	}
	
	private void createFisheEyeConfigPanel(){
		mwController.cfConfigPanel = new AnchorPane();
		Label fov = new Label("FOV:");
		mwController.cfConfigPanel.getChildren().add(fov);
		AnchorPane.setLeftAnchor(fov, 0.0);
		mwController.cfFovTextField = new TextField("165");
		mwController.cfConfigPanel.getChildren().add(mwController.cfFovTextField);
		AnchorPane.setLeftAnchor(mwController.cfFovTextField, 150.0);
		AnchorPane.setRightAnchor(mwController.cfFovTextField, 20.0);
		AnchorPane.setTopAnchor(mwController.cfFovTextField, 10.0);
		AnchorPane.setTopAnchor(fov, 15.0);
		//projection type
		Label proj_type = new Label("Fisheye Projection: ");
		mwController.cfConfigPanel.getChildren().add(proj_type);
		AnchorPane.setLeftAnchor(proj_type, 0.0);
		AnchorPane.setTopAnchor(proj_type, 50.0);
		
		ObservableList<String> options = 
			    FXCollections.observableArrayList(
			        "equisolid",
			        "orthographic",
			        "equidistant",
			        "stereographic"
			    );
		mwController.combobox = new ComboBox<String>(options);
		mwController.combobox.getSelectionModel().select(0);
		mwController.cfConfigPanel.getChildren().add(mwController.combobox);
		AnchorPane.setLeftAnchor(mwController.combobox, 150.0);
		AnchorPane.setRightAnchor(mwController.combobox, 20.0);
		AnchorPane.setTopAnchor(mwController.combobox, 50.0);
	}
	
	public void addComponents2OrthPane() {
		Label productsLabel = new Label("Products:");
		this.mwController.orthographicPane.getChildren().add(productsLabel);
		AnchorPane.setLeftAnchor(productsLabel, 0.0);
		AnchorPane.setTopAnchor(productsLabel, 150.0);
		this.mwController.orthfourCompsCheckbox = new CheckBox("Four Components Product");
		this.mwController.orthographicPane.getChildren().add(this.mwController.orthfourCompsCheckbox);
		AnchorPane.setLeftAnchor(this.mwController.orthfourCompsCheckbox, 150.0);
		AnchorPane.setTopAnchor(this.mwController.orthfourCompsCheckbox, 150.0);
	}
	
	public void addComponents2PerPane() {
		Label productsLabel = new Label("Products:");
		this.mwController.perspectivePane.getChildren().add(productsLabel);
		AnchorPane.setLeftAnchor(productsLabel, 0.0);
		AnchorPane.setTopAnchor(productsLabel, 100.0);
		this.mwController.perfourCompsCheckbox = new CheckBox("Four Components Product");
		this.mwController.perspectivePane.getChildren().add(this.mwController.perfourCompsCheckbox);
		AnchorPane.setLeftAnchor(this.mwController.perfourCompsCheckbox, 150.0);
		AnchorPane.setTopAnchor(this.mwController.perfourCompsCheckbox, 100.0);
	}

	//sensor
	public void initSensor(){
		
		createPhotonTracingConfigPanel();
		createFisheEyeConfigPanel();
		addComponents2OrthPane();
		addComponents2PerPane();
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
					mwController.sensorVbox.getChildren().remove(mwController.cfConfigPanel);
					mwController.sensorVbox.getChildren().remove(mwController.perspectivePane);
					mwController.sensorVbox.getChildren().add(mwController.orthographicPane);
					mwController.obsVbox.getChildren().remove(mwController.obsPerspectivePane);
					mwController.obsVbox.getChildren().add(mwController.obsOrthographicPane);
					mwController.pixelUnitLabel.setText("Samples [/pixel]:");
					mwController.sensorVbox.getChildren().remove(mwController.ptConfigPanel);
					mwController.virtualPlaneCheckbox.setSelected(false);
					handlePlaneCheckbox();
					mwController.virtualPlaneCheckbox.setDisable(false);
					mwController.sensorWidthField.setDisable(false);
					mwController.sensorHeightField.setDisable(false);
					mwController.sensorSampleField.setDisable(false);
					mwController.reDrawAll();
				}
				if(newVal.equals(Const.LESS_SENSOR_TYPE_PER)){
					mwController.sensorVbox.getChildren().remove(mwController.cfConfigPanel);
					mwController.sensorVbox.getChildren().remove(mwController.orthographicPane);
					mwController.sensorVbox.getChildren().add(mwController.perspectivePane);
					mwController.obsVbox.getChildren().remove(mwController.obsOrthographicPane);
					mwController.obsVbox.getChildren().remove(mwController.obsPerspectivePane);
					mwController.obsVbox.getChildren().add(mwController.obsPerspectivePane);
					mwController.pixelUnitLabel.setText("Samples [/pixel]:");
					mwController.sensorVbox.getChildren().remove(mwController.ptConfigPanel);
					mwController.virtualPlaneCheckbox.setSelected(false);
					handlePlaneCheckbox();
					mwController.virtualPlaneCheckbox.setDisable(true);
					mwController.sensorWidthField.setDisable(false);
					mwController.sensorHeightField.setDisable(false);
					mwController.sensorSampleField.setDisable(false);
					mwController.reDrawAll();
				}
				if(newVal.equals(Const.LESS_SENSOR_TYPE_CF)){
					mwController.sensorVbox.getChildren().remove(mwController.orthographicPane);
					mwController.sensorVbox.getChildren().remove(mwController.perspectivePane);
					mwController.sensorVbox.getChildren().remove(mwController.ptConfigPanel);
					mwController.sensorVbox.getChildren().add(mwController.cfConfigPanel);
					mwController.pixelUnitLabel.setText("Samples [/pixel]:");
					mwController.obsVbox.getChildren().remove(mwController.obsOrthographicPane);
					// fisheye uese the same obsVbox as perspective
					mwController.obsVbox.getChildren().remove(mwController.obsPerspectivePane);
					mwController.obsVbox.getChildren().add(mwController.obsPerspectivePane);
					//mwController.pixelUnitLabel.setText("Samples [/pixel]:");
					mwController.virtualPlaneCheckbox.setSelected(false);
					handlePlaneCheckbox();
					mwController.virtualPlaneCheckbox.setDisable(true);
					mwController.sensorWidthField.setDisable(false);
					mwController.sensorHeightField.setDisable(false);
					mwController.sensorSampleField.setDisable(false);
					mwController.reDrawAll();
				}
				if(newVal.equals(Const.LESS_SENSOR_TYPE_PT)){
					mwController.sensorVbox.getChildren().remove(mwController.cfConfigPanel);
					mwController.sensorVbox.getChildren().remove(mwController.orthographicPane);
					mwController.sensorVbox.getChildren().remove(mwController.perspectivePane);
					mwController.obsVbox.getChildren().remove(mwController.obsPerspectivePane);
					mwController.obsVbox.getChildren().remove(mwController.obsOrthographicPane);
					mwController.sensorVbox.getChildren().add(mwController.ptConfigPanel);
					//diable virtual plane
					mwController.virtualPlaneCheckbox.setSelected(false);
					handlePlaneCheckbox();
					mwController.virtualPlaneCheckbox.setDisable(false);
					VBox.setMargin(mwController.ptConfigPanel, new Insets(15,0,0,0));
					mwController.sensorWidthField.setDisable(true);
					mwController.sensorHeightField.setDisable(true);
					mwController.sensorSampleField.setDisable(true);
					mwController.reDrawAll();
				}
			}
		});
	}
	
	
	public  void initTerrainModule() {
		this.mwController.terrainVbox.getChildren().remove(this.mwController.terrFilePane);
		this.mwController.comboBoxDEMType.valueProperty().addListener(new ChangeListener<String>() {
			@Override 
			public void changed(ObservableValue ov, String oldVal, String newVal) {
				if(newVal.equals(Const.LESS_TERRAIN_PLANE)){
					mwController.sceneXSizeField.setDisable(false);
					mwController.sceneYSizeField.setDisable(false);
					mwController.terrainVbox.getChildren().remove(mwController.terrFilePane);
				}
				if (newVal.equals(Const.LESS_TERRAIN_MESH)){
					mwController.sceneXSizeField.setDisable(true);
					mwController.sceneYSizeField.setDisable(true);
					if (!mwController.terrainVbox.getChildren().contains(mwController.terrFilePane)){
						mwController.terrainVbox.getChildren().add(1, mwController.terrFilePane);
					}
				}
				if(newVal.equals(Const.LESS_TERRAIN_RASTER)){
					//show the selection for image
					mwController.sceneXSizeField.setDisable(false);
					mwController.sceneYSizeField.setDisable(false);
					if (!mwController.terrainVbox.getChildren().contains(mwController.terrFilePane)){
						mwController.terrainVbox.getChildren().add(1, mwController.terrFilePane);
					}
				}
		    } 
		});
		
		//brdf
		this.mwController.terrainBRDFTypeCombox.valueProperty().addListener(new ChangeListener<String>() {
			@Override 
			public void changed(ObservableValue ov, String oldVal, String newVal) {
				if(newVal.equals(Const.LESS_TERRAIN_BRDF_SOILSPECT)){
					mwController.terrainOpticalCombox.getSelectionModel().clearSelection();
					mwController.terrainOpticalCombox.setDisable(true);
					mwController.albedoLabel = new Label("\u03C9:");
					mwController.c1Label = new Label("c1:");
					mwController.c2Label = new Label("c2:");
					mwController.c3Label = new Label("c3:");
					mwController.c4Label = new Label("c4:");
					mwController.h1Label = new Label("h1:");
					mwController.h2Label = new Label("h2:");
					mwController.terrainOpticalAnchorPane.getChildren().add(mwController.albedoLabel);
					mwController.terrainOpticalAnchorPane.getChildren().add(mwController.c1Label);
					mwController.terrainOpticalAnchorPane.getChildren().add(mwController.c2Label);
					mwController.terrainOpticalAnchorPane.getChildren().add(mwController.c3Label);
					mwController.terrainOpticalAnchorPane.getChildren().add(mwController.c4Label);
					mwController.terrainOpticalAnchorPane.getChildren().add(mwController.h1Label);
					mwController.terrainOpticalAnchorPane.getChildren().add(mwController.h2Label);
					AnchorPane.setTopAnchor(mwController.albedoLabel, 110.0);
					AnchorPane.setTopAnchor(mwController.c1Label, 150.0);
					AnchorPane.setTopAnchor(mwController.c2Label, 190.0);
					AnchorPane.setTopAnchor(mwController.c3Label, 230.0);
					AnchorPane.setTopAnchor(mwController.c4Label, 270.0);
					AnchorPane.setTopAnchor(mwController.h1Label, 310.0);
					AnchorPane.setTopAnchor(mwController.h2Label, 350.0);
					
					mwController.albedoTextField = new TextField("0.537");
					mwController.c1TextField = new TextField("1.492");
					mwController.c2TextField = new TextField("0.56");
					mwController.c3TextField = new TextField("0.238");
					mwController.c4TextField = new TextField("-0.06");
					mwController.h1TextField = new TextField("1");
					mwController.h2TextField = new TextField("0.114");
					mwController.terrainOpticalAnchorPane.getChildren().add(mwController.albedoTextField);
					mwController.terrainOpticalAnchorPane.getChildren().add(mwController.c1TextField);
					mwController.terrainOpticalAnchorPane.getChildren().add(mwController.c2TextField);
					mwController.terrainOpticalAnchorPane.getChildren().add(mwController.c3TextField);
					mwController.terrainOpticalAnchorPane.getChildren().add(mwController.c4TextField);
					mwController.terrainOpticalAnchorPane.getChildren().add(mwController.h1TextField);
					mwController.terrainOpticalAnchorPane.getChildren().add(mwController.h2TextField);
					AnchorPane.setTopAnchor(mwController.albedoTextField, 105.0);
					AnchorPane.setTopAnchor(mwController.c1TextField, 145.0);
					AnchorPane.setTopAnchor(mwController.c2TextField, 185.0);
					AnchorPane.setTopAnchor(mwController.c3TextField, 225.0);
					AnchorPane.setTopAnchor(mwController.c4TextField, 265.0);
					AnchorPane.setTopAnchor(mwController.h1TextField, 305.0);
					AnchorPane.setTopAnchor(mwController.h2TextField, 345.0);
					AnchorPane.setLeftAnchor(mwController.albedoTextField, 120.0);
					AnchorPane.setLeftAnchor(mwController.c1TextField, 120.0);
					AnchorPane.setLeftAnchor(mwController.c2TextField, 120.0);
					AnchorPane.setLeftAnchor(mwController.c3TextField, 120.0);
					AnchorPane.setLeftAnchor(mwController.c4TextField, 120.0);
					AnchorPane.setLeftAnchor(mwController.h1TextField, 120.0);
					AnchorPane.setLeftAnchor(mwController.h2TextField, 120.0);
					
					mwController.soilspectHelp = new Label("(\u03C9"+"1,"+"\u03C9"+"2,...[Number of Bands])");
					mwController.terrainOpticalAnchorPane.getChildren().add(mwController.soilspectHelp);
					AnchorPane.setLeftAnchor(mwController.soilspectHelp, 300.0);
					AnchorPane.setTopAnchor(mwController.soilspectHelp, 110.0);
					
					
					mwController.terrainOpticalAnchorPane.getChildren().remove(mwController.landAlbedoTextField);
					mwController.terrainOpticalAnchorPane.getChildren().remove(mwController.landAlbedoLabel);
					mwController.terrainOpticalAnchorPane.getChildren().remove(mwController.selectLandAlbedoBtn);
				}
				if (newVal.equals(Const.LESS_TERRAIN_BRDF_LAMBERTIAN)){
					mwController.terrainOpticalCombox.getSelectionModel().select(0);
					mwController.terrainOpticalCombox.setDisable(false);
					
					mwController.terrainOpticalAnchorPane.getChildren().remove(mwController.albedoLabel);
					mwController.terrainOpticalAnchorPane.getChildren().remove(mwController.c1Label);
					mwController.terrainOpticalAnchorPane.getChildren().remove(mwController.c2Label);
					mwController.terrainOpticalAnchorPane.getChildren().remove(mwController.c3Label);
					mwController.terrainOpticalAnchorPane.getChildren().remove(mwController.c4Label);
					mwController.terrainOpticalAnchorPane.getChildren().remove(mwController.h1Label);
					mwController.terrainOpticalAnchorPane.getChildren().remove(mwController.h2Label);
					
					mwController.terrainOpticalAnchorPane.getChildren().remove(mwController.albedoTextField);
					mwController.terrainOpticalAnchorPane.getChildren().remove(mwController.c1TextField);
					mwController.terrainOpticalAnchorPane.getChildren().remove(mwController.c2TextField);
					mwController.terrainOpticalAnchorPane.getChildren().remove(mwController.c3TextField);
					mwController.terrainOpticalAnchorPane.getChildren().remove(mwController.c4TextField);
					mwController.terrainOpticalAnchorPane.getChildren().remove(mwController.h1TextField);
					mwController.terrainOpticalAnchorPane.getChildren().remove(mwController.h2TextField);
					
					mwController.terrainOpticalAnchorPane.getChildren().remove(mwController.soilspectHelp);
					
					
					mwController.terrainOpticalAnchorPane.getChildren().remove(mwController.landAlbedoTextField);
					mwController.terrainOpticalAnchorPane.getChildren().remove(mwController.landAlbedoLabel);
					mwController.terrainOpticalAnchorPane.getChildren().remove(mwController.selectLandAlbedoBtn);
				}
				
				if(newVal.equals(Const.LESS_TERRAIN_BRDF_LANDALBEDOMAP)) {
					mwController.terrainOpticalCombox.getSelectionModel().clearSelection();
					mwController.terrainOpticalCombox.setDisable(true);
					
					mwController.landAlbedoTextField = new TextField();
					mwController.terrainOpticalAnchorPane.getChildren().add(mwController.landAlbedoTextField);
					AnchorPane.setTopAnchor(mwController.landAlbedoTextField, 105.0);
					AnchorPane.setLeftAnchor(mwController.landAlbedoTextField, 120.0);
					
					mwController.landAlbedoLabel = new Label("Land Albedo Map: ");
					mwController.terrainOpticalAnchorPane.getChildren().add(mwController.landAlbedoLabel);
					AnchorPane.setTopAnchor(mwController.landAlbedoLabel, 110.0);
					AnchorPane.setLeftAnchor(mwController.landAlbedoLabel, 0.0);
					
					mwController.selectLandAlbedoBtn = new Button("\u2026");
					mwController.terrainOpticalAnchorPane.getChildren().add(mwController.selectLandAlbedoBtn);
					AnchorPane.setTopAnchor(mwController.selectLandAlbedoBtn, 105.0);
					AnchorPane.setLeftAnchor(mwController.selectLandAlbedoBtn, 300.0);
					
					mwController.terrainOpticalAnchorPane.getChildren().remove(mwController.albedoLabel);
					mwController.terrainOpticalAnchorPane.getChildren().remove(mwController.c1Label);
					mwController.terrainOpticalAnchorPane.getChildren().remove(mwController.c2Label);
					mwController.terrainOpticalAnchorPane.getChildren().remove(mwController.c3Label);
					mwController.terrainOpticalAnchorPane.getChildren().remove(mwController.c4Label);
					mwController.terrainOpticalAnchorPane.getChildren().remove(mwController.h1Label);
					mwController.terrainOpticalAnchorPane.getChildren().remove(mwController.h2Label);
					
					mwController.terrainOpticalAnchorPane.getChildren().remove(mwController.albedoTextField);
					mwController.terrainOpticalAnchorPane.getChildren().remove(mwController.c1TextField);
					mwController.terrainOpticalAnchorPane.getChildren().remove(mwController.c2TextField);
					mwController.terrainOpticalAnchorPane.getChildren().remove(mwController.c3TextField);
					mwController.terrainOpticalAnchorPane.getChildren().remove(mwController.c4TextField);
					mwController.terrainOpticalAnchorPane.getChildren().remove(mwController.h1TextField);
					mwController.terrainOpticalAnchorPane.getChildren().remove(mwController.h2TextField);
					
					mwController.terrainOpticalAnchorPane.getChildren().remove(mwController.soilspectHelp);
					
					mwController.selectLandAlbedoBtn.setOnAction(new EventHandler<ActionEvent>() {
					    @Override public void handle(ActionEvent e) {
					        selectLandAlbedoBtn();
					    }
					});
				}
				
		    } 
		});
		
	}
	
	//Open Prospect-D dialog
	public void OpenProspectD() {
		try {
			FXMLLoader loader = new FXMLLoader();
			loader.setLocation(LessMainWindowController.class.getResource("ProspectDView.fxml"));
			BorderPane rootLayout = (BorderPane) loader.load();
			Scene scene = new Scene(rootLayout);
			Stage subStage = new Stage();
			subStage.setScene(scene);
			subStage.setTitle("PROSPECT-D");
			ProspectDController prospectDController = loader.getController();
			prospectDController.setMainWindowController(this.mwController);
			prospectDController.setParentStage(subStage);
			//objController.setOpticalData(this.terrainOpticalData);
			//objController.setObjectData(objectsList, objectsAndCompomentsMap, opticalcomponentMap);
			prospectDController.initView();
			subStage.getIcons().add(new Image(LessMainApp.class.getResourceAsStream("LESS16_16.png")));
			subStage.getIcons().add(new Image(LessMainApp.class.getResourceAsStream("LESS32_32.png")));
			subStage.initOwner(this.mwController.mainApp.getPrimaryStage());
			subStage.show();
			
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
	
	//python interpreter
	public void choosePyInterpreter(){
		FileChooser fileChooser = new FileChooser();
		fileChooser.getExtensionFilters().add(new FileChooser.ExtensionFilter("Python Interpreter", "*.*"));
	    // Show open file dialog
	    File file = fileChooser.showOpenDialog(this.mwController.mainApp.getPrimaryStage());
	    if(file !=null)
	    {
	    	this.mwController.PyInterpreterEdit.setText(file.toString());
	    	PyLauncher.external_py_interpreter = file.toString();
	    }
	}
		
	
	//lab 
	public void PyJavaCommunication(){
		PyServer pyServer = new PyServer();
		pyServer.setMainConroller(this.mwController);
		Thread testA=new Thread(pyServer);  
        testA.start();  
	}
}
