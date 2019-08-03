package less.gui.lidar.view;

import java.io.BufferedWriter;
import java.io.File;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.concurrent.CountDownLatch;

import org.apache.commons.io.FileUtils;
import org.json.JSONObject;

import javafx.fxml.FXML;
import javafx.scene.control.MenuItem;
import javafx.scene.control.TabPane;
import javafx.scene.layout.VBox;
import javafx.stage.FileChooser;
import less.gui.helper.PyLauncher;
import less.gui.helper.RunningStatusThread;
import less.gui.lidar.LiDARMainApp;
import less.gui.utils.Const;

public class RootLayoutController {
	@FXML
	public VBox generalParameterVBox;
	@FXML
	public TabPane platformTabPane;
	
	@FXML
	public MenuItem singleLineMenuItem;
	@FXML
	public MenuItem multiLinesPointCloudMenuItem;
	
	
	private LiDARMainApp mainApp;
	
	public void setMainApp(LiDARMainApp mainApp) {
		this.mainApp = mainApp;
	}
	
	@FXML
	private void handleSave() {
		JSONObject json = new JSONObject();
		String platform = platformTabPane.getSelectionModel().getSelectedItem().getText();
		
		JSONObject platformJson = new JSONObject();
		switch (platform) {
		case "Mono Pulse":
			platformJson = mainApp.monoPulseParameterModel.getJson();
			platformJson.put("type", platform);
			break;
		case "ALS":
			platformJson = mainApp.alsParameterModel.getJson();
			platformJson.put("type", platform);
			break;
		case "TLS":
			platformJson = mainApp.tlsParameterModel.getJson();
			platformJson.put("type", platform);
			break;
		case "MLS":
			platformJson = mainApp.mlsParameterModel.getJson();
			platformJson.put("type", platform);
			break;
		}
		
		json.put("platform", platformJson);
		json.put("device", mainApp.deviceParameterModel.getJson());
		json.put("beam", mainApp.beamParameterModel.getJson());
		
		try {
			Path path = Paths.get(mainApp.mainApp.lessMainController.simulation_path, "Parameters", Const.LIDAR_PARAMETER);
			System.out.println("Lidar parameters saved: " + path.toString());
			BufferedWriter writer = Files.newBufferedWriter(path);
			writer.write(json.toString(2));
			writer.close();
		} catch (Exception e) {
			e.printStackTrace();
		}
	}
	
	@FXML
	private void handleOpen() {
		FileChooser fileChooser = new FileChooser();
		
		// Set extension filter
		FileChooser.ExtensionFilter extFilter = new FileChooser.ExtensionFilter("Config file (*.conf)", "*.conf");
		fileChooser.getExtensionFilters().add(extFilter);
		
		File file = fileChooser.showOpenDialog(mainApp.getPrimaryStage());
		
		
		open(file);	
	}

	public void open(File file) {
		try {
			if (file == null) {
				return ;
			}
			
			String content = FileUtils.readFileToString(file);
			JSONObject json = new JSONObject(content);
			
			JSONObject platformJson = json.getJSONObject("platform");
			String platform = platformJson.getString("type");
			
			switch (platform) {
			case "Mono Pulse":
				mainApp.monoPulseParameterModel.load(platformJson);
				platformTabPane.getSelectionModel().select(0);
				break;
			case "ALS":
				mainApp.alsParameterModel.load(platformJson);
				platformTabPane.getSelectionModel().select(1);
				break;
			case "TLS":
				mainApp.tlsParameterModel.load(platformJson);
				platformTabPane.getSelectionModel().select(2);
				break;
			case "MLS":
				mainApp.mlsParameterModel.load(platformJson);
				platformTabPane.getSelectionModel().select(3);
				break;
			}	
			
			mainApp.deviceParameterModel.load(json.getJSONObject("device"));
			mainApp.beamParameterModel.load(json.getJSONObject("beam"));
			
		} catch (Exception e) {
			e.printStackTrace();
		}
	}
	
	@FXML
	private void handleRunMenu() {
		singleLineMenuItem.setDisable(false);
		multiLinesPointCloudMenuItem.setDisable(false);
		if (mainApp.rootLayoutController.platformTabPane.getSelectionModel().getSelectedItem().getText().equals("Mono Pulse")) {
			singleLineMenuItem.setDisable(true);
			multiLinesPointCloudMenuItem.setDisable(true);
		}
	}
	
	@FXML
	private void handleToXml() {
		toXml();
		createGeometryConfigurationFile();
		
		mainApp.mainApp.lessMainController.generate_3d_model();
	}
	
	public void toXml() {
		Path parameters_path = Paths.get(mainApp.mainApp.lessMainController.simulation_path, "Parameters");
		Path script_path = Paths.get(PyLauncher.getScriptsPath("lidar/json2xml/json2xml"));
		try {
			ProcessBuilder pd=new ProcessBuilder(PyLauncher.getPyexe(), script_path.toString());
			pd.directory(new File(parameters_path.toString()));
			pd.start();
			System.out.println("To XML: " + parameters_path);
		} catch (Exception e) {
			e.printStackTrace();
		}
	}
	
	public void createGeometryConfigurationFile() {
		Path parameters_path = Paths.get(mainApp.mainApp.lessMainController.simulation_path, "Parameters");
		Path script_path = Paths.get(PyLauncher.getScriptsPath("lidar/geoconfig/generate"));
		try {
			ProcessBuilder pd=new ProcessBuilder(PyLauncher.getPyexe(), script_path.toString());
			pd.directory(new File(parameters_path.toString()));
			pd.start();
			System.out.println("Create geometry configuration script: " + script_path);
			System.out.println("Create geometry configuration file: " + parameters_path);
		} catch (Exception e) {
			e.printStackTrace();
		}
	}
	
	public void clear() {
		generalParameterVBox.getChildren().clear();
		platformTabPane.getTabs().clear();
	}
	
	@FXML
	public void handleMultiLineWaveform() {
		runWaveform();
	}
	
	@FXML
	public void handleMultiLinePointCloud() {
		runMultiLinePointCloud();
	}
	
	@FXML
	public void handleSingleRayPointCloud() {
		runSingleRayPointCloud();
	}
	
	public void runWaveform() {
		mainApp.mainApp.lessMainController.before_run();
		CountDownLatch latch = new CountDownLatch(1);
		PyLauncher currentPyLaucherThread = new PyLauncher();
		currentPyLaucherThread.setLessMainController(mainApp.mainApp.lessMainController);
		currentPyLaucherThread.prepare(mainApp.mainApp.lessMainController.simulation_path, PyLauncher.Operation.RUN_WAVEFORM, latch, mainApp.mainApp.lessMainController.outputConsole);
		currentPyLaucherThread.setTmpData(mainApp.mainApp.lessMainController.NumberofCoresTextField.getText());//Number of cores
		RunningStatusThread currentRunningStatusThread = new RunningStatusThread(currentPyLaucherThread, mainApp.mainApp.lessMainController.outputConsole, mainApp.mainApp.lessMainController.runBtn);
		mainApp.mainApp.lessMainController.currentRunningStatusThread = currentRunningStatusThread;
		currentRunningStatusThread.setMainController(mainApp.mainApp.lessMainController);
		currentRunningStatusThread.start();
	}
	
	public void runMultiLinePointCloud() {
		mainApp.mainApp.lessMainController.before_run();
		CountDownLatch latch = new CountDownLatch(1);
		PyLauncher currentPyLaucherThread = new PyLauncher();
		currentPyLaucherThread.setLessMainController(mainApp.mainApp.lessMainController);
		currentPyLaucherThread.prepare(mainApp.mainApp.lessMainController.simulation_path, PyLauncher.Operation.RUN_MULTI_RAYS_POINT_CLOUD, latch, mainApp.mainApp.lessMainController.outputConsole);
		currentPyLaucherThread.setTmpData(mainApp.mainApp.lessMainController.NumberofCoresTextField.getText());//Number of cores
		RunningStatusThread currentRunningStatusThread = new RunningStatusThread(currentPyLaucherThread, mainApp.mainApp.lessMainController.outputConsole, mainApp.mainApp.lessMainController.runBtn);
		mainApp.mainApp.lessMainController.currentRunningStatusThread = currentRunningStatusThread;
		currentRunningStatusThread.setMainController(mainApp.mainApp.lessMainController);
		currentRunningStatusThread.start();
	}
	
	public void runSingleRayPointCloud() {
		mainApp.mainApp.lessMainController.before_run();
		CountDownLatch latch = new CountDownLatch(1);
		PyLauncher currentPyLaucherThread = new PyLauncher();
		currentPyLaucherThread.setLessMainController(mainApp.mainApp.lessMainController);
		currentPyLaucherThread.prepare(mainApp.mainApp.lessMainController.simulation_path, PyLauncher.Operation.RUN_SINGLE_RAY_POINT_CLOUD, latch, mainApp.mainApp.lessMainController.outputConsole);
		currentPyLaucherThread.setTmpData(mainApp.mainApp.lessMainController.NumberofCoresTextField.getText());//Number of cores
		RunningStatusThread currentRunningStatusThread = new RunningStatusThread(currentPyLaucherThread, mainApp.mainApp.lessMainController.outputConsole, mainApp.mainApp.lessMainController.runBtn);
		mainApp.mainApp.lessMainController.currentRunningStatusThread = currentRunningStatusThread;
		currentRunningStatusThread.setMainController(mainApp.mainApp.lessMainController);
		currentRunningStatusThread.start();
	}
	
	@FXML
	public void handleWaveformToPoint() {
		blockWaveformToPoint();
	}
	
	public void blockWaveformToPoint() {
		Path parameters_path = Paths.get(mainApp.mainApp.lessMainController.simulation_path);
		Path script_path = Paths.get(PyLauncher.getScriptsPath("lidar/waveformToPoint/blockWaveformToPoint"));
		try {		
			
			int numberOfBins = getNumberOfBins();
			System.out.println("RootLayoutController.oneFileWaveformToPoint numberOfBins = " + numberOfBins);
			
			
			ProcessBuilder pd=new ProcessBuilder(PyLauncher.getPyexe(), script_path.toString(), String.valueOf(numberOfBins));
			pd.directory(new File(parameters_path.toString()));
			pd.start();
			System.out.println("Waveform to point");
		} catch (Exception e) {
			e.printStackTrace();
		}
	}
	
	private int getNumberOfBins() {
		int numberOfBins;
		double minRange = 0;
		double maxRange = 10;
		double rate = mainApp.deviceParameterModel.getAcquisitionPeriod() * 1e-9;
		if (mainApp.rootLayoutController.platformTabPane.getSelectionModel().getSelectedItem().getText().equals("TLS")) {
			System.out.println("RootLayoutController.getNumberOfBins TLS");
			minRange = mainApp.tlsParameterModel.getMinRange();
			maxRange = mainApp.tlsParameterModel.getMaxRange();
			
		} else if (mainApp.rootLayoutController.platformTabPane.getSelectionModel().getSelectedItem().getText().equals("ALS") ) {
			double altitude = mainApp.alsParameterModel.getAltitude();
			minRange = altitude - mainApp.alsParameterModel.getSavedUpper();
			maxRange = altitude + mainApp.alsParameterModel.getSavedLower();
		}
		
		final double C = 299792458.0;
		numberOfBins = (int)(2 * (maxRange - minRange) / (C * rate)) + 1;
		return numberOfBins;
	}
}
