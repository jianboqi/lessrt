package less.gui.display3D;

import java.util.ArrayList;

import org.apache.commons.lang3.ObjectUtils.Null;

import javafx.application.Platform;
import javafx.collections.ObservableList;
import javafx.event.Event;
import javafx.event.EventHandler;
import javafx.fxml.FXML;
import javafx.scene.Node;
import javafx.scene.PerspectiveCamera;
import javafx.scene.SceneAntialiasing;
import javafx.scene.SubScene;
import javafx.scene.control.CheckBox;
import javafx.scene.control.ColorPicker;
import javafx.scene.control.SplitPane;
import javafx.scene.control.Tooltip;
import javafx.scene.input.KeyEvent;
import javafx.scene.input.MouseEvent;
import javafx.scene.input.ScrollEvent;
import javafx.scene.layout.AnchorPane;
import javafx.scene.layout.VBox;
import javafx.scene.paint.Color;
import javafx.scene.paint.PhongMaterial;
import javafx.scene.shape.Box;
import javafx.scene.shape.Mesh;
import javafx.scene.shape.MeshView;
import javafx.scene.shape.TriangleMesh;
import javafx.scene.transform.Rotate;
import javafx.stage.Stage;
import javafx.stage.WindowEvent;
import less.gui.model.LSBoundingbox;
import less.gui.view.LessMainWindowController;
import less.gui.view.ObjectsDefineWindowViewController;

public class DisplaySingleObject3DController {
	@FXML
	private VBox componentVbox;
	@FXML
	private AnchorPane subScenePane;
	@FXML
	private AnchorPane configAnchorPane;
	@FXML
	private ColorPicker backgroundColorPicker;
	@FXML
	private CheckBox AxisCheck;
	
	
	private SubScene displayScene;
	private ObjectsDefineWindowViewController objectDefineController;
	private Stage parentStage;
	
	final Xform world = new Xform();
    final PerspectiveCamera camera = new PerspectiveCamera(true);
    final Xform cameraXform = new Xform();
    final Xform cameraXform2 = new Xform();
    final Xform cameraXform3 = new Xform();
    private static final double CAMERA_INITIAL_DISTANCE = -50;
    private static final double CAMERA_INITIAL_X_ANGLE = 70.0;
    private static final double CAMERA_INITIAL_Y_ANGLE = 320.0;
    private static final double CAMERA_NEAR_CLIP = 0.1;
    private static final double CAMERA_FAR_CLIP = 10000.0;
    
    private  double AXIS_LENGTH = 15.0;
    
    final Xform axisGroup = new Xform();
    
    //view control
    private static final double CONTROL_MULTIPLIER = 2;    
    private static final double SHIFT_MULTIPLIER = 10.0;    
    private static final double MOUSE_SPEED = 0.1;    
    private static final double ROTATION_SPEED = 2.0;    
    private static final double TRACK_SPEED = 0.3;
    
    double mousePosX;
    double mousePosY;
    double mouseOldX;
    double mouseOldY;
    double mouseDeltaX;
    double mouseDeltaY;
    
    String choosedObjName = null;
    Xform instanceForm=null;// currently displayed meshes
	
	public void setParentController(ObjectsDefineWindowViewController objectDefineController){
		this.objectDefineController = objectDefineController;
	}
	public void setParentStage(Stage parentStage){
		this.parentStage = parentStage;
	}
	public void initDisplay3D(){
		displayScene = new SubScene(world, 100, 100, true, SceneAntialiasing.BALANCED);
		subScenePane.getChildren().add(displayScene);
		displayScene.heightProperty().bind(subScenePane.heightProperty());
		displayScene.widthProperty().bind(subScenePane.widthProperty());
		AnchorPane.setLeftAnchor(displayScene, 0.0);
		AnchorPane.setRightAnchor(displayScene, 0.0);
		AnchorPane.setBottomAnchor(displayScene, 0.0);
		AnchorPane.setTopAnchor(displayScene, 0.0);
		SplitPane.setResizableWithParent(configAnchorPane, false);
		
		//displayScene.setManaged(false);
	    displayScene.setFill(Color.rgb(255, 255, 255));
	    backgroundColorPicker.setValue(Color.rgb(10, 10, 40));
	    
	    buildCamera();
		displayScene.setCamera(camera);
		handleKeyboard(displayScene, world);
        handleMouse(displayScene, world);
        
        event_handle();
        
        displaySelectedObject();
        buildAxes();
	}
	
	private void buildCamera() {
		choosedObjName = this.objectDefineController.objectsLV.getSelectionModel().getSelectedItem();
		if(choosedObjName == null){
			System.out.println("Please choose a object to display.");
			return;
		}
		
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
        double axisRadius = 0.2;
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
        axisGroup.setVisible(false);
        world.getChildren().addAll(axisGroup);
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
		
		public void event_handle(){	
			this.parentStage.setOnCloseRequest(new EventHandler<WindowEvent>() {
			      public void handle(WindowEvent we) {
			    	  objectDefineController.displaySingleObject3DController = null;
			      }
			  });
			
			this.backgroundColorPicker.setOnAction(new EventHandler() {
			     public void handle(Event t) {
			         Color c = backgroundColorPicker.getValue();
			         displayScene.setFill(c);
			     }
			 });
		}
	
	private void displaySelectedObject(){
		//get selected obj name
		if(choosedObjName != null){
			ObservableList<String> componentList = this.objectDefineController.mwController.objectsAndCompomentsMap.get(choosedObjName);
			ArrayList<Mesh> objMeshes = DrawElement.getMeshlistFromObjList(componentList, this.objectDefineController.mwController.projManager.getParameterDirPath());
			ArrayList<Color> compColorList = new ArrayList<Color>();
			for(int i=0;i<componentList.size();i++){
				compColorList.add(this.objectDefineController.mwController.opticalcomponentMap.get(choosedObjName+"_"+componentList.get(i)).getComponentColor());
			}
			LSBoundingbox lsBoundingbox = this.objectDefineController.mwController.objectAndBoundingboxMap.get(choosedObjName);
			AXIS_LENGTH = lsBoundingbox.getMaxOfAllAxes()*2.2;
			instanceForm = DrawElement.ConvertMeshList2xform(objMeshes,compColorList);
			instanceForm.setTranslateX(0);
			instanceForm.setTranslateZ(0);
				instanceForm.setTranslateY(0);
			Platform.runLater(() ->world.getChildren().add(instanceForm));
			}			
		}
	
	public void changeMeshColor(){
		ObservableList<String> componentList = this.objectDefineController.mwController.objectsAndCompomentsMap.get(choosedObjName);
		ArrayList<Mesh> objMeshes = DrawElement.getMeshlistFromObjList(componentList, this.objectDefineController.mwController.projManager.getParameterDirPath());
		ArrayList<Color> compColorList = new ArrayList<Color>();
		for(int i=0;i<componentList.size();i++){
			compColorList.add(this.objectDefineController.mwController.opticalcomponentMap.get(choosedObjName+"_"+componentList.get(i)).getComponentColor());
		}
		
		for(int i=0;i<instanceForm.getChildren().size();i++){
			MeshView child_mesh = (MeshView)instanceForm.getChildren().get(i);
			final PhongMaterial material = new PhongMaterial();
			material.setDiffuseColor(compColorList.get(i));
			material.setSpecularColor(compColorList.get(i));
			material.setSpecularPower(Double.POSITIVE_INFINITY);
			child_mesh.setMaterial(material);
		}
	}
		
}
