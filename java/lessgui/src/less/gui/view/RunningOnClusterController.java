package less.gui.view;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.file.Paths;

import javafx.application.Platform;
import javafx.beans.value.ChangeListener;
import javafx.beans.value.ObservableValue;
import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.event.EventHandler;
import javafx.fxml.FXML;
import javafx.scene.control.Button;
import javafx.scene.control.CheckBox;
import javafx.scene.control.ListView;
import javafx.scene.control.TextField;
import javafx.stage.Stage;
import javafx.stage.WindowEvent;
import less.gui.helper.Filehelper;
import less.gui.helper.PyLauncher;
import less.gui.utils.Const;

public class RunningOnClusterController {
	
	@FXML
	private TextField AddressHostField;
	@FXML
	private TextField AddressPortField;
	@FXML
	private Button serverBtn;
	@FXML
	private TextField remoteHostField;
	@FXML
	private TextField remotePortField;
	@FXML
	private ListView<String> serverListView;
	@FXML
	private CheckBox networkSimCheck;
	
	private ObservableList<String> serverList = FXCollections.observableArrayList();
	
	private LessMainWindowController mwController;
	private Stage parentStage;
	
	
	
	public void setLessMainController(LessMainWindowController mWindowController){
		this.mwController = mWindowController;
	}
	
	public void setParentStage(Stage stage){
		this.parentStage  = stage;
	}
	
	public void initView(){
		serverListView.setItems(this.serverList);
		
		this.parentStage.setOnCloseRequest(new EventHandler<WindowEvent>() {
		      public void handle(WindowEvent we) {
		    	  save_to_file();
		      }
		  });
		this.load_from_file();
		
		if(mwController.projManager.isNetworkSim){
			serverListView.setDisable(false);
			networkSimCheck.setSelected(true);
		}else{
			serverListView.setDisable(true);
			networkSimCheck.setSelected(false);
		}
		//checkbox
		networkSimCheck.selectedProperty().addListener(new ChangeListener<Boolean>() {
	        public void changed(ObservableValue<? extends Boolean> ov,
	                Boolean old_val, Boolean new_val) {
	                    if(new_val){
	                    	serverListView.setDisable(false);
	            			mwController.projManager.isNetworkSim = true;
	                    }
	                    else{
	                    	serverListView.setDisable(true);
	            			mwController.projManager.isNetworkSim = false;
	                    }
	            }
	        });
		
		//锟斤拷始锟斤拷锟斤拷钮状态锟斤拷锟斤拷锟矫关闭达拷锟斤拷锟劫打开ｏ拷状态锟侥憋拷
		changeStartServerBtn();
	}
	
	/**
	 * 锟侥憋拷button锟斤拷状态
	 */
	private void changeStartServerBtn(){
		if(this.mwController.projManager.isServerStarted){
			Platform.runLater(() ->serverBtn.setText("Stop server"));
			Platform.runLater(() ->serverBtn.setStyle("-fx-text-fill: #ff0000"));
			;
		}else{
			Platform.runLater(() ->serverBtn.setText("Start server"));
			Platform.runLater(() ->serverBtn.setStyle("-fx-text-fill: #000000"));
		}
	}
	
	@FXML
	private void onStartServer(){
		
		if(!this.mwController.projManager.isServerStarted){
			this.mwController.projManager.isServerStarted = true;
			serverBtn.setText("Staring server...");
			serverBtn.setStyle("-fx-text-fill: #000000");
			Thread t = new Thread(new Runnable() {
		    	public void run () {
		    		 start_server();
		    	}
		    });

		    t.start();
		}
		else{
			this.mwController.projManager.isServerStarted = false;
			changeStartServerBtn();
			this.mwController.projManager.p.destroy();
			this.mwController.outputConsole.appendText("INFO: Server stopped.\n");
		}
	}
	
	
	private void start_server(){
		String srvexe = this.getSrvexe();
		String host = AddressHostField.getText();
		String port = AddressPortField.getText();
		this.mwController.outputConsole.appendText("INFO: Starting server "+host +":"+port+"\n");
		if(host.equals("") || port.equals(""))
			return;
		//
		ProcessBuilder pd=new ProcessBuilder(this.getSrvexe(),"-i", host, "-l", port);
		pd.directory(new File(this.getSrvDir()));
		try {
			this.mwController.projManager.p = pd.start();
			
			BufferedReader input = new BufferedReader(new InputStreamReader(this.mwController.projManager.p.getInputStream()));
			String line;
			this.mwController.outputConsole.setNormalMode();
			while ((line = input.readLine()) != null) {
				if(line.contains("Enter mtssrv -h")){
					
				}else if (line.contains("Send Ctrl-C to stop")){
					changeStartServerBtn();//
					this.mwController.outputConsole.appendText("INFO: Server started, listening on "+host +":"+port+"\n");
				}else{
					String [] arr = line.split("]");
					this.mwController.outputConsole.appendText("INFO: " + arr[1]+"\n");	
				}
					
							
			}
			input = new BufferedReader(new InputStreamReader(this.mwController.projManager.p.getErrorStream()));
			while ((line = input.readLine()) != null) {
				this.mwController.outputConsole.setErrorMode();
				this.mwController.outputConsole.log(line+"\n");
			}
			this.mwController.projManager.p.waitFor();
		} catch (IOException | InterruptedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
	
	
	/**
	 * 锟斤拷锟絪erver
	 */
	@FXML
	private void onAdd(){
		String remoteHost = this.remoteHostField.getText();
		String portHost = this.remotePortField.getText();
		if(remoteHost.equals("") || portHost.equals("")){
			return;
		}
		if(!this.serverList.contains(remoteHost+":"+portHost))
			this.serverList.add(remoteHost+":"+portHost);
	}
	
	@FXML
	private void onDel(){
		int seletedIndex = this.serverListView.getSelectionModel().getSelectedIndex();
		if(seletedIndex >= 0){
			this.serverList.remove(this.serverListView.getSelectionModel().getSelectedItem());
		}
	}
	
	
	private void save_to_file(){
		if(this.mwController.simulation_path==null){
			System.out.println("INFO: No simulation.");
			return;
		}
		
		String paramPath = this.mwController.projManager.getParameterDirPath();
		String servertxtPath = Paths.get(paramPath, Const.LESS_SERVER_TXT_FILE).toString();
		String srvstr = "";
		for(int i=0;i<this.serverList.size();i++){
			srvstr += this.serverList.get(i)+"\n";
		}
		Filehelper.save_string_to_file(servertxtPath, srvstr);
	}
	
	private void load_from_file(){
		if(this.mwController.simulation_path==null){
			System.out.println("INFO: No simulation.");
			return;
		}
		
		String paramPath = this.mwController.projManager.getParameterDirPath();
		File servertxtPath = Paths.get(paramPath, Const.LESS_SERVER_TXT_FILE).toFile();
		
		if(servertxtPath.exists()){
			this.serverList.clear();
			try (BufferedReader reader = new BufferedReader(new FileReader(servertxtPath))) {
		        String line;
		        int objnum = 0;
		        while ((line = reader.readLine()) != null){
		        	if(!line.equals("")){
		        		this.serverList.add(line);
		        	}
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
	
	@FXML
	private void onCancel(){
		this.parentStage.close();
	}
	
	@FXML
	private void onOK(){
		this.save_to_file();
		this.parentStage.close();
	}
	
	/**
	 * 
	 * @return
	 */
	public String getSrvexe(){
		String srvPath;
		if(Const.LESS_MODE.equals("development")){
			srvPath= Paths.get(PyLauncher.getLessPyFolderPath(),"bin","rt",
					this.mwController.constConfig.data.getString("current_rt_program"),Const.LESS_SERVER_EXE).toString();
		}else{
			srvPath = Paths.get(System.getProperty("user.dir"),"bin","scripts","Lesspy",
					"bin","rt",this.mwController.constConfig.data.getString("current_rt_program"),Const.LESS_SERVER_EXE).toString();
		}
		return srvPath;
	}
	
	public String getSrvDir(){
		String srvPath;
		if(Const.LESS_MODE.equals("development")){
			srvPath= Paths.get(PyLauncher.getLessPyFolderPath(),"bin","rt",
					this.mwController.constConfig.data.getString("current_rt_program")).toString();
		}else{
			srvPath = Paths.get(System.getProperty("user.dir"),"bin","scripts","Lesspy",
					"bin","rt",this.mwController.constConfig.data.getString("current_rt_program")).toString();
		}
		return srvPath;
	}
}
