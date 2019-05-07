package less.gui.lidar.view;

import java.io.BufferedWriter;
import java.io.File;
import java.nio.file.Files;
import java.nio.file.Paths;

import org.apache.commons.io.FileUtils;
import org.json.JSONObject;

import javafx.fxml.FXML;
import javafx.scene.control.MenuItem;
import javafx.scene.control.TabPane;
import javafx.scene.layout.VBox;
import javafx.stage.FileChooser;
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
			BufferedWriter writer = Files.newBufferedWriter(Paths.get(Const.LIDAR_PARAMETER));
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
			
			mainApp.update();
			
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
	
	public void clear() {
		generalParameterVBox.getChildren().clear();
		platformTabPane.getTabs().clear();
	}
}
