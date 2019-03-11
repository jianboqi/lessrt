package less.gui.display3D;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Map;
import java.util.concurrent.CountDownLatch;

import com.sun.jndi.url.iiopname.iiopnameURLContextFactory;

import javafx.application.Platform;
import javafx.beans.value.ChangeListener;
import javafx.beans.value.ObservableValue;
import javafx.collections.ObservableList;
import javafx.event.Event;
import javafx.event.EventHandler;
import javafx.fxml.FXML;
import javafx.geometry.Point3D;
import javafx.scene.AmbientLight;
import javafx.scene.Node;
import javafx.scene.PerspectiveCamera;
import javafx.scene.SceneAntialiasing;
import javafx.scene.SubScene;
import javafx.scene.control.CheckBox;
import javafx.scene.control.ColorPicker;
import javafx.scene.control.RadioButton;
import javafx.scene.control.SplitPane;
import javafx.scene.control.Toggle;
import javafx.scene.control.ToggleGroup;
import javafx.scene.control.Tooltip;
import javafx.scene.input.KeyEvent;
import javafx.scene.input.MouseEvent;
import javafx.scene.input.ScrollEvent;
import javafx.scene.layout.AnchorPane;
import javafx.scene.paint.Color;
import javafx.scene.paint.PhongMaterial;
import javafx.scene.shape.Box;
import javafx.scene.shape.Cylinder;
import javafx.scene.shape.Mesh;
import javafx.scene.shape.MeshView;
import javafx.scene.shape.TriangleMesh;
import javafx.scene.transform.Rotate;
import javafx.stage.Stage;
import javafx.stage.WindowEvent;
import less.gui.helper.PyLauncher;
import less.gui.helper.RunningStatusThread;
import less.gui.model.LSBoundingbox;
import less.gui.model.PositionXY;
import less.gui.utils.Const;
import less.gui.view.LessMainWindowController;

public class Display3DController {
	
	private SubScene displayScene;
	@FXML
	private AnchorPane subscenePane;
	

	@FXML
	private AnchorPane configAnchorPane;
	
	@FXML
	private CheckBox AxisCheck;
	@FXML
	private CheckBox GridCheck;
	@FXML
	private CheckBox SunRayCheck;
	@FXML
	private CheckBox CameraVolCheck;
	@FXML
	private CheckBox ShowObjectCheck;
	@FXML
	private ColorPicker backgroundColorPicker;
	@FXML
	private ColorPicker cameraVolColorPicker;
	private PhongMaterial volMtl;//
	
	@FXML
	private RadioButton FullDetailRadioBtn;
	@FXML
	private RadioButton BoundingBoxRadioBtn;
	
	private LessMainWindowController mwController;
	private Stage parentStage;
	private Boolean isSimplified;
	
    final Xform world = new Xform();
    final PerspectiveCamera camera = new PerspectiveCamera(true);
    final Xform cameraXform = new Xform();
    final Xform cameraXform2 = new Xform();
    final Xform cameraXform3 = new Xform();
    private static final double CAMERA_INITIAL_DISTANCE = -300;
    private static final double CAMERA_INITIAL_X_ANGLE = 70.0;
    private static final double CAMERA_INITIAL_Y_ANGLE = 320.0;
    private static final double CAMERA_NEAR_CLIP = 0.01;
    private static final double CAMERA_FAR_CLIP = 10000.0;
    
    private  double AXIS_LENGTH = 15.0;
    
    final Xform axisGroup = new Xform();
    private Xform gridGroup;
    public Xform sunray;
    public Xform cameraVolume;
    
    public ArrayList<Xform> instanceList;
    private ToggleGroup tg;
    
    //view control
    private static final double CONTROL_MULTIPLIER = 2;    
    private static final double SHIFT_MULTIPLIER = 10.0;    
    private static final double MOUSE_SPEED = 0.01;    
    private static final double ROTATION_SPEED = 2.0;    
    private static final double TRACK_SPEED = 0.3;
    
    double mousePosX;
    double mousePosY;
    double mouseOldX;
    double mouseOldY;
    double mouseDeltaX;
    double mouseDeltaY;
    
	
	public void setParentController(LessMainWindowController mwController){
		this.mwController = mwController;
	}
	
	public void setParentStage(Stage parentStage){
		this.parentStage = parentStage;
	}
	
	public void setSimplified(Boolean isSimplified){
		this.isSimplified = isSimplified;
	}
	
	public void initDisplay3D(){
		displayScene = new SubScene(world, 100, 100, true, SceneAntialiasing.BALANCED);
		subscenePane.getChildren().add(displayScene);
		displayScene.heightProperty().bind(subscenePane.heightProperty());
		displayScene.widthProperty().bind(subscenePane.widthProperty());
		AnchorPane.setLeftAnchor(displayScene, 0.0);
		AnchorPane.setRightAnchor(displayScene, 0.0);
		AnchorPane.setBottomAnchor(displayScene, 0.0);
		AnchorPane.setTopAnchor(displayScene, 0.0);
		SplitPane.setResizableWithParent(configAnchorPane, false);
		
		//displayScene.setManaged(false);
	    displayScene.setFill(Color.rgb(10, 10, 40));
	    backgroundColorPicker.setValue(Color.rgb(10, 10, 40));
	    
	    //camera
	    cameraVolColorPicker.setValue(Color.web("1212ee50"));
	    cameraVolColorPicker.setDisable(true);
	    final PhongMaterial colortrans = new PhongMaterial();
		colortrans.setDiffuseColor(Color.web("1212ee50"));
		colortrans.setSpecularColor(Color.web("1212ee50"));
		colortrans.setSpecularPower(Double.POSITIVE_INFINITY);
		volMtl = colortrans;
		
		initRadioButtons();
	    
	    buildCamera();
	   // buildLighting();
	    displayScene.setCamera(camera);
	    buildGrid();
	    buildAxes();
	    
	    handleKeyboard(displayScene, world);
        handleMouse(displayScene, world);
		
        Thread t = new Thread(new Runnable() {
        	public void run () {
        		 drawTerrain();
        		 drawObjectsAndInstances();
        		 drawLightRay();
        		 drawCamerafrustum();
        		 System.out.println("INFO: Finished.");
        	}
        });

        t.start();
		event_handle();
	}
	
	private void initRadioButtons() {
		tg = new ToggleGroup();
		FullDetailRadioBtn.setToggleGroup(tg);
		FullDetailRadioBtn.setSelected(!isSimplified);
		FullDetailRadioBtn.setUserData("F");
		BoundingBoxRadioBtn.setToggleGroup(tg);
		BoundingBoxRadioBtn.setSelected(isSimplified);
		BoundingBoxRadioBtn.setUserData("B");
		tg.selectedToggleProperty().addListener(new ChangeListener<Toggle>() {
		      public void changed(ObservableValue<? extends Toggle> ov,
		          Toggle old_toggle, Toggle new_toggle) {
		        if (tg.getSelectedToggle() != null) {
		          if(tg.getSelectedToggle().getUserData().toString().equals("F")) {
		        	  isSimplified = false;
		          }else {
		        	  isSimplified = true;
		          }
		          Thread t = new Thread(new Runnable() {
		          	public void run () {
		          		 drawObjectsAndInstances();
		          	}
		          });
		          t.start();
		        }
		      }
		    });
	}
	
	private void buildCamera() {
		//camera.setFieldOfView(value);
		world.getChildren().add(cameraXform);
        cameraXform.getChildren().add(cameraXform2);
        cameraXform2.getChildren().add(cameraXform3);
        cameraXform3.getChildren().add(camera);
        cameraXform3.setRotateZ(180.0);
 
        camera.setNearClip(CAMERA_NEAR_CLIP);
        camera.setFarClip(CAMERA_FAR_CLIP);
        camera.setTranslateZ(CAMERA_INITIAL_DISTANCE);
        cameraXform.ry.setAngle(CAMERA_INITIAL_Y_ANGLE);
        cameraXform.rx.setAngle(CAMERA_INITIAL_X_ANGLE);
    }
	
	private void buildLighting(){
		AmbientLight al = new AmbientLight();
		world.getChildren().add(al);
	}
	
	public void buildAxes(){		
		final PhongMaterial redMaterial = new PhongMaterial();
        redMaterial.setDiffuseColor(Color.RED);
        redMaterial.setSpecularColor(Color.RED);
        redMaterial.setSpecularPower(Double.POSITIVE_INFINITY);
 
        final PhongMaterial greenMaterial = new PhongMaterial();
        greenMaterial.setDiffuseColor(Color.GREEN);
        greenMaterial.setSpecularColor(Color.GREEN);
        greenMaterial.setSpecularPower(Double.POSITIVE_INFINITY);
 
        final PhongMaterial blueMaterial = new PhongMaterial();
        blueMaterial.setDiffuseColor(Color.BLUE);
        blueMaterial.setSpecularColor(Color.BLUE);
        blueMaterial.setSpecularPower(Double.POSITIVE_INFINITY);
        double axisRadius = 0.6;
        final Box xAxis = new Box(AXIS_LENGTH, axisRadius, axisRadius);
        final Box yAxis = new Box(axisRadius, AXIS_LENGTH, axisRadius);
        final Box zAxis = new Box(axisRadius, axisRadius, AXIS_LENGTH);
        
        xAxis.setMaterial(redMaterial);
        yAxis.setMaterial(greenMaterial);
        zAxis.setMaterial(blueMaterial);
        
        TriangleMesh mesh = new TriangleMesh();
        
        double arrowAxis = axisRadius*3;
        double points[] = {AXIS_LENGTH*0.5, 0.5*arrowAxis, 0.5*arrowAxis,
        				   AXIS_LENGTH*0.5, -0.5*arrowAxis, 0.5*arrowAxis,
        				   AXIS_LENGTH*0.5, -0.5*arrowAxis, -0.5*arrowAxis,
        				   AXIS_LENGTH*0.5, 0.5*arrowAxis, -0.5*arrowAxis,
        				   AXIS_LENGTH*0.5+arrowAxis*1.5, 0, 0};
        mesh.getPoints().addAll(DrawElement.toFloatArray(points));
        int faces[] = {0,0,1,0,4,0,
        			   1,0,2,0,4,0,
        			   2,0,3,0,4,0,
        			   3,0,0,0,4,0,
        			   0,0,3,0,1,0,
        			   3,0,2,0,1,0
        			   };
        mesh.getFaces().addAll(faces);
        mesh.getTexCoords().addAll(0,0);
        MeshView meshViewx = new MeshView(mesh);
        meshViewx.setMaterial(redMaterial);
        
        MeshView meshViewy = new MeshView(mesh);
        meshViewy.setMaterial(greenMaterial);
        meshViewy.setRotate(90);
        meshViewy.setTranslateY(AXIS_LENGTH*0.5);
        meshViewy.setTranslateX(-AXIS_LENGTH*0.5-arrowAxis*0.75);
        
        MeshView meshViewz = new MeshView(mesh);
        meshViewz.setMaterial(blueMaterial);
        meshViewz.setRotationAxis(Rotate.Y_AXIS);
        meshViewz.setRotate(-90);
        meshViewz.setTranslateZ(AXIS_LENGTH*0.5);
        meshViewz.setTranslateX(-AXIS_LENGTH*0.5-arrowAxis*0.75);
        
        Tooltip labelX = new Tooltip();
		labelX.setText("X");
		Tooltip labelY= new Tooltip();
		labelY.setText("Y");
		Tooltip labelZ = new Tooltip();
		labelZ.setText("Z");
        Tooltip.install(meshViewx, labelX);
        Tooltip.install(xAxis, labelX);
        Tooltip.install(meshViewy, labelY);
        Tooltip.install(yAxis, labelY);
        Tooltip.install(meshViewz, labelZ);
        Tooltip.install(yAxis, labelZ);
        
        axisGroup.getChildren().addAll(xAxis, yAxis, zAxis);
        axisGroup.getChildren().addAll(meshViewx,meshViewy,meshViewz);
        axisGroup.setVisible(true);
        world.getChildren().addAll(axisGroup);
	}
	
	private void buildGrid(){
		double width = Double.parseDouble(this.mwController.sceneXSizeField.getText().replaceAll(",", ""));
		double height = Double.parseDouble(this.mwController.sceneYSizeField.getText().replaceAll(",", ""));
		
		AXIS_LENGTH = Math.max(width, height)*1.2;
		
		gridGroup = DrawElement.drawXYGrid(width, height, 20);
		gridGroup.setVisible(true);
		world.getChildren().add(gridGroup);
	}
	
	
	@FXML
	private void onShowAxes(){
		if(AxisCheck.isSelected()){
			//show
			axisGroup.setVisible(true);
		}
		else{
			//hide
			axisGroup.setVisible(false);
		}
	}
	
	@FXML
	private void onShowGrid(){
		if(GridCheck.isSelected()){
			//show
			gridGroup.setVisible(true);
		}
		else{
			//hide
			gridGroup.setVisible(false);
		}
	}
	
	@FXML
	private void onShowSunRay(){
		if(SunRayCheck.isSelected()){
			//show
			sunray.setVisible(true);
		}
		else{
			//hide
			sunray.setVisible(false);
		}
	}
	@FXML
	private void onShowCameraVolume(){
		if(CameraVolCheck.isSelected()){
			//show
			cameraVolume.setVisible(true);
			cameraVolColorPicker.setDisable(false);
		}
		else{
			//hide
			cameraVolume.setVisible(false);
			cameraVolColorPicker.setDisable(true);
		}
	}
	
	@FXML
	private void onShowObjects() {
		if(ShowObjectCheck.isSelected()) {
			if(instanceList != null) {
				for(int i=0;i<instanceList.size();i++) {
					Xform xform = instanceList.get(i);
					xform.setVisible(true);
				}
			}
		}else {
			if(instanceList != null) {
				for(int i=0;i<instanceList.size();i++) {
					Xform xform = instanceList.get(i);
					xform.setVisible(false);
				}
			}
		}
	}
	

	private void handleMouse(SubScene scene, final Node root) {
		 
      scene.setOnMousePressed(new EventHandler<MouseEvent>() {
          @Override public void handle(MouseEvent me) {
              mousePosX = me.getSceneX();
              mousePosY = me.getSceneY();
              mouseOldX = me.getSceneX();
              mouseOldY = me.getSceneY();
          }
      });
      
      scene.setOnScroll(
          new EventHandler<ScrollEvent>() {
            @Override
            public void handle(ScrollEvent event) {
              double zoomFactor = 150.05;
              double deltaY = event.getDeltaY();
              if (deltaY < 0){
                zoomFactor = zoomFactor-300.0;
              }
              double modifierFactor = 1;
              double z = camera.getTranslateZ();
              if (event.isControlDown()) {
            	  modifierFactor = 5;
              } 
              double newZ = z + modifierFactor*MOUSE_SPEED*zoomFactor;
              camera.setTranslateZ(newZ);
              event.consume();
            }
      });
      
      scene.setOnMouseDragged(new EventHandler<MouseEvent>() {
          @Override public void handle(MouseEvent me) {
              mouseOldX = mousePosX;
              mouseOldY = mousePosY;
              mousePosX = me.getSceneX();
              mousePosY = me.getSceneY();
              mouseDeltaX = (mousePosX - mouseOldX); 
              mouseDeltaY = (mousePosY - mouseOldY);
              
             double modifierFactor = 0.1;
             double modifier = 4.0;

             if (me.isControlDown()) {
                  modifier = CONTROL_MULTIPLIER;
              } 
              if (me.isShiftDown()) {
                  modifier = SHIFT_MULTIPLIER;
              }     
              if (me.isPrimaryButtonDown()) {
                  cameraXform.ry.setAngle(cameraXform.ry.getAngle() -
                     mouseDeltaX*modifierFactor*modifier*ROTATION_SPEED);  // 
                 cameraXform.rx.setAngle(cameraXform.rx.getAngle() +
                     mouseDeltaY*modifierFactor*modifier*ROTATION_SPEED);  // -
              }
              else if (me.isMiddleButtonDown()) {
                  double z = camera.getTranslateZ();
                  double newZ = z + mouseDeltaX*MOUSE_SPEED*modifier;
                  camera.setTranslateZ(newZ);
              }
              else if (me.isSecondaryButtonDown()) {
                 cameraXform2.t.setX(cameraXform2.t.getX() + 
                    mouseDeltaX*MOUSE_SPEED*modifier*TRACK_SPEED);  // -
                 cameraXform2.t.setY(cameraXform2.t.getY() + 
                    mouseDeltaY*MOUSE_SPEED*modifier*TRACK_SPEED);  // -
              }
         }
     }); // setOnMouseDragged
 } //handleMouse
	private void handleKeyboard(SubScene scene, final Node root) {

      scene.setOnKeyPressed(new EventHandler<KeyEvent>() {
          @Override
          public void handle(KeyEvent event) {
             switch (event.getCode()) {
                 case Z:
                     cameraXform2.t.setX(0.0);
                     cameraXform2.t.setY(0.0);
                     cameraXform.ry.setAngle(CAMERA_INITIAL_Y_ANGLE);
                     cameraXform.rx.setAngle(CAMERA_INITIAL_X_ANGLE);
                     break;
                 case X:
                      axisGroup.setVisible(!axisGroup.isVisible());
                      break;
                  case V:
                  //   moleculeGroup.setVisible(!moleculeGroup.isVisible());
                     break;
             } // switch
          } // handle()
      });  // setOnKeyPressed
  }  //  handleKeyboard()
	
	
	
	public void event_handle(){	
		this.parentStage.setOnCloseRequest(new EventHandler<WindowEvent>() {
		      public void handle(WindowEvent we) {
		    	  mwController.drawtoolBarHelper.display3dController = null;
		      }
		  });
		
		this.backgroundColorPicker.setOnAction(new EventHandler() {
		     public void handle(Event t) {
		         Color c = backgroundColorPicker.getValue();
		         displayScene.setFill(c);
		     }
		 });
		
		this.cameraVolColorPicker.setOnAction(new EventHandler() {
		     public void handle(Event t) {
		         Color c = cameraVolColorPicker.getValue();
		         final PhongMaterial colortrans = new PhongMaterial();
		 		 colortrans.setDiffuseColor(c);
		 		 colortrans.setSpecularColor(c);
		 		 colortrans.setSpecularPower(Double.POSITIVE_INFINITY);
		 		volMtl = colortrans;
		 		drawCamerafrustum();
		     }
		 });
	}
	
	/**
	 */
	public void drawTerrain(){
		double width = Double.parseDouble(this.mwController.sceneXSizeField.getText().replaceAll(",", ""));
		double height = Double.parseDouble(this.mwController.sceneYSizeField.getText().replaceAll(",", ""));
		if(this.mwController.comboBoxDEMType.getSelectionModel().getSelectedItem().equals(Const.LESS_TERRAIN_PLANE)){
			Box plane = DrawElement.drawPlane(width, height);
			world.getChildren().add(plane);
		}
		if(this.mwController.comboBoxDEMType.getSelectionModel().getSelectedItem().equals(Const.LESS_TERRAIN_RASTER)){
			System.out.println("INFO: Converting terrain image to obj...");
			String targetFileName = Paths.get(this.mwController.projManager.getParameterDirPath(),"terrain.obj").toString();
			String inputFileName = Paths.get(this.mwController.projManager.getParameterDirPath(), this.mwController.terrFileField.getText()).toString();
        	ProcessBuilder pd = new ProcessBuilder(PyLauncher.getPyexe(),
        			PyLauncher.getUtilityScriptsPath(Const.LESS_UTILITY_SCRIPT_RASTER2OBJ),"-i",inputFileName, "-o", targetFileName,"-X",width+"","-Z",height+"");
        	String param_path = this.mwController.projManager.getParameterDirPath();
        	pd.directory(new File(param_path));
        	
//        	List<String> cmdstrs = pd.command();
//    		for(int i=0;i<cmdstrs.size();i++){
//    			this.mwController.outputConsole.appendText(cmdstrs.get(i)+" ");
//    		}
//    		this.mwController.outputConsole.appendText("\n");
        	
        	PyLauncher.runUtilityscripts(pd, this.mwController.outputConsole, "");
        	Xform terrain = DrawElement.drawObj(targetFileName);
        	Platform.runLater(() -> world.getChildren().add(terrain));
        	
		}
	}
	
	public void drawObjectsAndInstances(){
		//clear before
		if(instanceList != null) {
			for(int i=0;i<instanceList.size();i++) {
				Xform xform = instanceList.get(i);
				Platform.runLater(() ->world.getChildren().remove(xform));
			}
		}
		
		double width = Double.parseDouble(this.mwController.sceneXSizeField.getText().replaceAll(",", ""));
		double height = Double.parseDouble(this.mwController.sceneYSizeField.getText().replaceAll(",", ""));
		
		boolean isTerrainRaster = this.mwController.comboBoxDEMType.getSelectionModel().getSelectedItem().equals(Const.LESS_TERRAIN_RASTER);
		
		ArrayList<Double> altitudeList = new ArrayList<Double>();
		if(isTerrainRaster){
			System.out.println("INFO: Quering object altitude...");
			this.mwController.before_run();
			CountDownLatch latch = new CountDownLatch(1);
			this.mwController.currentPyLaucherThread = new PyLauncher();
			this.mwController.currentPyLaucherThread.prepare(this.mwController.simulation_path, PyLauncher.Operation.GENERATE_TREEHEIGHT_FOR_3DVIWER, latch, this.mwController.outputConsole);
			this.mwController.currentRunningStatusThread = new RunningStatusThread(this.mwController.currentPyLaucherThread, this.mwController.outputConsole, this.mwController.runBtn);
			this.mwController.currentRunningStatusThread.setMainController(this.mwController);
			this.mwController.currentRunningStatusThread.start();
			try {
				latch.await();
			} catch (InterruptedException e1) {
				// TODO Auto-generated catch block
				e1.printStackTrace();
			}
			
			String param_path = this.mwController.projManager.getParameterDirPath();
			File objectsfile = Paths.get(param_path, Const.LESS_OBJECTS_ALTITUDE_3D).toFile();
			if(objectsfile.exists()){
				try (BufferedReader reader = new BufferedReader(new FileReader(objectsfile))) {
			        String line;
			        int objnum = 0;
			        while ((line = reader.readLine()) != null){
			        	String [] arr = line.trim().split(" ");
			        	double y = Double.parseDouble(arr[2]);
			        	altitudeList.add(y);
			        }  
			    } catch (IOException e) {
			    }
			}
		}
		instanceList = new ArrayList<Xform>();
		Boolean ballAsObjects = this.isSimplified; //simplified objects
		final PhongMaterial darkGreen = new PhongMaterial();
		darkGreen.setDiffuseColor(Color.DARKGREEN);
		darkGreen.setSpecularColor(Color.DARKGREEN);
		darkGreen.setSpecularPower(Double.POSITIVE_INFINITY);
		int index = 0;
		System.out.println("INFO: Displaying objects...");
		
		//hide selected objects
		ObservableList<String> tobeHide = null;
		if(this.mwController.HideSelectedCheck.isSelected()){
			tobeHide = this.mwController.objectLV.getSelectionModel().getSelectedItems();
		}
		
		for(Map.Entry<String, ObservableList<PositionXY>> entry: this.mwController.objectAndPositionMap.entrySet()){
			String objName = entry.getKey();
			
			if(tobeHide!=null && tobeHide.contains(objName)){
				continue;
			}
			ArrayList<Mesh> objMeshes = null;
			ArrayList<Color> compColorList = null;//
			if (!ballAsObjects){
				ObservableList<String> componentList = this.mwController.objectsAndCompomentsMap.get(objName);
				objMeshes = DrawElement.getMeshlistFromObjList(componentList, this.mwController.projManager.getParameterDirPath());
				compColorList = new ArrayList<Color>();
				for(int i=0;i<componentList.size();i++){
					compColorList.add(this.mwController.opticalcomponentMap.get(objName+"_"+componentList.get(i)).getComponentColor());
				}
			}
			LSBoundingbox lsBoundingbox = this.mwController.objectAndBoundingboxMap.get(objName);
			ObservableList<PositionXY> positionXYs = entry.getValue();
			for(int i=0;i<positionXYs.size();i++){ //positions
				PositionXY posxy = positionXYs.get(i);
				Double pos_x = Double.parseDouble(posxy.getPos_x());
				Double pos_y = Double.parseDouble(posxy.getPos_y());
				Double pos_z = Double.parseDouble(posxy.getPos_z());
				if (!ballAsObjects){ //not boundingbox
					Xform instanceForm = DrawElement.ConvertMeshList2xform(objMeshes,compColorList);
					instanceForm.setTranslateX(width*0.5-pos_x);
					instanceForm.setTranslateZ(height*0.5 - pos_y);
					if(isTerrainRaster)
						instanceForm.setTranslateY(altitudeList.get(index)+pos_z);
					else
						instanceForm.setTranslateY(pos_z);
					instanceList.add(instanceForm);
					Platform.runLater(() ->world.getChildren().add(instanceForm));
				}else
				{//boundingbox 
					Box box = new Box(lsBoundingbox.maxX-lsBoundingbox.minX, lsBoundingbox.maxY-lsBoundingbox.minY,
							lsBoundingbox.maxZ-lsBoundingbox.minZ);
					box.setTranslateX(width*0.5-pos_x);
					box.setTranslateZ(height*0.5 - pos_y);
					box.setMaterial(darkGreen);
					if(isTerrainRaster)
						box.setTranslateY(altitudeList.get(index)+box.getHeight()+pos_z);
					else
						box.setTranslateY(box.getHeight()*0.5+pos_z);
					Xform objXform = new Xform();
					objXform.getChildren().add(box);
					instanceList.add(objXform);
					Platform.runLater(() ->world.getChildren().add(objXform));
				}
				
				index++;
			}
		}
	}

	/**
	 * 
	 */
	public void drawLightRay(){
		
		if(world.getChildren().contains(sunray)){
			world.getChildren().remove(sunray);
		}
		
		final PhongMaterial yellow = new PhongMaterial();
		yellow.setDiffuseColor(Color.YELLOW);
		yellow.setSpecularColor(Color.YELLOW);
		yellow.setSpecularPower(Double.POSITIVE_INFINITY);
		double sun_zenith = Double.parseDouble(this.mwController.sunZenithField.getText().replaceAll(",", ""));
		double sun_azimuth = Double.parseDouble(this.mwController.sunAzimuthField.getText().replaceAll(",", ""));
		double phi = -(sun_azimuth - 90) / 180.0 * Math.PI;
		double theta = sun_zenith/180.0*Math.PI;
		double R = 500;
		double x = -R*Math.sin(theta)*Math.cos(phi);
		double z = R*Math.sin(theta)*Math.sin(phi);
		double y = R*Math.cos(theta);
		Cylinder suncylinder = DrawElement.drawLine(new Point3D(x, y, z), new Point3D(0, 0, 0));
		suncylinder.setMaterial(yellow);
		sunray = new Xform();
		sunray.getChildren().add(suncylinder);
		if(!SunRayCheck.isSelected()){
			sunray.setVisible(false);
		}
		Platform.runLater(() -> world.getChildren().add(sunray));
	}
	
	/**
	 */
	public void drawCamerafrustum(){
				
		if(world.getChildren().contains(cameraVolume)){
			world.getChildren().remove(cameraVolume);
		}
		
		//
		if(this.mwController.comboBoxSensorType.getSelectionModel().getSelectedItem().equals(Const.LESS_SENSOR_TYPE_ORTH)){
			double view_zenith_angle = Double.parseDouble(this.mwController.obsZenithField.getText().replaceAll(",", ""));
			double view_azimuth_angle = Double.parseDouble(this.mwController.obsAzimuthField.getText().replaceAll(",", ""));
			double sub_region_w = Double.parseDouble(this.mwController.sensorXExtentField.getText().replaceAll(",", ""));
			double sub_region_h = Double.parseDouble(this.mwController.sensorYExtentField.getText().replaceAll(",", ""));
			cameraVolume = DrawElement.drawOrthographicFrustum(AXIS_LENGTH, view_zenith_angle, view_azimuth_angle, sub_region_w, sub_region_h,volMtl);
			if(!CameraVolCheck.isSelected()){
				cameraVolume.setVisible(false);
			}
			Platform.runLater(() -> world.getChildren().add(cameraVolume));
			
		}
		
		if(this.mwController.comboBoxSensorType.getSelectionModel().getSelectedItem().equals(Const.LESS_SENSOR_TYPE_PER)){
			String o_x_str = this.mwController.pers_o_x_field.getText().replaceAll(",", "");
			String o_y_str = this.mwController.pers_o_y_field.getText().replaceAll(",", "");
			String o_z_str = this.mwController.pers_o_z_field.getText().replaceAll(",", "");
			String t_x_str = this.mwController.pers_t_x_field.getText().replaceAll(",", "");
			String t_y_str = this.mwController.pers_t_y_field.getText().replaceAll(",", "");
			String t_z_str = this.mwController.pers_t_z_field.getText().replaceAll(",", "");
			
			String fov_x_str = this.mwController.xfovField.getText().replaceAll(",", "");
			String fov_y_str = this.mwController.yfovField.getText().replaceAll(",", "");
			
			if(o_x_str.equals("") || o_y_str.equals("") || o_z_str.equals("")||
			   t_x_str.equals("") || t_y_str.equals("") || t_z_str.equals("")||
			   fov_x_str.equals("") || fov_y_str.equals(""))
				return;
			
			double o_x = Double.parseDouble(o_x_str);
			double o_y = Double.parseDouble(o_y_str);
			double o_z = Double.parseDouble(o_z_str);
			double t_x = Double.parseDouble(t_x_str);
			double t_y = Double.parseDouble(t_y_str);
			double t_z = Double.parseDouble(t_z_str);
			
			double fovx = Double.parseDouble(fov_x_str);
			double fovy = Double.parseDouble(fov_y_str);
			
			cameraVolume = DrawElement.drawPerspectiveFrustum(new Point3D(o_x, o_y,o_z), new Point3D(t_x, t_y, t_z),fovx,fovy,volMtl);
			if(!CameraVolCheck.isSelected()){
				cameraVolume.setVisible(false);
			}
			Platform.runLater(() -> world.getChildren().add(cameraVolume));
		}
		
		
	}
	
}
