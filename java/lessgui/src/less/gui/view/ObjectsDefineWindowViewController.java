package less.gui.view;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.nio.file.CopyOption;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.Map;
import java.util.Optional;

import org.apache.commons.io.FilenameUtils;
import org.junit.experimental.theories.Theories;

import com.interactivemesh.jfx.importer.ImportException;
import com.interactivemesh.jfx.importer.obj.ObjModelImporter;

import javafx.beans.value.ChangeListener;
import javafx.beans.value.ObservableValue;
import javafx.collections.FXCollections;
import javafx.collections.ObservableFloatArray;
import javafx.collections.ObservableList;
import javafx.event.Event;
import javafx.event.EventHandler;
import javafx.fxml.FXML;
import javafx.fxml.FXMLLoader;
import javafx.scene.Scene;
import javafx.scene.control.Alert;
import javafx.scene.control.Alert.AlertType;
import javafx.scene.control.Button;
import javafx.scene.control.ButtonType;
import javafx.scene.control.ColorPicker;
import javafx.scene.control.ComboBox;
import javafx.scene.control.ListView;
import javafx.scene.control.SplitMenuButton;
import javafx.scene.control.TextField;
import javafx.scene.control.TextInputDialog;
import javafx.scene.image.Image;
import javafx.scene.layout.AnchorPane;
import javafx.scene.layout.BorderPane;
import javafx.scene.paint.Color;
import javafx.scene.shape.MeshView;
import javafx.scene.shape.ObservableFaceArray;
import javafx.scene.shape.TriangleMesh;
import javafx.stage.FileChooser;
import javafx.stage.Stage;
import javafx.stage.WindowEvent;
import less.LessMainApp;
import less.gui.display3D.Display3DController;
import less.gui.display3D.DisplaySingleObject3DController;
import less.gui.helper.Filehelper;
import less.gui.helper.PyLauncher;
import less.gui.model.LSBoundingbox;
import less.gui.model.OpticalThermalProperty;
import less.gui.model.PositionXY;
import less.gui.utils.CommonUitls;
import less.gui.utils.Const;

public class ObjectsDefineWindowViewController {
	
	@FXML
	public ListView<String> objectsLV;
	@FXML
	private ListView<String> componentLV;
	@FXML
	private SplitMenuButton importBtn;
	@FXML
	private Button DelBtn;
	@FXML
	private Button delNameBtn;
	@FXML
	private TextField objectNameField;
	@FXML
	private ComboBox<String> opticalPropsComboBox;
	@FXML
	private ComboBox<String> opticalTemperComboBox;
	@FXML
	private AnchorPane temperAnchorPane;
	@FXML
	private ColorPicker compColorPicker;
	
	public LessMainWindowController mwController;
	private Stage parentStage;
	private boolean isThermalMode;
	
	public DisplaySingleObject3DController displaySingleObject3DController;
	
	//for scale obj when loading.
	public double fx = 1.0;
	public double fy = 1.0;
	public double fz = 1.0;
	public boolean isTranslate2Origin = false; 
	
	
	public void setMainWindowController(LessMainWindowController mwController){
		this.mwController = mwController;
	}
	
	public void setParentStage(Stage parentStage) {
		this.parentStage = parentStage;
	}
	
	
	@SuppressWarnings({ "unchecked", "rawtypes" })
	public void initView(){
		this.objectsLV.setItems(this.mwController.objectsList);
		//change selection
		this.objectsLV.getSelectionModel().selectedItemProperty().addListener(new ChangeListener<String>() {
		    @Override
		    public void changed(ObservableValue<? extends String> observable, String oldValue, String newValue) {
		    	if(newValue != null){
		    		componentLV.setItems(mwController.objectsAndCompomentsMap.get(newValue));
			        importBtn.setDisable(false);
			        delNameBtn.setDisable(false);
		    	}else{
		    		delNameBtn.setDisable(true);
		    		importBtn.setDisable(true);
		    	}
		        
		    }
		});
		this.componentLV.getSelectionModel().selectedItemProperty().addListener(new ChangeListener<String>() {
		    @Override
		    public void changed(ObservableValue<? extends String> observable, String oldValue, String newValue) {
		       if(newValue != null){
		    	   DelBtn.setDisable(false);
		    	   opticalPropsComboBox.setDisable(false);
		    	   compColorPicker.setDisable(false);
		    	   String objName = objectsLV.getSelectionModel().getSelectedItem();
		    	   String key = objName+"_"+newValue;
		    	   if(mwController.opticalcomponentMap.containsKey(key)){
		    		   OpticalThermalProperty property = mwController.opticalcomponentMap.get(objName+"_"+newValue);
		    		   opticalPropsComboBox.getSelectionModel().select(property.getOpticalName());
		    		   compColorPicker.setValue(property.getComponentColor());
		    	   }
		    	   else{
		    		   opticalPropsComboBox.getSelectionModel().select(null);
		    		   compColorPicker.setValue(Color.DARKGREEN);
		    	   }
		    		   
		    	   
		    	   if(isThermalMode){
		    		   opticalTemperComboBox.setDisable(false);
		    		   if(mwController.opticalcomponentMap.containsKey(key)){
		    			   OpticalThermalProperty opticalThermalProperty = mwController.opticalcomponentMap.get(key);
		    			   String temper = opticalThermalProperty.getTermperatureName();
		    			   opticalTemperComboBox.getSelectionModel().select(temper);
		    		   }else{
		    			   opticalPropsComboBox.getSelectionModel().select(null);
		    		   }
		    	   }
		    	   
		       }else{
		    	   DelBtn.setDisable(true);
		    	   opticalPropsComboBox.setDisable(true);
		    	   compColorPicker.setDisable(true);
		    	   if(isThermalMode){
		    		   opticalTemperComboBox.setDisable(true);
		    	   }
		       }
		    }
		});		
		//optical property
		opticalPropsComboBox.setItems(mwController.terrainOpticalData);
		opticalTemperComboBox.setItems(mwController.projManager.temperatureList);
		opticalPropsComboBox.valueProperty().addListener(new ChangeListener<String>() {
			@Override 
			public void changed(ObservableValue ov, String oldVal, String newVal) {
				if (newVal!=null){
					String objName = objectsLV.getSelectionModel().getSelectedItem();
					String compoName = componentLV.getSelectionModel().getSelectedItem();
					String key = objName+"_"+compoName;
					if(mwController.opticalcomponentMap.containsKey(key)){
						mwController.opticalcomponentMap.get(key).setOpticalName(newVal);
					}else{
						mwController.opticalcomponentMap.put(key, new OpticalThermalProperty(newVal));
					}	
				}
				
			}
		});
		
		opticalTemperComboBox.valueProperty().addListener(new ChangeListener<String>() {
			@Override 
			public void changed(ObservableValue ov, String oldVal, String newVal) {
				if (newVal!=null){
					String objName = objectsLV.getSelectionModel().getSelectedItem();
					String compoName = componentLV.getSelectionModel().getSelectedItem();
					String key = objName+"_"+compoName;
					String opticalName = opticalPropsComboBox.getSelectionModel().getSelectedItem();
					if(mwController.opticalcomponentMap.containsKey(key)){
						mwController.opticalcomponentMap.get(key).setTemperatureName(newVal);
					}else{
						mwController.opticalcomponentMap.put(key, new OpticalThermalProperty(opticalName, newVal));
					}
					
				}
				
			}
		});
		
		compColorPicker.setValue(Color.DARKGREEN);
		compColorPicker.setOnAction(new EventHandler() {
		     public void handle(Event t) {
		        Color c = compColorPicker.getValue();
		        String objName = objectsLV.getSelectionModel().getSelectedItem();
				String compoName = componentLV.getSelectionModel().getSelectedItem();
				String key = objName+"_"+compoName;
				if(mwController.opticalcomponentMap.containsKey(key)){
					mwController.opticalcomponentMap.get(key).setComponentColor(c);
				}else{
					mwController.opticalcomponentMap.put(key, new OpticalThermalProperty(c));
				}
				
				 //change color of single object display
				if(displaySingleObject3DController != null)
					displaySingleObject3DController.changeMeshColor();
		     }
		 });
		
		
		this.parentStage.setOnCloseRequest(new EventHandler<WindowEvent>() {
		      public void handle(WindowEvent we) {
		    	  removeInvalidItemBeforeClosing();
		    	}
		  }); 
		isThermalMode = this.mwController.ThermalCheckbox.isSelected();
		if(isThermalMode){
			temperAnchorPane.setVisible(true);
		}else{
			temperAnchorPane.setVisible(false);
		}
		//load existed file
		//load_objects_file();
	}
	
//	@FXML
//	private void load_objects_file(){
//		String param_path = this.mwController.projManager.getParameterDirPath();
//		File objectsfile = Paths.get(param_path, Const.LESS_OBJECTS_FILE_NAME).toFile();
//		if(objectsfile.exists()){
//			try (BufferedReader reader = new BufferedReader(new FileReader(objectsfile))) {
//		        String line;
//		        int objnum = 0;
//		        while ((line = reader.readLine()) != null){
//		        	String [] arr = line.trim().split(" ");
//		        	String objName = arr[0];
//		        	mwController.objectsList.add(objName);
//		        	ObservableList<String> compList = FXCollections.observableArrayList();
//		        	for(int i=1;i<arr.length;i=i+3){
//		        		String compName = arr[i];
//		        		compList.add(compName);
//		        		String opticalName = arr[i+1];
//		        		String temperName = arr[i+2];
//		        		System.out.println(temperName);
//		        		mwController.opticalcomponentMap.put(objName+"_"+compName, new OpticalThermalProperty(opticalName, temperName));
//		        	}
//		        	mwController.objectsAndCompomentsMap.put(objName, compList);
//		        }  
//
//		    } catch (IOException e) {
//		    }
//		}
//	}
	

	@FXML
	private void AddObjectsName(){
		String objectName = this.objectNameField.getText();
		if(!objectName.equals("")){
			if(mwController.objectsList.contains(objectName)){
				Alert alert = new Alert(AlertType.WARNING);
				alert.setTitle("Warnning");
				alert.setHeaderText("Warnning");
				alert.setContentText("Object:"+objectName+" already exists.");
				ButtonType buttonTypeOne = new ButtonType("OK");
		    	alert.getButtonTypes().setAll(buttonTypeOne);
				alert.showAndWait();
			}
			else if(objectName.contains(" ")) {
				Alert alert = new Alert(AlertType.WARNING);
				alert.setTitle("Warnning");
				alert.setHeaderText("Warnning");
				alert.setContentText("Space is not allowed when defining the object name!");
				ButtonType buttonTypeOne = new ButtonType("OK");
		    	alert.getButtonTypes().setAll(buttonTypeOne);
				alert.showAndWait();
			}
			else{
				mwController.objectsList.add(objectName);
				//this.objectsLV.getSelectionModel().select(objectName);
				mwController.objectsAndCompomentsMap.put(objectName, FXCollections.observableArrayList());
			}
			
		}
	}
	
	@FXML
	private void DeleteObjectName(){
		String selected = this.objectsLV.getSelectionModel().getSelectedItem();
		//remove all the components correspond to the the selected object.
		ObservableList<String> compList = mwController.objectsAndCompomentsMap.get(selected);
		String param_path = this.mwController.projManager.getParameterDirPath();
		for(int i=0;i<compList.size();i++){
			String compName = compList.get(i);
			File obj_file = Paths.get(param_path,compName).toFile();
			try {
				Files.delete(obj_file.toPath());
			} catch (IOException e) {
				e.printStackTrace();
			}
			mwController.opticalcomponentMap.remove(selected + "_" + compName);
		}
		this.mwController.objectsList.remove(selected);
		this.mwController.objectsAndCompomentsMap.remove(selected);
		if(this.mwController.objectAndPositionMap.containsKey(selected)){
			this.mwController.objectAndPositionMap.get(selected).clear();
			this.mwController.objectAndPositionMap.remove(selected);
		}
		if(this.mwController.objectAndBoundingboxMap.containsKey(selected)){
			this.mwController.objectAndBoundingboxMap.remove(selected);
		}
		
	}
	
	@FXML
	private void DeleteCompoment(){
		String objName = this.objectsLV.getSelectionModel().getSelectedItem();
		String compName = this.componentLV.getSelectionModel().getSelectedItem();
		int compIndex = this.componentLV.getSelectionModel().getSelectedIndex();
		//delete corresponding file
		String param_path = this.mwController.projManager.getParameterDirPath();
		File obj_file = Paths.get(param_path,compName).toFile();
		try {
			Files.delete(obj_file.toPath());
		} catch (IOException e) {
			e.printStackTrace();
		}
		
		this.mwController.objectsAndCompomentsMap.get(objName).remove(compName);
		//remove optical properties for the compoment
		this.mwController.opticalcomponentMap.remove(objName + "_" + compName);
		this.mwController.objectAndBoundingboxMap.get(objName).removeChild(compIndex);	
		
	}
	
	
	private void initObjectAndPositionMap(String newValue){
		if(!this.mwController.objectAndPositionMap.containsKey(newValue)){
			this.mwController.objectAndPositionMap.put(newValue, FXCollections.observableArrayList());
        }
		this.mwController.objectAndPositionMap.get(newValue).removeListener(this.mwController.tree_pos_change_listener);
		this.mwController.objectAndPositionMap.get(newValue).addListener(this.mwController.tree_pos_change_listener);
	}
	
	/**
	 * save to file
	 */
	@FXML
	private void SaveObjectstoFile(){
		String param_path = this.mwController.projManager.getParameterDirPath();
		String objectsfilePath = Paths.get(param_path, Const.LESS_OBJECTS_FILE_NAME).toString();
		String totalStr = "";
		for(Map.Entry<String, ObservableList<String>> entry: mwController.objectsAndCompomentsMap.entrySet()){
			String objName = entry.getKey();
			totalStr  += objName;
			ObservableList<String> compList = entry.getValue();
			if(compList.size()==0){
				Alert alert = new Alert(AlertType.WARNING);
				alert.setTitle("Warnning");
				alert.setHeaderText("Warnning");
				alert.setContentText("Object:"+objName+" does not have any component.");
				ButtonType buttonTypeOne = new ButtonType("OK");
		    	alert.getButtonTypes().setAll(buttonTypeOne);
				alert.showAndWait();
				return;
			}
			for(int i=0;i<compList.size();i++){ //component
				String compName = compList.get(i);
				String opticalKey = objName + "_" + compName;
				if(!this.mwController.opticalcomponentMap.containsKey(opticalKey)){
					Alert alert = new Alert(AlertType.WARNING);
					alert.setTitle("Warnning");
					alert.setHeaderText("Warnning");
					alert.setContentText("Component:"+compName+" does not have a optical properties.");
					ButtonType buttonTypeOne = new ButtonType("OK");
			    	alert.getButtonTypes().setAll(buttonTypeOne);
					alert.showAndWait();
					return;
				}else{
					if(this.mwController.opticalcomponentMap.get(opticalKey).getOpticalName()==null){
						Alert alert = new Alert(AlertType.WARNING);
						alert.setTitle("Warnning");
						alert.setHeaderText("Warnning");
						alert.setContentText("Component:"+compName+" does not have a optical properties.");
						ButtonType buttonTypeOne = new ButtonType("OK");
				    	alert.getButtonTypes().setAll(buttonTypeOne);
						alert.showAndWait();
						return;
					}
				}
				OpticalThermalProperty ot = this.mwController.opticalcomponentMap.get(opticalKey);
				totalStr += " "+compName + " " + ot.getOpticalName() + " " +ot.getTermperatureName()+" "+ ot.getComponentColor().toString();
				initObjectAndPositionMap(objName);
			}
			totalStr += System.getProperty("line.separator");
		}
		
		
		if(!totalStr.equals("")){
			Filehelper.save_string_to_file(objectsfilePath, totalStr);
		}
		else{
			File obj_file = new File(objectsfilePath);
			if(obj_file.exists()){
				try {
					Files.delete(obj_file.toPath());
				} catch (IOException e) {
					e.printStackTrace();
				}
			}
			
		}
		
		//save bounding box
		String out_str = "";
		String outPath = Paths.get(this.mwController.projManager.getParameterDirPath(),Const.LESS_OBJECTS_BOUNDINGBOX_FILE).toString();
		for(Map.Entry<String, LSBoundingbox> entry: this.mwController.objectAndBoundingboxMap.entrySet()){
			String objName = entry.getKey();
			String boundingbox_str = entry.getValue().toString();
			out_str += objName + ":" + boundingbox_str + "\n";
		}
		Filehelper.save_string_to_file(outPath, out_str);
		this.parentStage.close();
	}
	
	@FXML
	private void onCancel(){
		removeInvalidItemBeforeClosing();
		this.parentStage.close();
	}
	
	@FXML
	private void OpenSingleObjectDisplay3D(){
		String choosedObjName = this.objectsLV.getSelectionModel().getSelectedItem();
		if(choosedObjName == null){
			System.out.println("Please choose a object to display.");
			return;
		}
		
		FXMLLoader loader = new FXMLLoader();
		loader.setLocation(DisplaySingleObject3DController.class.getResource("DisplaySingleObject3DView.fxml"));
		try {
			BorderPane rootLayout = (BorderPane) loader.load();
			displaySingleObject3DController = loader.getController();
			displaySingleObject3DController.setParentController(this);
			Scene scene = new Scene(rootLayout);
			Stage display3dStage = new Stage();
			display3dStage.setScene(scene);
			display3dStage.setTitle("3D Object Viewer");
			displaySingleObject3DController.setParentStage(display3dStage);
			displaySingleObject3DController.initDisplay3D();
			display3dStage.getIcons().add(new Image(LessMainApp.class.getResourceAsStream("LESS16_16.png")));
			display3dStage.getIcons().add(new Image(LessMainApp.class.getResourceAsStream("LESS32_32.png")));
			display3dStage.initOwner(this.mwController.mainApp.getPrimaryStage());
			display3dStage.show();
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
	
	private void removeInvalidItemBeforeClosing(){
		//before close, check all setting is ok
		for(Iterator<Map.Entry<String, ObservableList<String>>> iterator = this.mwController.objectsAndCompomentsMap.entrySet().iterator();iterator.hasNext();){
			Map.Entry<String, ObservableList<String>> entry = iterator.next();
			String objName = entry.getKey();
			ObservableList<String> compList = entry.getValue();
			if(compList.size()==0){
				iterator.remove();
				this.mwController.objectsList.remove(objName);
			}
			for(int i=0;i<compList.size();i++){ //component
				String compName = compList.get(i);
				String opticalKey = objName + "_" + compName;
				if(!this.mwController.opticalcomponentMap.containsKey(opticalKey)){
					iterator.remove();
					this.mwController.objectsList.remove(objName);
				}
			}
		}
	}
	
	
	/**
	 * importFromObjGroups: not used
	 */
	@FXML
	private void importObjs(){
		if(this.objectsLV.getSelectionModel().getSelectedIndex() > -1){
			FileChooser fileChooser = new FileChooser();
			String lastOpened = this.mwController.getLastOpenedPath(Const.LAST_OPNED_CHOOSE_OBJ);
			if (lastOpened != null && new File(lastOpened).exists()){
				fileChooser.setInitialDirectory(new File(lastOpened));
			}
			fileChooser.getExtensionFilters().add(new FileChooser.ExtensionFilter("OBJ Mesh", "*.obj"));
			File file = fileChooser.showOpenDialog(this.parentStage);
	        if(file !=null)
	        {
	        	this.mwController.setLastOpenedPath(Const.LAST_OPNED_CHOOSE_OBJ,file.getParent().toString());
	        	String targetFileName = this.objectsLV.getSelectionModel().getSelectedItem()+"_"+file.getName().replaceAll(" ", "_");
	        	System.out.println(targetFileName);
	        	mwController.objectsAndCompomentsMap.get(this.objectsLV.getSelectionModel().getSelectedItem()).add(targetFileName);
	        	
	        	//copy mtl file if exits
	        	String mtlFileName = FilenameUtils.removeExtension(file.getName())+".mtl";
	        	File mtlSrcFile = Paths.get(file.getParent(),mtlFileName).toFile();
	        	
	        	//copy obj file to parameters folder
	        	//copy this to the folder of paramters
	        	String param_path = this.mwController.projManager.getParameterDirPath();
	        	CopyOption[] options = new CopyOption[]{
	                    StandardCopyOption.REPLACE_EXISTING,
	                    StandardCopyOption.COPY_ATTRIBUTES
	            };
	        	try {
	        		
					Files.copy(file.toPath(), Paths.get(param_path,targetFileName), options);
					if(mtlSrcFile.exists()){
						Files.copy(mtlSrcFile.toPath(), Paths.get(param_path,mtlFileName), options);
					}
				} catch (IOException e) {
					e.printStackTrace();
				}
	        	
	        }
		}
		
	}
	
	/**
	 * import from RAMI def files
	 */
	@FXML
	public void importFromRamiDefFile(){
		if(this.objectsLV.getSelectionModel().getSelectedIndex() >-1){
			FileChooser fileChooser = new FileChooser();
			String lastOpened = this.mwController.getLastOpenedPath(Const.LAST_OPNED_CHOOSE_OBJ);
			if (lastOpened != null && new File(lastOpened).exists()){
				fileChooser.setInitialDirectory(new File(lastOpened));
			}
			fileChooser.getExtensionFilters().add(new FileChooser.ExtensionFilter("RAMI def file", "*.def"));
			File file = fileChooser.showOpenDialog(this.parentStage);
	        if(file !=null)
	        {
	        	this.mwController.setLastOpenedPath(Const.LAST_OPNED_CHOOSE_OBJ,file.getParent().toString());
	        	//convert from def to obj
	        	String targetFileName = this.objectsLV.getSelectionModel().getSelectedItem()+"_"+file.getName().substring(0,file.getName().lastIndexOf('.')).replaceAll(" ", "_")+".obj";
	        	ProcessBuilder pd = new ProcessBuilder(PyLauncher.getPyexe(),
	        			PyLauncher.getUtilityScriptsPath(Const.LESS_UTILITY_SCRIPT_DEF2OBJ),"-i",file.toString(), "-o", targetFileName);
	        	String param_path = this.mwController.projManager.getParameterDirPath();
	        	pd.directory(new File(param_path));
	        	ArrayList<String> compNames = PyLauncher.runUtilityscripts(pd, this.mwController.outputConsole, "componentName");
	        	for(int i=0;i<compNames.size();i++)
	        		mwController.objectsAndCompomentsMap.get(this.objectsLV.getSelectionModel().getSelectedItem()).add(compNames.get(i).trim());	        	
	        }
		}
	}
	
	/**
	 * import from objfile into groups
	 */
	@FXML
	public void importFromObjGroups(){
		if(this.objectsLV.getSelectionModel().getSelectedIndex() > -1){
			FileChooser fileChooser = new FileChooser();
			String lastOpened = this.mwController.getLastOpenedPath(Const.LAST_OPNED_CHOOSE_OBJ);
			if (lastOpened != null && new File(lastOpened).exists()){
				fileChooser.setInitialDirectory(new File(lastOpened));
			}
			fileChooser.getExtensionFilters().add(new FileChooser.ExtensionFilter("OBJ Mesh", "*.obj"));
			File file = fileChooser.showOpenDialog(this.parentStage);
	        if(file !=null)
	        {
	        	this.mwController.setLastOpenedPath(Const.LAST_OPNED_CHOOSE_OBJ,file.getParent().toString());
	        	// show scale window
	        	showScaleDialog();
	        	
	        	//read file
	        	ObjModelImporter objImporter = new ObjModelImporter();
	    		try {
	    		    objImporter.read(file.toString());            
	    		}
	    		catch (ImportException e) {
	    		    // handle exception
	    		}
	    		Map<String, MeshView> importedGroupsMap = objImporter.getNamedMeshViews();
	    		objImporter.close();
	    		String objName = this.objectsLV.getSelectionModel().getSelectedItem();
	    		
	    		
	    		//determine boundingbox
	    		LSBoundingbox subObjBoundingBox = new LSBoundingbox(); //Import obj to an existing obj
	    		for (Map.Entry<String, MeshView> entry : importedGroupsMap.entrySet()) {
	    			TriangleMesh compMesh = (TriangleMesh)entry.getValue().getMesh();
	    			LSBoundingbox lsBoundingbox = new LSBoundingbox();
	    			ObservableFloatArray pointarray =  compMesh.getPoints();
	    			for(int i=0;i<pointarray.size();i += 3){
	    				double x = pointarray.get(i)*fx;
	    				double y = -pointarray.get(i+1)*fy;
	    				double z = -pointarray.get(i+2)*fz;
	    				if(x < lsBoundingbox.minX) lsBoundingbox.minX = x;
	    				if(y < lsBoundingbox.minY) lsBoundingbox.minY = y;
	    				if(z < lsBoundingbox.minZ) lsBoundingbox.minZ = z;
	    				if(x > lsBoundingbox.maxX) lsBoundingbox.maxX = x;
	    				if(y > lsBoundingbox.maxY) lsBoundingbox.maxY = y;
	    				if(z > lsBoundingbox.maxZ) lsBoundingbox.maxZ = z;
	    			}
	    			subObjBoundingBox.addChild(lsBoundingbox);
	    		}

	    		double lower_center_x=0,lower_center_z=0,lower_center_y=0;
	    		if(this.isTranslate2Origin) {
	    			lower_center_x = 0.5*(subObjBoundingBox.minX + subObjBoundingBox.maxX);
		    		lower_center_z = 0.5*(subObjBoundingBox.minZ + subObjBoundingBox.maxZ);
		    		lower_center_y = subObjBoundingBox.minY;
		    		subObjBoundingBox.offset(-lower_center_x, -lower_center_y, -lower_center_z);
	    		}
	    		
	    		if(this.mwController.objectAndBoundingboxMap.containsKey(objName)){
	    			this.mwController.objectAndBoundingboxMap.get(objName).addChild(subObjBoundingBox);
	    		}else{
	    			this.mwController.objectAndBoundingboxMap.put(objName, subObjBoundingBox);
	    		}
	    		
	    		
	    		for (Map.Entry<String, MeshView> entry : importedGroupsMap.entrySet())
	    		{
	    			String readedGroupName = entry.getKey();
	    			//rename the group
	    			if(readedGroupName.equals("Group")) {
	    				TextInputDialog dialog = new TextInputDialog("Group");
	    		        dialog.setTitle("Rename the component");
	    		        dialog.setHeaderText("Group name is not found, please enter a new one (e.g., branch or leaves) or keep default:");
	    		        dialog.setContentText("Component Name:"); 		 
	    		        Optional<String> result = dialog.showAndWait();
	    		        if(result.isPresent()) {
	    		        	readedGroupName = result.get();
	    		        }
	    		    }

	    			String targetFileName = objName+"_"+readedGroupName;
	    			targetFileName = targetFileName.replace(".", "_");
	    			String write_groupName = targetFileName;
	    			targetFileName += ".obj";
	    			
	    			//if exiting, choose another name
	    			if(mwController.objectsAndCompomentsMap.get(objName).contains(targetFileName)) {
	    				targetFileName = targetFileName.substring(0, targetFileName.length()-4)+mwController.objectsAndCompomentsMap.get(objName).size()+".obj";
	    			}
	    			
		        	mwController.objectsAndCompomentsMap.get(objName).add(targetFileName);
		        	String param_path = this.mwController.projManager.getParameterDirPath();
		        	String targetFilePath = Paths.get(param_path, targetFileName).toString();
		        	Filehelper.write_mesh_to_obj(targetFilePath, write_groupName, (TriangleMesh)entry.getValue().getMesh(),fx,fy,fz,
		        			lower_center_x, lower_center_y,lower_center_z);
		        	
		        	//set color according to possible name
		        	if(CommonUitls.contain_branch_names(targetFileName)){
		        		String key = objName+"_"+targetFileName;
						if(mwController.opticalcomponentMap.containsKey(key)){
							mwController.opticalcomponentMap.get(key).setComponentColor(Const.LESS_DEFAULT_BRANCH_COLOR);
						}else{
							mwController.opticalcomponentMap.put(key, new OpticalThermalProperty(Const.LESS_DEFAULT_BRANCH_COLOR));
						}	
		        	}
	    		}
	        }
		}
	}
	
	private void showScaleDialog(){
		try {
			FXMLLoader loader = new FXMLLoader();
			loader.setLocation(ObjectsDefineWindowViewController.class.getResource("ObjTransformView.fxml"));
			BorderPane rootLayout = (BorderPane) loader.load();
			Scene scene = new Scene(rootLayout);
			Stage subStage = new Stage();
			subStage.setScene(scene);
			subStage.setTitle("Multiply/Scale");
			ObjTransformController objController = loader.getController();
			objController.setParentStage(subStage);
			objController.setObjDefController(this);
			subStage.getIcons().add(new Image(LessMainApp.class.getResourceAsStream("LESS16_16.png")));
			subStage.getIcons().add(new Image(LessMainApp.class.getResourceAsStream("LESS32_32.png")));
			subStage.initOwner(this.parentStage);
			subStage.showAndWait();
			
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
	
	
}
