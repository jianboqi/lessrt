package less.gui.view;

import java.io.File;
import java.util.concurrent.CountDownLatch;

import javafx.fxml.FXML;
import javafx.scene.control.Button;
import javafx.scene.control.ComboBox;
import javafx.scene.control.TextField;
import javafx.stage.FileChooser;
import javafx.stage.Stage;
import less.gui.helper.LAICaculatorThread;
import less.gui.helper.PyLauncher;
import less.gui.helper.RunningStatusThread;
import less.gui.helper.SimpleCrownGeneratorRunningStatusThread;
import less.gui.helper.SimpleCrownGeneratorThread;
import less.gui.utils.Const;

public class SimpleCrownGeneratorController {
	@FXML
	public ComboBox<String> combCrownShape;
	@FXML
	public TextField tfCrownHeight;
	@FXML
	public TextField tfCrownDiameterSN;
	@FXML
	public TextField tfCrownDiameterEW;
	@FXML
	public TextField tfTrunkHeight;
	@FXML
	public TextField tfDBH;
	@FXML
	public ComboBox<String> combLeafShape;
	@FXML
	public ComboBox<String> combLAD;
	@FXML
	public TextField tfSingleLeafArea;
	@FXML
	public TextField tfLeafNum;
	@FXML
	public TextField tfPolygonSides;
	@FXML
	public Button btnRun;
	@FXML
	public TextField tfOutObjPath;
	
	private Stage parentStage;
	public LessMainWindowController mwController;
	
	private String outputObjPath = "";
	
	
	public void initView(){
		combCrownShape.getItems().addAll( "Ellipsoid", "Cube","Cylinder", "Cone");
		combCrownShape.getSelectionModel().select(0);
		
		combLAD.getItems().addAll("Spherical", "Uniform", "Planophile", "Plagiophile", "Erectophile", "Extremophile");
		combLAD.getSelectionModel().select(0);
		
		combLeafShape.getItems().addAll("Square", "Disk");
		combLeafShape.getSelectionModel().select(0);
		tfPolygonSides.setDisable(true);
	}
	
	public void setParentStage(Stage parentStage) {
		this.parentStage = parentStage;
	}
	
	public void setmwController(LessMainWindowController mwController){
		this.mwController = mwController;
	}
	
	@FXML
	private void btnOutObj() {
		FileChooser fileChooser = new FileChooser();
		String lastOpened = this.mwController.getLastOpenedPath(Const.LAST_OPNED_OUT_OBJ_FILE_PATH);
		if (lastOpened != null && new File(lastOpened).exists()){
			fileChooser.setInitialDirectory(new File(lastOpened));
		}else{
			if(this.mwController.simulation_path != null)
				fileChooser.setInitialDirectory(new File(this.mwController.simulation_path));
		}
		fileChooser.getExtensionFilters().add(new FileChooser.ExtensionFilter("OBJ File", "*.obj"));
		File file = fileChooser.showSaveDialog(this.parentStage);
        if(file !=null)
        {
        	this.mwController.setLastOpenedPath(Const.LAST_OPNED_OUT_OBJ_FILE_PATH,file.getParent().toString());
        	this.tfOutObjPath.setText(file.toString());
        	outputObjPath = file.toString();
        }
	}
	
	@FXML
	private void btnRun() {
		if(this.outputObjPath.equals("")) {
			this.mwController.outputConsole.log("INFO: OBJ output path is not set.\n");
			return;
		}
		CountDownLatch latch = new CountDownLatch(1);
		SimpleCrownGeneratorThread scThread = new SimpleCrownGeneratorThread();
		scThread.setLessMainController(this.mwController);
		scThread.prepare(this, this.mwController.outputConsole, latch);
		SimpleCrownGeneratorRunningStatusThread scgStatusThread = new SimpleCrownGeneratorRunningStatusThread(scThread, btnRun);
		scgStatusThread.start();
	}
	
	@FXML
	private void LeafShapOnAction() {
		if(combLeafShape.getValue().equals("Square")){
			tfPolygonSides.setDisable(true);
		}else {
			tfPolygonSides.setDisable(false);
		}
	}
	
	
	
}
