package less.gui.view;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintStream;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.Map;
import java.util.Properties;
import java.util.concurrent.CountDownLatch;

import javafx.beans.value.ChangeListener;
import javafx.beans.value.ObservableValue;
import javafx.collections.FXCollections;
import javafx.collections.ListChangeListener;
import javafx.collections.ObservableList;
import javafx.event.ActionEvent;
import javafx.event.EventHandler;
import javafx.fxml.FXML;
import javafx.fxml.FXMLLoader;
import javafx.scene.Scene;
import javafx.scene.canvas.Canvas;
import javafx.scene.control.Button;
import javafx.scene.control.CheckBox;
import javafx.scene.control.ComboBox;
import javafx.scene.control.ContextMenu;
import javafx.scene.control.Label;
import javafx.scene.control.ListView;
import javafx.scene.control.RadioButton;
import javafx.scene.control.RadioMenuItem;
import javafx.scene.control.ScrollPane;
import javafx.scene.control.SelectionMode;
import javafx.scene.control.SplitMenuButton;
import javafx.scene.control.TabPane;
import javafx.scene.control.TableCell;
import javafx.scene.control.TableColumn;
import javafx.scene.control.TableColumn.CellEditEvent;
import javafx.scene.control.TableView;
import javafx.scene.control.TextArea;
import javafx.scene.control.TextField;
import javafx.scene.control.TextFormatter;
import javafx.scene.control.ToggleGroup;
import javafx.scene.control.ToolBar;
import javafx.scene.control.cell.PropertyValueFactory;
import javafx.scene.control.cell.TextFieldTableCell;
import javafx.scene.image.Image;
import javafx.scene.layout.AnchorPane;
import javafx.scene.layout.BorderPane;
import javafx.scene.layout.VBox;
import javafx.scene.paint.Color;
import javafx.stage.DirectoryChooser;
import javafx.stage.Stage;
import javafx.stage.WindowEvent;
import javafx.util.Callback;
import less.LessMainApp;
import less.gui.display2D.DrawToolBarHelper;
import less.gui.helper.DrawHelper;
import less.gui.helper.FieldUtils;
import less.gui.helper.Filehelper;
import less.gui.helper.OutputConsole;
import less.gui.helper.ProjectManager;
import less.gui.helper.PyLauncher;
import less.gui.helper.RunningStatusThread;
import less.gui.model.FacetOptical;
import less.gui.model.LSBoundingbox;
import less.gui.model.OpticalThermalProperty;
import less.gui.model.PositionXY;
import less.gui.utils.CommonUitls;
import less.gui.utils.Const;
import less.gui.utils.ConstConfig;
import less.gui.utils.DBReader;
import less.gui.utils.EditingCell;
import less.gui.utils.NumberStringFilteredConverter;
import net.sf.cglib.core.Local;

public class LessMainWindowController {
	@FXML
	private AnchorPane cavasAnchorPane;
	@FXML
	public TabPane ConsoleTabPane;
	@FXML
	public AnchorPane ConsoleBarAnchorPane;
	
	
	@FXML
	public Canvas canvas;
	public Boolean StopDrawTree = false;//stop drawing tree positions
	@FXML
	public CheckBox DrawPolygonCheckbox;
	@FXML
	public CheckBox DrawPointCheckbox;
	@FXML
	public Button AddTreePolyBtn;
	@FXML
	public Button DelTreePolyBtn;
	@FXML
	public Button ApplyTreeSpeciesBtn;
	@FXML
	public TextField ImgBarMinDistTextField;
	
	//terrain
	@FXML
	public AnchorPane terrFilePane;
	@FXML
	public VBox terrainVbox;
	@FXML
	public Button selectTerrBtn;
	
	public AnchorPane terrainPane;
	
	public Button selectLandAlbedoBtn;
	
	public TextField landAlbedoTextField;
	public Label landAlbedoLabel;
	@FXML
	public ComboBox<String> comboBoxDEMType;
	@FXML
	public TextField sceneXSizeField;
	@FXML 
	public TextField sceneYSizeField;
	@FXML
	public TextField terrFileField;
	@FXML
	public ComboBox<String> terrainOpticalCombox;
	@FXML
	public ComboBox<String> terrainBRDFTypeCombox;
	@FXML
	public ObservableList<String> terrainOpticalData;
	@FXML
	public CheckBox landcoverCheckbox;
	@FXML
	public AnchorPane opticalAnchorPane;
	@FXML
	public AnchorPane landcoverAnchorPane;
	@FXML
	public AnchorPane terrainOpticalAnchorPane;
	
	public Map<String, String> landcoverTypesOpticalMap;
	
	public Label albedoLabel;
	public Label c1Label;
	public Label c2Label;
	public Label c3Label;
	public Label c4Label;
	public Label h1Label;
	public Label h2Label;
	
	public Label soilspectHelp;
	
	public TextField albedoTextField;
	public TextField c1TextField;
	public TextField c2TextField;
	public TextField c3TextField;
	public TextField c4TextField;
	public TextField h1TextField;
	public TextField h2TextField;
	
	
	//forest
	@FXML
	private Button forestTreePosBtn;
//	@FXML
//	public TextField forestTreePosField;
//	public String tree_pos_path;
	@FXML
	public ListView<String> objectLV;
	@FXML
	public TableView positionTable;
	public ObservableList<PositionXY> positionXYData;
	public Map<String, ObservableList<PositionXY> > objectAndPositionMap = new HashMap<String, ObservableList<PositionXY>>();
	
	@FXML
	private Button posAddBtn;
	@FXML
	private Button posDelBtn;
	@FXML 
	private SplitMenuButton posRandom;
	@FXML
	private Button DeleteAllPosBtn;
	@FXML
	public CheckBox objFileCacheChecbox;
	@FXML
	public CheckBox ShowObjectDimensionCheck;
	
	/**
	 * object list
	 */
	public ObservableList<String> objectsList =FXCollections.observableArrayList();
	/**
	 * the component of each object
	 */
	public Map<String, ObservableList<String> > objectsAndCompomentsMap = new HashMap<String, ObservableList<String>>();
	/**
	 * the boundingbox of each object
	 */
	public Map<String, LSBoundingbox> objectAndBoundingboxMap = new HashMap<String, LSBoundingbox>();
	/**
	 * //the optical of each compoment of each object. object_component is the key
	 */
	public Map<String, OpticalThermalProperty> opticalcomponentMap = new HashMap<String, OpticalThermalProperty>();
	@FXML
	private TextField XPosField;
	@FXML
	private TextField YPosField;
	@FXML
	private TextField ZPosField;
	
	//sensor
	@FXML
	private AnchorPane sensorAnchorPane;
	@FXML 
	public VBox sensorVbox;
	@FXML
	public AnchorPane orthographicPane;
	@FXML
	public AnchorPane perspectivePane;
	public AnchorPane ptConfigPanel;//for photon tracing parameters
	public AnchorPane cfConfigPanel;//for fisheye parameters
	@FXML
	public ComboBox<String> comboBoxSensorType;
	@FXML 
	public TextField sensorWidthField;
	@FXML
	public TextField sensorHeightField;
	@FXML
	public Label pixelUnitLabel;
	@FXML 
	public TextField sensorSampleField;
	@FXML
	public TextField sensorBandsField;
	@FXML
	public TextField sensorXExtentField;
	@FXML
	public TextField sensorYExtentField;
	
	public CheckBox orthfourCompsCheckbox;
	public CheckBox perfourCompsCheckbox;
	
	
	@FXML
	public TextField obsAGLField;
	
	public TextField illumResTextField;// for photon tracing
	public CheckBox productBRFCheckbox;// for photon tracing
	public Label virtualLabel;
	public TextField virtualDirTextField;
	public Label numOfDirectionLabel;
	public TextField numOfDirectionTextField;
	public Label virtualDetectorLabel;
	public TextField virtualDetectorTextField;
	public CheckBox productUpDownRadiationCheckbox;// for photon tracing
	
	public CheckBox productfPARChecbox;
	public Label fPARLayerLabel;
	public TextField fPARLayerTextEdit;
	
	public TextField cfFovTextField;// for fisheye parameters
	public ComboBox<String> combobox;
	@FXML
	public TextField xfovField;
	@FXML
	public TextField yfovField;
	@FXML
	public CheckBox firstOrderCheckbox;
	@FXML
	public CheckBox virtualPlaneCheckbox;
	@FXML
	public CheckBox ThermalCheckbox;
	@FXML
	public CheckBox CoverWholeSceneCheckbox;
	@FXML
	public RadioButton spectrumRadio;
	@FXML 
	public RadioButton rgbRadio;
	public ToggleGroup ImageFormatRadioroup;
	@FXML
	public TextField sensorNoDataValueField;
	@FXML
	public TextField sensorRepetitiveSceneTextField;
	
	
	//observation and illumination
	@FXML
	public AnchorPane illuAtmPane;
	@FXML
	public VBox obsVbox;
	@FXML
	public TextField obsZenithField;
	@FXML
	public TextField obsAzimuthField;
	@FXML
	public AnchorPane obsOrthographicPane;
	@FXML
	public AnchorPane obsPerspectivePane;
	@FXML
	public TextField pers_o_x_field;
	@FXML
	public TextField pers_o_y_field;
	@FXML
	public TextField pers_o_z_field;
	@FXML
	public TextField pers_t_x_field;
	@FXML
	public TextField pers_t_y_field;
	@FXML
	public TextField pers_t_z_field;
	@FXML
	public CheckBox CameraPosRelativeHeightCheckbox;
	@FXML
	public CheckBox showCameraPosCheckbox;
	
	@FXML
	public TextField sunZenithField;
	@FXML
	public TextField sunAzimuthField;
	@FXML
	public TextField atsPercentageField;
	@FXML
	public ComboBox<String> atsTypeCombobox;
	public Button atsButton;
	@FXML
	public Label unitLabel;
	@FXML
	private AnchorPane SolarSpectrumPane;
	@FXML
	public CheckBox SolarSpectrumCheckbox;
	@FXML
	public TextField SolarSpectrumSunTextField;
	@FXML
	public TextField SolarSpectrumSkyTextField;
	@FXML
	public AnchorPane SkyTotalPane;
	@FXML
	public AnchorPane skyPane;
	
	
	//console
	@FXML
	private TextArea consoleTextArea;
	public OutputConsole outputConsole;
	private PrintStream ps ;
	
	public RunningStatusThread currentRunningThread;
	public PyLauncher currentPyLaucherThread;
	public boolean isRunning = false;
	
	@FXML
	public Button runBtn;
	
	
	public LessMainApp mainApp;
	
	private ControlJsonWrapper jsonWrapper;
	
	//project related
	public String simulation_path;
	
	public ConstConfig constConfig;
	
	public ProjectManager projManager;
	
	public RunningStatusThread currentRunningStatusThread;
	
	@FXML
	public Label mapInfoLabel;
	public DrawHelper drawHeper;
	@FXML
	public ToolBar DrawToolBar;
	public DrawToolBarHelper drawtoolBarHelper;
	@FXML
	public ScrollPane canvasScrollPane;
	@FXML
	public AnchorPane AnchorInsideScrollPane;
	
	
	//optical db
	@FXML
	public TableView opticalTable;
	@FXML
	private TextField opticalNameField;
	@FXML
	private TextField opticalRefFrantField;
	@FXML
	private TextField opticalRefBackField;
	@FXML
	private TextField opticalTransField;
	public ObservableList<FacetOptical> opticalData;
	public DBReader dbReader = new DBReader();
	@FXML
	public Button ClearSelectionBtn;
	@FXML
	public CheckBox displayPosOn2DCheck;
	@FXML
	public CheckBox HideSelectedCheck;
	
	@FXML
	private Button chooseFromDBBtn;
	@FXML
	private Button importObjectsBtn;
	@FXML 
	private Button importInstancesBtn;
	
	public Map<String, String> temperatureMap = new HashMap<String, String>();
	
	//advanced
	@FXML
	public TextField minIterTextField;
	@FXML
	public TextField NumberofCoresTextField;
	@FXML
	public TextField PyInterpreterEdit;
	
	public void setMainApp(LessMainApp mainApp)
	{
		this.mainApp = mainApp;
	}
	
	
	/**
	 * Do initialization work for the MainWindow
	 */
	public void initView(){
		dbReader.connect();
		drawHeper = new DrawHelper(this);
		projManager = new ProjectManager(this);
		this.drawBasicGrids();
		this.drawSunAndView();
		this.drawOrthographicSensor();
		this.inputValidation();
        this.initalTerrainModule();
        this.addAtmsphereType_Listener();
        this.initSensor();
        this.initSunAndIlluminationView();
        this.initCanvasContextMenu();
        this.initOpticalTableView();
        this.initForestPosTableView();
        this.outputConsole = new OutputConsole(this.consoleTextArea);
		ps = new PrintStream(outputConsole);
		System.setErr(ps);
		System.setOut(ps);
		constConfig = new ConstConfig();
		terrainOpticalCombox.setItems(this.terrainOpticalData);
		
		this.objectLV.setItems(this.objectsList);
		this.objectLV.getSelectionModel().setSelectionMode(SelectionMode.MULTIPLE);
		save_file_before_closing();
		Forest_Pos_add_addListener();
		
		//initial draw toolbar
		drawtoolBarHelper = new DrawToolBarHelper(this);
		drawtoolBarHelper.initDrawToolBar();
		
		FieldUtils.fixBlurryText(this.sensorAnchorPane);
		FieldUtils.fixBlurryText(this.illuAtmPane);
		FieldUtils.fixBlurryText(this.terrainPane);
		
		hidenotImplemented();
		
	}
	
	private void hidenotImplemented(){
		if(Const.LESS_HIDE_NOT_IMPLEMENTED){
			this.importInstancesBtn.setVisible(false);
			this.importObjectsBtn.setVisible(false);
		}
	}
	
	
	private void initCanvasContextMenu(){
		ContextMenu contextMenu = new ContextMenu();
		RadioMenuItem arrowMenuItem = new RadioMenuItem("Show arrows");
		arrowMenuItem.setSelected(true);
		arrowMenuItem.setOnAction(new EventHandler<ActionEvent>() {
            @Override
            public void handle(ActionEvent event) {
            	if(arrowMenuItem.isSelected()){
            		DrawHelper.showArrows = true;
            	}else{
            		DrawHelper.showArrows = false;
            	}
                
                reDrawAll();
            }
        });
		RadioMenuItem gridMenuItem = new RadioMenuItem("Show grid");
		gridMenuItem.setSelected(true);
		gridMenuItem.setOnAction(new EventHandler<ActionEvent>() {
            @Override
            public void handle(ActionEvent event) {
            	if(gridMenuItem.isSelected()){
            		DrawHelper.showGrids = true;
            	}else{
            		DrawHelper.showGrids = false;
            	}
                reDrawAll();
            }
        });
		contextMenu.getItems().addAll(arrowMenuItem, gridMenuItem);
		canvas.setOnContextMenuRequested(e -> contextMenu.show(canvas, e.getScreenX(), e.getScreenY()));
	}
	
	/**
	 * forest
	 */
	@SuppressWarnings("unchecked")
	private void Forest_Pos_add_addListener(){
		this.objectLV.getSelectionModel().selectedItemProperty().addListener(new ChangeListener<String>() {
						
		    @SuppressWarnings("unchecked")
			@Override
		    public void changed(ObservableValue<? extends String> observable, String oldValue, String newValue) {
		    	if(newValue != null){
		    		posAddBtn.setDisable(false);
			        posDelBtn.setDisable(false);
			        DeleteAllPosBtn.setDisable(false);
			        
			        positionTable.setItems(objectAndPositionMap.get(newValue));
//			        objectAndPositionMap.get(newValue).addListener(new ListChangeListener<PositionXY>() {
//			        	 @Override
//			                public void onChanged(javafx.collections.ListChangeListener.Change<? extends PositionXY> pChange) {
//			                    while(pChange.next()) {
//			                    	reDrawAll();
//			                    }
//			                }
//					});
		    	}else{
		    		posAddBtn.setDisable(true);
		    		posDelBtn.setDisable(true);
		    		DeleteAllPosBtn.setDisable(true);
		    	}
		    }
		});
		posAddBtn.setOnAction((event) -> {
		    String objName = objectLV.getSelectionModel().getSelectedItem();
		    String xString = XPosField.getText();
		    String yString = YPosField.getText();
		    String zString = ZPosField.getText();
		    if(!xString.equals("") && !yString.equals("") && !zString.equals("")){
		    	objectAndPositionMap.get(objName).add(new PositionXY(xString, yString,zString));
		    }
		    
		});
		posDelBtn.setOnAction((event) -> {
		    String objName = objectLV.getSelectionModel().getSelectedItem();
		    objectAndPositionMap.get(objName).remove(positionTable.getSelectionModel().getSelectedItem());
		});
		DeleteAllPosBtn.setOnAction((event) -> {
			ObservableList<String> selectedObjs = objectLV.getSelectionModel().getSelectedItems();
			for (String objName : selectedObjs) {
				objectAndPositionMap.get(objName).clear();
			}
		});
		
		
		
		posRandom.setOnAction((event) -> {
		   // String objName = objectLV.getSelectionModel().getSelectedItem();
		    //open new dialog for tree position generate
		    if(this.simulation_path == null){
				outputConsole.log("Please create a simulation first.\n");
				return;
			}
			try {
				FXMLLoader loader = new FXMLLoader();
				loader.setLocation(LessMainWindowController.class.getResource("TreePosGenerateView.fxml"));
				BorderPane rootLayout = (BorderPane) loader.load();
				Scene scene = new Scene(rootLayout);
				Stage subStage = new Stage();
				subStage.setScene(scene);
				subStage.setTitle("Tree Position Generation");
				TreePosGenerateController treeposController = loader.getController();
				treeposController.setMainWindowController(this);
				treeposController.setParentStage(subStage);
				treeposController.initView();
				subStage.getIcons().add(new Image(LessMainApp.class.getResourceAsStream("LESS16_16.png")));
				subStage.getIcons().add(new Image(LessMainApp.class.getResourceAsStream("LESS32_32.png")));
				subStage.initOwner(this.mainApp.getPrimaryStage());
				subStage.show();
				
			} catch (IOException e) {
				e.printStackTrace();
			}
		    
		    
		});
	}
	
	/**
	 * Import tree position from CHM image
	 */
	@FXML
	private void treePosFromCHM(){
		this.projManager.treePosFromCHM();
	}
	
	@FXML
	private void onDisplayPosOn2DCheck(){
		this.projManager.onDisplayPosOn2DCheck();
	}
	
	@FXML
	private void onShowObjectDimensionCheck() {
		this.projManager.onShowObjectDimensionCheck();
	}
	
	@FXML
	private void onHideSelectedOn2DCheck(){
		this.projManager.onHideSelectedOn2DCheck();
	}
	
	
	private void save_file_before_closing(){
		this.mainApp.getPrimaryStage().setOnCloseRequest(new EventHandler<WindowEvent>() {
		      public void handle(WindowEvent we) {
		    	  final_save();
		    	  stop_simulation();
		    	  projManager.closingAllPyConsole();
		    	 // PyLauncher.killLessRT();
		      }
		  }); 
	}
	
	private void final_save(){
		if(this.simulation_path != null){
			save_parameters();
		}
	}	
	
	/**
	 * Prevent the invalid inputs
	 */
	private void inputValidation(){
		java.util.Locale locale = new java.util.Locale("en");
		NumberStringFilteredConverter converter = new NumberStringFilteredConverter(locale);
        final TextFormatter<Number> formatterX = new TextFormatter<>(
                converter,
                100,
                converter.getFilter()
        );
        sceneXSizeField.setTextFormatter(formatterX);
        formatterX.valueProperty().addListener((observable, oldValue, newValue) ->
        				reDrawAll()      		
        		);
        final TextFormatter<Number> formatterY = new TextFormatter<>(
                converter,
                100,
                converter.getFilter()
        );
        formatterY.valueProperty().addListener((observable, oldValue, newValue) ->
        				reDrawAll()      		
        		);
        sceneYSizeField.setTextFormatter(formatterY);   
        xfovField.setTextFormatter(new TextFormatter<>(converter,45,converter.getFilter()));
        yfovField.setTextFormatter(new TextFormatter<>(converter,30,converter.getFilter()));
        final TextFormatter<Number> formatterobsZenith = new TextFormatter<>(
                converter,
                0,
                converter.getFilter()
        );
        formatterobsZenith.valueProperty().addListener((observable, oldValue, newValue) ->
        				reDrawAll()      		
        		);
        
        obsZenithField.setTextFormatter(formatterobsZenith);
        final TextFormatter<Number> formatterobsAzimuth = new TextFormatter<>(
                converter,
                180,
                converter.getFilter()
        );
        formatterobsAzimuth.valueProperty().addListener((observable, oldValue, newValue) ->
        				reDrawAll()      		
        		);
    	obsAzimuthField.setTextFormatter(formatterobsAzimuth);
    	final TextFormatter<Number> formatterobszenith = new TextFormatter<>(
                converter,
                45,
                converter.getFilter()
        );
    	formatterobszenith.valueProperty().addListener((observable, oldValue, newValue) ->
        				reDrawAll()      		
        		);
    	
    	sunZenithField.setTextFormatter(formatterobszenith);
    	final TextFormatter<Number> formattersunAzimuth = new TextFormatter<>(
                converter,
                90,
                converter.getFilter()
        );
    	formattersunAzimuth.valueProperty().addListener((observable, oldValue, newValue) ->
    					reDrawAll()     		
    	);
    	sunAzimuthField.setTextFormatter(formattersunAzimuth);
    	sensorWidthField.setTextFormatter(new TextFormatter<>(converter,100,converter.getFilter()));
    	sensorHeightField.setTextFormatter(new TextFormatter<>(converter,100,converter.getFilter()));
    	sensorSampleField.setTextFormatter(new TextFormatter<>(converter,128,converter.getFilter()));
    	final TextFormatter<Number> formatterSensorXExtent = new TextFormatter<>(
                converter,
                100,
                converter.getFilter()
        );
    	formatterSensorXExtent.valueProperty().addListener((observable, oldValue, newValue) ->
    						reDrawAll()     		
    				);
    	sensorXExtentField.setTextFormatter(formatterSensorXExtent);
    	final TextFormatter<Number> formatterSensorYExtent = new TextFormatter<>(
                converter,
                100,
                converter.getFilter()
        );
    	formatterSensorYExtent.valueProperty().addListener((observable, oldValue, newValue) ->
    						reDrawAll()     		
    				);
    	
    	sensorYExtentField.setTextFormatter(formatterSensorYExtent);
    	xfovField.setTextFormatter(new TextFormatter<>(converter,40,converter.getFilter()));
    	yfovField.setTextFormatter(new TextFormatter<>(converter,30,converter.getFilter()));
    	
    	sensorBandsField.textProperty().addListener((observable, oldValue, newValue) -> {
    		String skylstr = this.atsPercentageField.getText().trim();
    		String [] bands = newValue.split(",");
    		String [] skyls = skylstr.split(",");
    		int bandnum = bands.length;
    		String finalstr = "";
    		for(int i=0;i<bandnum;i++){
    			if(i<skyls.length){
    				finalstr += skyls[i]+",";
    			}else{
    				finalstr += "0.0,";
    			}
    		}
    		finalstr = finalstr.substring(0, finalstr.length()-1);
    		this.atsPercentageField.setText(finalstr);
    	    //System.out.println("textfield changed from " + oldValue + " to " + newValue);
    	});
    	
    	//perspective camera
    	pers_o_x_field.textProperty().addListener((observable, oldValue, newValue) -> {
    		reDrawAll();
    	});
    	pers_o_y_field.textProperty().addListener((observable, oldValue, newValue) -> {
    		reDrawAll();
    	});
    	pers_o_z_field.textProperty().addListener((observable, oldValue, newValue) -> {
    		reDrawAll();
    	});
    	pers_t_x_field.textProperty().addListener((observable, oldValue, newValue) -> {
    		reDrawAll();
    	});
    	pers_t_y_field.textProperty().addListener((observable, oldValue, newValue) -> {
    		reDrawAll();
    	});
    	pers_t_z_field.textProperty().addListener((observable, oldValue, newValue) -> {
    		reDrawAll();
    	});
    	xfovField.textProperty().addListener((observable, oldValue, newValue) -> {
    		reDrawAll();
    	});
    	yfovField.textProperty().addListener((observable, oldValue, newValue) -> {
    		reDrawAll();
    	});
	}
	
	/**
	 * init terrain
	 */
	private void initalTerrainModule() {
		this.projManager.initTerrainModule();
	}
	
	private void addAtmsphereType_Listener() {
		atsTypeCombobox.valueProperty().addListener(new ChangeListener<String>() {
			@Override 
			public void changed(ObservableValue ov, String oldVal, String newVal) {
				if(newVal.equals(Const.LESS_ATS_TYPE_SKY)){
					skyPane.getChildren().remove(atsButton);
					skyPane.getChildren().add(SkyTotalPane);
				}
				if (newVal.equals(Const.LESS_ATS_TYPE_ATS)){
					skyPane.getChildren().remove(SkyTotalPane);
					//add a button to show atmosphere dialog
					atsButton = new Button("Define Atmosphere...");
					skyPane.getChildren().add(atsButton);
					AnchorPane.setLeftAnchor(atsButton, 150.0);
					AnchorPane.setTopAnchor(atsButton, 80.0);
					atsButton.setOnAction(new EventHandler<ActionEvent>() {
					    @Override public void handle(ActionEvent e) {
					    	projManager.OpenAtmosphereEditor();
					    }
					});				
				}
		    } 
		});
	}
	
	/**
	 * 
	 */
	private void initSensor(){
		this.projManager.initSensor();
	}
	
	/**
	 * 
	 */
	@SuppressWarnings("unchecked")
	private void initForestPosTableView(){
		positionTable.setEditable(true);
		TableColumn xCol = new TableColumn("X");
	    TableColumn yCol = new TableColumn("Y");
	    TableColumn zCol = new TableColumn("Z");
	    positionTable.getColumns().addAll(xCol,yCol,zCol);
	    positionXYData = FXCollections.observableArrayList();
	    xCol.setCellValueFactory(new PropertyValueFactory<PositionXY, String>("pos_x"));
	    yCol.setCellValueFactory(new PropertyValueFactory<PositionXY, String>("pos_y"));
	    zCol.setCellValueFactory(new PropertyValueFactory<PositionXY, String>("pos_z"));
	    positionTable.setItems(positionXYData);
	    xCol.setCellFactory(TextFieldTableCell.forTableColumn());
	    xCol.setOnEditCommit(
	        new EventHandler<CellEditEvent<PositionXY, String>>() {
	            @Override
	            public void handle(CellEditEvent<PositionXY, String> t) {
	                ((PositionXY) t.getTableView().getItems().get(
	                    t.getTablePosition().getRow())
	                    ).setPos_x(t.getNewValue());
	            }
	        }
	    );
	    yCol.setCellFactory(TextFieldTableCell.forTableColumn());
	    yCol.setOnEditCommit(
	        new EventHandler<CellEditEvent<PositionXY, String>>() {
	            @Override
	            public void handle(CellEditEvent<PositionXY, String> t) {
	                ((PositionXY) t.getTableView().getItems().get(
	                    t.getTablePosition().getRow())
	                    ).setPos_y(t.getNewValue());
	            }
	        }
	    );
	    zCol.setCellFactory(TextFieldTableCell.forTableColumn());
	    zCol.setOnEditCommit(
	        new EventHandler<CellEditEvent<PositionXY, String>>() {
	            @Override
	            public void handle(CellEditEvent<PositionXY, String> t) {
	                ((PositionXY) t.getTableView().getItems().get(
	                    t.getTablePosition().getRow())
	                    ).setPos_z(t.getNewValue());
	            }
	        }
	    );
	}
	
	/**
	 * initialize Sun and Illumination panel
	 */
	private void initSunAndIlluminationView(){
		unitLabel.setText("W·m"+'\u207B'+'\u00B2'+"·"+"nm"+'\u207B'+'\u00B9');
		SolarSpectrumPane.setVisible(false);
		SolarSpectrumCheckbox.selectedProperty().addListener(new ChangeListener<Boolean>() {
	        public void changed(ObservableValue<? extends Boolean> ov,
	                Boolean old_val, Boolean new_val) {
	                    if(new_val){
	                    	SolarSpectrumPane.setVisible(true);
	                    	atsPercentageField.setDisable(true);
	                    }
	                    else{
	                    	SolarSpectrumPane.setVisible(false);
	                    	atsPercentageField.setDisable(false);
	                    }
	            }
	        });
	}
	
	/**
	 * init table view
	 */
	@SuppressWarnings("unchecked")
	private void initOpticalTableView(){
		opticalTable.setEditable(true);
		Callback<TableColumn, TableCell> cellFactory =
	             new Callback<TableColumn, TableCell>() {
	                 public TableCell call(TableColumn p) {
	                    return new EditingCell();
	                 }
	             };
		TableColumn opticalNameCol = new TableColumn("Name");
	    TableColumn ReflectanceFrontCol = new TableColumn("Reflectance (Front)");
	    TableColumn ReflectanceBackCol = new TableColumn("Reflectance (Back)");
	    TableColumn TransmittanceCol = new TableColumn("Transmittance");
	    opticalTable.getColumns().addAll(opticalNameCol, ReflectanceFrontCol, ReflectanceBackCol, TransmittanceCol);
	    String wavelength_and_bandwidth = this.sensorBandsField.getText().trim();
	    opticalData = FXCollections.observableArrayList(
			    dbReader.getOpticalTableElementByName(Const.LESS_DEFAULT_OPTICAL1, wavelength_and_bandwidth),
			    dbReader.getOpticalTableElementByName(Const.LESS_DEFAULT_OPTICAL2, wavelength_and_bandwidth),
			    dbReader.getOpticalTableElementByName(Const.LESS_DEFAULT_OPTICAL3, wavelength_and_bandwidth)
			);
	    //initialize terrain optical
	    terrainOpticalData = FXCollections.observableArrayList(Const.LESS_DEFAULT_OPTICAL1,Const.LESS_DEFAULT_OPTICAL2,Const.LESS_DEFAULT_OPTICAL3);
	    this.terrainOpticalCombox.getSelectionModel().select(Const.LESS_DEFAULT_OPTICAL2);
	    opticalNameCol.setCellValueFactory(new PropertyValueFactory<FacetOptical, String>("opticalName"));
	    ReflectanceFrontCol.setCellValueFactory(new PropertyValueFactory<FacetOptical, String>("reflectanceFront"));
	    ReflectanceBackCol.setCellValueFactory(new PropertyValueFactory<FacetOptical, String>("reflectanceBack"));
	    TransmittanceCol.setCellValueFactory(new PropertyValueFactory<FacetOptical, String>("transmittance"));
	    opticalTable.setItems(opticalData);
	    
	    ClearSelectionBtn.setOnAction((event) -> { 
	    	objectLV.getSelectionModel().select(-1);
	    });
	    
	    opticalNameCol.setCellFactory(TextFieldTableCell.forTableColumn());
	    opticalNameCol.setOnEditCommit(
	        new EventHandler<CellEditEvent<FacetOptical, String>>() {
	            @Override
	            public void handle(CellEditEvent<FacetOptical, String> t) {
	               String oldVal = t.getOldValue();
	                ((FacetOptical) t.getTableView().getItems().get(
	                    t.getTablePosition().getRow())
	                    ).setOpticalName(t.getNewValue());
	                int index = terrainOpticalData.indexOf(oldVal);
	                terrainOpticalData.add(index, t.getNewValue());
	                terrainOpticalData.remove(oldVal);
	                
	            }
	        }
	    );
	    ReflectanceFrontCol.setCellFactory(TextFieldTableCell.forTableColumn());
	    ReflectanceFrontCol.setOnEditCommit(
		        new EventHandler<CellEditEvent<FacetOptical, String>>() {
		            @Override
		            public void handle(CellEditEvent<FacetOptical, String> t) {
		                ((FacetOptical) t.getTableView().getItems().get(
		                    t.getTablePosition().getRow())
		                    ).setReflectanceFront(t.getNewValue());
		            }
		        }
		    );
	    
	    ReflectanceBackCol.setCellFactory(TextFieldTableCell.forTableColumn());
	    ReflectanceBackCol.setOnEditCommit(
		        new EventHandler<CellEditEvent<FacetOptical, String>>() {
		            @Override
		            public void handle(CellEditEvent<FacetOptical, String> t) {
		                ((FacetOptical) t.getTableView().getItems().get(
		                    t.getTablePosition().getRow())
		                    ).setReflectanceBack(t.getNewValue());
		            }
		        }
		    );
	    
	    TransmittanceCol.setCellFactory(TextFieldTableCell.forTableColumn());
	    TransmittanceCol.setOnEditCommit(
		        new EventHandler<CellEditEvent<FacetOptical, String>>() {
		            @Override
		            public void handle(CellEditEvent<FacetOptical, String> t) {
		                ((FacetOptical) t.getTableView().getItems().get(
		                    t.getTablePosition().getRow())
		                    ).setTransmittance(t.getNewValue());
		            }
		        }
		    );
	}
	
	/**
	 * Optical from manual
	 */
	@FXML
	private void addOptical(){
		if(opticalNameField.getText().equals("")||
				opticalRefFrantField.getText().equals("") ||
                opticalRefBackField.getText().equals("")||
                opticalTransField.getText().equals(""))
		{
			outputConsole.log("Optical should not be empty.\n");
			return;
		}
		opticalData.add(new FacetOptical(
                opticalNameField.getText(),
                opticalRefFrantField.getText(),
                opticalRefBackField.getText(),
                opticalTransField.getText(), Const.LESS_OP_TYPE_MANUAL));
		terrainOpticalData.add(opticalNameField.getText());
	}
	@FXML
	private void copyOptical(){
		FacetOptical facetOptical = (FacetOptical) opticalTable.getSelectionModel().getSelectedItem();
		if(facetOptical != null){
			String newName = facetOptical.getOpticalName()+"_copy";
			for(FacetOptical fo: opticalData) {
				if(fo.getOpticalName().equals(newName)) {
					newName += "_copy";
				}
			}
			opticalData.add(new FacetOptical(
					newName,
					facetOptical.getReflectanceFront(),
	                facetOptical.getReflectanceBack(),
	                facetOptical.getTransmittance(),Const.LESS_OP_TYPE_MANUAL));
			terrainOpticalData.add(newName);
		}
		
	}
	@FXML
	private void deleteOptical(){
		FacetOptical facetOptical = (FacetOptical) opticalTable.getSelectionModel().getSelectedItem();
		if(facetOptical != null){
			terrainOpticalData.remove(facetOptical.getOpticalName());
			opticalTable.getItems().remove(
					facetOptical
				    );
		}		
	}
	
	/*
	 * ***********************************************************
	 * functions related to 2D drawing.
	 * ***********************************************************
	 */
	/**
	 * Draw basic grids on the canvas
	 */
	private void drawBasicGrids(){
		this.drawHeper.drawBasicGrids();
	}
	
	private void drawSunAndView(){
		this.drawHeper.drawSunAndView();
	}
	
	/**
	 * Draw extent of orthgraphic sensor
	 */
	private void drawOrthographicSensor(){
		this.drawHeper.drawOrthgraphicCameraAndSensor();
	}
	
	/**
	 * Redraw all when Resizing or change sensor value
	 */
	public void reDrawAll(){
		this.drawHeper.reDrawAll();		
	}
	@FXML
	public void onLoadPolygon(){
		this.drawtoolBarHelper.onLoadPolygon();
	}
	@FXML
	public void onSavePolygon(){
		this.drawtoolBarHelper.onSavePolygon();
	}
	
	/*
	 * ********************************************************
	 * End
	 * ********************************************************
	 */
	
	
	//terrain
	@FXML
	private void selectTerrainFile(){
		this.projManager.selectTerrainFile();
	}
	
	
	// import land cover map
	@FXML
	private void handleLandcoverCheckbox(){
		this.projManager.handleLandcoverCheckbox();
	}
	
	@FXML
	private void handleThermalRadiationCheckbox(){
		this.projManager.handleThermalRadiationCheckbox();
	}
	
	@FXML
	private void handlePlaneCheckbox(){
		this.projManager.handlePlaneCheckbox();
	}
	
	
	@FXML
	private void handleWholeSceneCheckbox(){
		this.projManager.handleWholeSceneCheckbox();
	}
	/**
	 * open window for define objects
	 */
	@FXML
	private void onDefineForest(){
		if(this.simulation_path == null){
			outputConsole.log("Please create a simulation first.\n");
			return;
		}
		try {
			FXMLLoader loader = new FXMLLoader();
			loader.setLocation(LessMainWindowController.class.getResource("ObjectsDefineWindowView.fxml"));
			BorderPane rootLayout = (BorderPane) loader.load();
			Scene scene = new Scene(rootLayout);
			Stage subStage = new Stage();
			subStage.setScene(scene);
			subStage.setTitle("Objects Definition");
			ObjectsDefineWindowViewController objController = loader.getController();
			objController.setMainWindowController(this);
			objController.setParentStage(subStage);
			objController.initView();
			subStage.getIcons().add(new Image(LessMainApp.class.getResourceAsStream("LESS16_16.png")));
			subStage.getIcons().add(new Image(LessMainApp.class.getResourceAsStream("LESS32_32.png")));
			subStage.initOwner(this.mainApp.getPrimaryStage());
			subStage.show();
			
		} catch (IOException e) {
			e.printStackTrace();
		}
		
	}
	
	/**
	 * open DB reader
	 */
	@FXML
	private void OpenDBChooser(){
		try {
			FXMLLoader loader = new FXMLLoader();
			loader.setLocation(LessMainWindowController.class.getResource("DBChooserView.fxml"));
			BorderPane rootLayout = (BorderPane) loader.load();
			Scene scene = new Scene(rootLayout);
			Stage subStage = new Stage();
			subStage.setScene(scene);
			subStage.setTitle("Band Definition");
			DBChooserController dbController = loader.getController();
			dbController.setMainWindowController(this);
			dbController.setParentStage(subStage);
			//objController.setOpticalData(this.terrainOpticalData);
			//objController.setObjectData(objectsList, objectsAndCompomentsMap, opticalcomponentMap);
			dbController.initView();
			subStage.getIcons().add(new Image(LessMainApp.class.getResourceAsStream("LESS16_16.png")));
			subStage.getIcons().add(new Image(LessMainApp.class.getResourceAsStream("LESS32_32.png")));
			subStage.initOwner(this.mainApp.getPrimaryStage());
			subStage.show();
			
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
	
	/**
	 * Open Prospect-D dialog
	 */
	
	@FXML
	private void OpenProspectD() {
		this.projManager.OpenProspectD();
	}
	
	@FXML
	private void OpenSunPosCalculator(){
		this.projManager.OpenSunPosCalculator();
	}
	
	/**
	 * refresh DB
	 */
	@FXML
	private void RefreshDB(){
		String waveLength_and_bandwidth = this.sensorBandsField.getText().trim();
		
		dbReader.refreshOpticalDB(this, opticalData, waveLength_and_bandwidth);
		
	}
	
	@FXML
	private void PlotSpectra() {
		this.projManager.PlotSpectra();
	}
	
	@FXML
	private void showCameraPos() {
		this.reDrawAll();
	}
	
	
	/**
	 * open window for define forests
	 */
	@FXML
	private void openBandsDefineWindow(){
		if(this.simulation_path == null){
			outputConsole.log("Please create a simulation first.\n");
			return;
		}
		try {
			FXMLLoader loader = new FXMLLoader();
			loader.setLocation(LessMainWindowController.class.getResource("SpectralBandsDefineView.fxml"));
			BorderPane rootLayout = (BorderPane) loader.load();
			Scene scene = new Scene(rootLayout);
			Stage subStage = new Stage();
			subStage.setScene(scene);
			subStage.setTitle("Band Definition");
			SpectralBandsDefineController bandController = loader.getController();
			bandController.setMainWindowController(this);
			bandController.setParentStage(subStage);
			//objController.setOpticalData(this.terrainOpticalData);
			//objController.setObjectData(objectsList, objectsAndCompomentsMap, opticalcomponentMap);
			bandController.initView();
			subStage.getIcons().add(new Image(LessMainApp.class.getResourceAsStream("LESS16_16.png")));
			subStage.getIcons().add(new Image(LessMainApp.class.getResourceAsStream("LESS32_32.png")));
			subStage.show();
			
		} catch (IOException e) {
			e.printStackTrace();
		}
		
	}
	
	/**
	 * open about dialog
	 */
	@FXML
	private void OpenAboutDialog(){
		this.projManager.OpenAboutDialog();
	}
	
	public ListChangeListener<PositionXY> tree_pos_change_listener = new ListChangeListener<PositionXY>() {
      	 @Override
         public void onChanged(javafx.collections.ListChangeListener.Change<? extends PositionXY> pChange) {
             while(pChange.next()) {
            	 if(!StopDrawTree)
            		 reDrawAll();
             }
         }
	};
	
	/**
	 * load objects
	 */
	private void load_objects_file(){
		//clear before load
		objectsList.clear();
		for(Map.Entry<String, ObservableList<PositionXY>> entry: this.objectAndPositionMap.entrySet()){
			entry.getValue().clear();
		}
		objectAndPositionMap.clear();
		objectsAndCompomentsMap.clear();
		
		opticalcomponentMap.clear();
		String param_path = this.projManager.getParameterDirPath();
		File objectsfile = Paths.get(param_path, Const.LESS_OBJECTS_FILE_NAME).toFile();
		if(objectsfile.exists()){
			try (BufferedReader reader = new BufferedReader(new FileReader(objectsfile))) {
		        String line;
		        int objnum = 0;
		        while ((line = reader.readLine()) != null){
		        	String [] arr = line.trim().split(" ");
		        	String objName = arr[0];
		        	objectsList.add(objName);
		        	if(!objectAndPositionMap.containsKey(objName)){
		        		objectAndPositionMap.put(objName, FXCollections.observableArrayList());
		        		this.objectAndPositionMap.get(objName).addListener(tree_pos_change_listener);
		        	}
		        	ObservableList<String> compList = FXCollections.observableArrayList();
		        	//compatible with older simulation project
		        	if(arr[4].startsWith("0x")) {
		        		for(int i=1;i<arr.length;i=i+4){
			        		String compName = arr[i];
			        		compList.add(compName);
			        		String opticalName = arr[i+1];
			        		String temperName = arr[i+2];
			        		String colorStr = arr[i+3];
			        		OpticalThermalProperty property = new OpticalThermalProperty(opticalName, temperName, colorStr);
			        		opticalcomponentMap.put(objName+"_"+compName, property);
			        	}
		        	}else {
		        		for(int i=1;i<arr.length;i=i+3){
			        		String compName = arr[i];
			        		compList.add(compName);
			        		String opticalName = arr[i+1];
			        		String temperName = arr[i+2];
			        		OpticalThermalProperty property = new OpticalThermalProperty(opticalName, temperName);
			        		if(CommonUitls.contain_branch_names(compName)){
			        			property.setComponentColor(Const.LESS_DEFAULT_BRANCH_COLOR);
			        		}
			        		opticalcomponentMap.put(objName+"_"+compName, property);
			        	}
		        	}
		        	
		        	objectsAndCompomentsMap.put(objName, compList);
		        }  

		    } catch (IOException e) {
		    }
		}
		
		//load bounding box
		File boundingboxFile = Paths.get(this.projManager.getParameterDirPath(),Const.LESS_OBJECTS_BOUNDINGBOX_FILE).toFile();
		if(boundingboxFile.exists()){
			try (BufferedReader reader = new BufferedReader(new FileReader(boundingboxFile))) {
				String line;
				while ((line = reader.readLine()) != null){
					if(!line.equals("")){
						String [] arr = line.trim().split(":");
						LSBoundingbox lsBoundingbox = new LSBoundingbox();
						lsBoundingbox.loadFromString(arr[1]);
						this.objectAndBoundingboxMap.put(arr[0], lsBoundingbox);
					}
				}
				
			} catch (FileNotFoundException e) {
				e.printStackTrace();
			} catch (IOException e) {
				e.printStackTrace();
			}
		}
	}
	
	/**
	 * load instances.txt 
	 */
	public void load_instances_file(){
		String param_path = this.projManager.getParameterDirPath();
		File instancefile = Paths.get(param_path, Const.LESS_INSTANCE_FILE_NAME).toFile();
		if(instancefile.exists()){
			try (BufferedReader reader = new BufferedReader(new FileReader(instancefile))) {
		        String line;
		        int objnum = 0;
		        this.StopDrawTree = true;
//		        for(int i=0;i<objectsList.size();i++)
//		        	objectAndPositionMap.get(objectsList.get(i)).removeListener(tree_pos_change_listener);
		        while ((line = reader.readLine()) != null){
		        	String [] arr = line.trim().split(" ");
		        	String objName = arr[0];
		        	String extra_props = "";
		        	if (arr.length > 4 ){
		        		for(int k = 4;k<arr.length;k++){
		        			extra_props += arr[k]+" ";
		        		}
		        	}
		        	objectAndPositionMap.get(objName).add(new PositionXY(arr[1], arr[2], arr[3], extra_props));
		        }
		        this.StopDrawTree = false;
//		        for(int i=0;i<objectsList.size();i++)
//		        	objectAndPositionMap.get(objectsList.get(i)).addListener(tree_pos_change_listener);
		    } catch (IOException e) {
		    }
		}
	}
	
	//project management
	@FXML
	private void newSim(){
		DirectoryChooser directoryChooser = new DirectoryChooser();
		directoryChooser.setTitle("New simulation: choose an empty folder.");
		String lastOpened = getLastOpenedPath(Const.LAST_OPENED_SIM);
		if (lastOpened != null && new File(lastOpened).exists()){
			directoryChooser.setInitialDirectory(new File(lastOpened));
		}
		File selectedDirectory = directoryChooser.showDialog(this.mainApp.getPrimaryStage());
		if(selectedDirectory != null)
		{
			if(!selectedDirectory.exists()){
				if(!selectedDirectory.mkdirs()){
					outputConsole.log("Creating simulation folder failed.");
					return;
				}
			}
			setLastOpenedPath(Const.LAST_OPENED_SIM,selectedDirectory.toString());
			this.simulation_path = selectedDirectory.getAbsolutePath();
			if(projManager.isAreadyASimulation())
			{
				outputConsole.log("The chosen folder is already a simulation.\n");
				return;
			}
			CountDownLatch latch = new CountDownLatch(1);
			PyLauncher pyLauncher = new PyLauncher();
			pyLauncher.prepare(this.simulation_path, PyLauncher.Operation.NEW_SIM, latch, outputConsole);
			pyLauncher.start();
			try {
				latch.await();
			} catch (InterruptedException e) {
				e.printStackTrace();
			}
			mainApp.getPrimaryStage().setTitle(Const.LESS_TITLE+simulation_path);
			//save parameters
			//save_parameters();
			projManager.copyDefaultConfigfile();
			projManager.clear_proj();
			//load back to reset all controls
			load_parameters();
		}
			
	}
	
	@FXML
	private void openSim(){
		DirectoryChooser directoryChooser = new DirectoryChooser();
		String lastOpened = getLastOpenedPath(Const.LAST_OPENED_SIM);
		if (lastOpened != null && new File(lastOpened).exists()){
			directoryChooser.setInitialDirectory(new File(lastOpened));
		}
		File selectedDirectory = directoryChooser.showDialog(this.mainApp.getPrimaryStage());
		if(selectedDirectory != null){
			//check whether a valid project
			File dotlessFile = Paths.get(selectedDirectory.toString(), Const.LESS_DOT_LESS_FILE).toFile();
			if (!dotlessFile.exists()){
				outputConsole.log("Not a valid simulation folder\n");
				return;
			}
			setLastOpenedPath(Const.LAST_OPENED_SIM,selectedDirectory.toString());
			this.simulation_path = selectedDirectory.getAbsolutePath();
			mainApp.getPrimaryStage().setTitle(Const.LESS_TITLE+simulation_path);
			//load paraters
			load_parameters();
			//load forest
			load_objects_file();
			load_instances_file();
			reDrawAll();
			outputConsole.log("Successfully load simulation: " + simulation_path + "\n");
		}		
	}
	
	
	@FXML
	public void saveSim(){
		this.before_run();
	}
	
	@FXML
	private void saveAsSim(){
		DirectoryChooser directoryChooser = new DirectoryChooser();
		String lastOpened = getLastOpenedPath(Const.LAST_OPENED_SIM);
		if (lastOpened != null){
			directoryChooser.setInitialDirectory(new File(lastOpened));
		}
		File selectedDirectory = directoryChooser.showDialog(this.mainApp.getPrimaryStage());
		if(selectedDirectory != null){
			//save project
			before_run();
			setLastOpenedPath(Const.LAST_OPENED_SIM,selectedDirectory.toString());
			//old path
			String old = this.simulation_path;
			this.simulation_path = selectedDirectory.getAbsolutePath();
			CountDownLatch latch = new CountDownLatch(1);
			currentPyLaucherThread = new PyLauncher();
			currentPyLaucherThread.setTmpData(old);
			currentPyLaucherThread.prepare(this.simulation_path, PyLauncher.Operation.SAVE_AS, latch, outputConsole);
			currentPyLaucherThread.start();
			try {
				latch.await();
			} catch (InterruptedException e) {
				e.printStackTrace();
			}
			mainApp.getPrimaryStage().setTitle(Const.LESS_TITLE+simulation_path);
		}
	}
	
	
	/**
	 */
	@FXML
	public void before_run(){
		if(this.simulation_path==null){
			outputConsole.log("No simulation.\n");
			return;
		}
		this.RefreshDB();
		ControlJsonWrapper controlJsonWrapper = new ControlJsonWrapper(this);
		save_parameters();
		//if can not parsing the check validation
		if(!controlJsonWrapper.checkInput()){
			return;
		}
		
	}
	
	@FXML
	private void generateViewIllumination(){
		before_run();
		CountDownLatch latch = new CountDownLatch(1);
		currentPyLaucherThread = new PyLauncher();
		currentPyLaucherThread.prepare(this.simulation_path, PyLauncher.Operation.GENERATE_V_I, latch, outputConsole);
		currentRunningStatusThread = new RunningStatusThread(currentPyLaucherThread, outputConsole, runBtn);
		currentRunningStatusThread.setMainController(this);
		currentRunningStatusThread.start();
	}
	
	@FXML
	private void generate_3d_model(){
		before_run();
		CountDownLatch latch = new CountDownLatch(1);
		currentPyLaucherThread = new PyLauncher();
		currentPyLaucherThread.prepare(this.simulation_path, PyLauncher.Operation.GENERATE_3D_MODEL, latch, outputConsole);
		currentRunningStatusThread = new RunningStatusThread(currentPyLaucherThread, outputConsole, runBtn);
		currentRunningStatusThread.setMainController(this);
		currentRunningStatusThread.start();
	}
	
	@FXML
	private void run_less(){
		before_run();
		if(this.projManager.isNetworkSim){
			this.outputConsole.log("INFO: Network simulation is enabled.\n");
		}
		CountDownLatch latch = new CountDownLatch(1);
		currentPyLaucherThread = new PyLauncher();
		currentPyLaucherThread.setLessMainController(this);
		currentPyLaucherThread.prepare(this.simulation_path, PyLauncher.Operation.RUN_LESS, latch, outputConsole);
		currentPyLaucherThread.setTmpData(this.NumberofCoresTextField.getText());//Number of cores
		currentRunningStatusThread = new RunningStatusThread(currentPyLaucherThread, outputConsole, runBtn);
		currentRunningStatusThread.setMainController(this);
		currentRunningStatusThread.start();
	}
	
	@FXML
	public void run_all(){
		before_run();
		CountDownLatch latch = new CountDownLatch(1);
		currentPyLaucherThread = new PyLauncher();
		currentPyLaucherThread.prepare(this.simulation_path, PyLauncher.Operation.RUN_ALL, latch, outputConsole);
		currentPyLaucherThread.setTmpData(this.NumberofCoresTextField.getText());//Number of cores
		currentRunningStatusThread = new RunningStatusThread(currentPyLaucherThread, outputConsole, runBtn);
		currentRunningStatusThread.setMainController(this);
		currentRunningStatusThread.start();
	}
	
	
	@FXML
	private void stop_simulation(){
		if(currentRunningStatusThread != null)
			currentRunningStatusThread.stop_current_job();
	}
	
	@FXML
	private void runBRF(){
		CountDownLatch latch = new CountDownLatch(1);
		currentPyLaucherThread = new PyLauncher();
		currentPyLaucherThread.prepare(this.simulation_path, PyLauncher.Operation.RUN_BRF, latch, outputConsole);
		currentRunningStatusThread = new RunningStatusThread(currentPyLaucherThread, outputConsole, runBtn);
		currentRunningStatusThread.setMainController(this);
		currentRunningStatusThread.start();
	}
	
	@FXML
	private void runBT() {
		CountDownLatch latch = new CountDownLatch(1);
		currentPyLaucherThread = new PyLauncher();
		currentPyLaucherThread.prepare(this.simulation_path, PyLauncher.Operation.RUN_BT, latch, outputConsole);
		currentRunningStatusThread = new RunningStatusThread(currentPyLaucherThread, outputConsole, runBtn);
		currentRunningStatusThread.setMainController(this);
		currentRunningStatusThread.start();
	}
	
	private void save_parameters(){
		String parameter_file_path = Paths.get(this.simulation_path,
				constConfig.data.getString("input_dir"),
				constConfig.data.getString("config_file")).toString();
		if(simulation_path != null){
			jsonWrapper = new ControlJsonWrapper(this);
	        Filehelper.save_string_to_file(parameter_file_path, jsonWrapper.controltoJson());
		}
		save_tree_pos_xy();
		
		this.projManager.save_hidden_object_list();
	}
	
	
	/**
	 * save tree posiiton
	 */
	public void save_tree_pos_xy(){
		String param_path = this.projManager.getParameterDirPath();
		String instancefilePath = Paths.get(param_path, Const.LESS_INSTANCE_FILE_NAME).toString();
		
		File parent = new File(instancefilePath);
		if(!parent.getParentFile().exists()){
			return;
		}
		
		BufferedWriter writer = null;
		try {
			writer = new BufferedWriter( new FileWriter(instancefilePath));
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		Boolean empty = true;
		for(Map.Entry<String, ObservableList<PositionXY>> entry: objectAndPositionMap.entrySet()){
			String objName = entry.getKey();
			ObservableList<PositionXY> positionXYs = entry.getValue();
			for(int i=0;i<positionXYs.size();i++){ //component
				empty = false;
				String totalStr = "";
				PositionXY posxy = positionXYs.get(i);
				totalStr += objName+ " " +posxy.getPos_x() + " " + posxy.getPos_y() + " " +posxy.getPos_z() + " " +posxy.getExtra_props();
				totalStr += System.getProperty("line.separator");
				try {
					writer.write( totalStr);
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
		
		
		File ins_file = new File(instancefilePath);
		if(empty && ins_file.exists()){
			try {
				Files.delete(ins_file.toPath());
			} catch (IOException e) {
				e.printStackTrace();
			}
		}
		
	}
	
	
	private void load_parameters(){
		jsonWrapper = new ControlJsonWrapper(this);
		jsonWrapper.json2controls();
	}
	
	
	//clear console
	@FXML
	private void clear_console(){
		this.consoleTextArea.clear();
	}
	/**
	 * Returns the person file preference, i.e. the file that was last opened.
	 * The preference is read from the OS specific registry. If no such
	 * preference can be found, null is returned.
	 * 
	 * @return
	 */

	public String getLastOpenedPath(String Type) {
		String rootdir = System.getProperty("user.dir");
	    File cfgPath = Paths.get(rootdir,Const.LESS_CONFIG_PROPERTIES_FILE).toFile();
	    Properties properties = new Properties();
	    if(cfgPath.exists()){
	    	try {
				properties.load(new FileInputStream(cfgPath));
			} catch (IOException e) {
				e.printStackTrace();
			}
	    	return properties.getProperty(Type);
	    }else{
	    	return null;
	    }
	}

	/**
	 * Sets the file path of the currently loaded file. The path is persisted in
	 * the OS specific registry.
	 * 
	 * @param file the file or null to remove the path
	 */
	public void setLastOpenedPath(String Type, String filepath) {
	    String rootdir = System.getProperty("user.dir");
	    File cfgPath = Paths.get(rootdir,Const.LESS_CONFIG_PROPERTIES_FILE).toFile();
	    Properties properties = new Properties();
	    if(cfgPath.exists()){
	    	try {
				properties.load(new FileInputStream(cfgPath));
			} catch (IOException e) {
				e.printStackTrace();
			}
	    }
	    properties.setProperty(Type, filepath);
		try {
			properties.store(new FileOutputStream(cfgPath), null);
		} catch (IOException e) {
			e.printStackTrace();
		}	    
	}
	
	@FXML
	private void openLiDARSimulator() {
		this.projManager.openLiDARSimulator();
	}
	
	@FXML
	private void OpenResultsFolder(){
		this.projManager.openResultFolder();
	}
	
	@FXML
	private void OpenBatchTool(){
		this.projManager.OpenBatchTool();
	}
	
	@FXML
	private void Open3DViewer(){
		this.drawtoolBarHelper.open3dViewer(false);
	}
	
	@FXML
	private void RunOnCluster(){
		this.projManager.RunOnCluster();
	}
	
	@FXML
	private void Open3DViewerSO(){
		this.drawtoolBarHelper.open3dViewer(true);
	}
	@FXML
	private void RunPythonConsole(){
		this.projManager.RunPythonConsole();
	}
	@FXML
	private void RunLAICalculator(){
		this.projManager.RunLAICalculator();
	}
	
	@FXML
	private void choosePyInterpreter(){
		this.projManager.choosePyInterpreter();
	}
	
	@FXML
	private void startHelpViewer(){
		this.projManager.startHelpViewer();
	}
	
	
	@FXML
	private void OpenDoc(){
		this.mainApp.getHostServices().showDocument(Const.LESS_HELP_ONLINE_URL);
	}
	
	
	
	@FXML
	private void test(){
		jsonWrapper = new ControlJsonWrapper(this);
        System.out.println(jsonWrapper.controltoJson());
	}
	
	@FXML
	private void PyJavaCommunication(){
		this.projManager.PyJavaCommunication();
	}	
	
}
