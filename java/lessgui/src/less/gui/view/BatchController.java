package less.gui.view;


import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.concurrent.CountDownLatch;

import org.json.JSONObject;
import org.json.JSONTokener;

import javafx.beans.value.ChangeListener;
import javafx.beans.value.ObservableValue;
import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.event.EventHandler;
import javafx.fxml.FXML;
import javafx.scene.control.Button;
import javafx.scene.control.ListView;
import javafx.scene.control.TextField;
import javafx.scene.control.TreeCell;
import javafx.scene.control.TreeItem;
import javafx.scene.control.TreeView;
import javafx.scene.layout.AnchorPane;
import javafx.stage.FileChooser;
import javafx.stage.Stage;
import javafx.stage.WindowEvent;
import javafx.util.Callback;
import less.gui.helper.Filehelper;
import less.gui.helper.PyLauncher;
import less.gui.helper.RunningStatusThread;
import less.gui.model.TreeViewNode;
import less.gui.usercontrol.TreeViewCell;
import less.gui.usercontrol.TreeViewWithItems;
import less.gui.utils.BatchConfig;
import less.gui.utils.Const;

public class BatchController {
	@FXML
	private TreeViewWithItems<TreeViewNode> parameterTreeView;
	private ObservableList<TreeViewNode> paramterArray = FXCollections.observableArrayList();
	@FXML
	private AnchorPane treeviewAnchorPane;
	
	
	@FXML
	private TextField groupTextField;
	@FXML
	private Button groupAddBtn;
	@FXML
	private Button groupDelBtn;
	@FXML
	private Button paramterAddBtn;
	@FXML
	private Button paramterDelBtn;
	@FXML
	private ListView<String> groupListView;
	private ObservableList<String> groupList = FXCollections.observableArrayList();
	@FXML
	private ListView<String> parameterListView;
	
	private Map<String, ObservableList<String>> group_param_map = new LinkedHashMap<String, ObservableList<String>>();
	private Map<String, String> param_value_map = new LinkedHashMap<String, String>();
	
	@FXML
	private TextField valueTextField;

	private LessMainWindowController mwController;
	
	private String batch_file_path = "";
	
	private Stage parentStage;
	
	public void setMainWindowController(LessMainWindowController mWindowController){
		this.mwController = mWindowController;
	}
	
	public void setParentStage(Stage parentStage) {
		this.parentStage = parentStage;
	}
	
	public void initView(){
		initTreeView();
	}
	
	public void initTreeView(){
		TreeViewNode root = new TreeViewNode("Parameters", "");
		TreeItem<TreeViewNode> rootItem = new TreeItem<TreeViewNode>(root);
		parameterTreeView = new TreeViewWithItems<TreeViewNode>(rootItem);
		treeviewAnchorPane.getChildren().add(parameterTreeView);
		AnchorPane.setLeftAnchor(parameterTreeView, 0.0);
		AnchorPane.setRightAnchor(parameterTreeView, 0.0);
		AnchorPane.setBottomAnchor(parameterTreeView, 0.0);
		AnchorPane.setTopAnchor(parameterTreeView, 0.0);
		parameterTreeView.setItems(paramterArray);
		parameterTreeView.setShowRoot(false);
		parameterTreeView.setCellFactory(new Callback<TreeView<TreeViewNode>, TreeCell<TreeViewNode>>(){
			@Override
			public TreeCell<TreeViewNode> call(TreeView<TreeViewNode> p) {
				return new TreeViewCell();
			}
		});	
		BatchConfig batchConfig = new BatchConfig();
		batchConfig.constructTree(root);
		paramterArray.add(root);
		for(TreeItem<?> child: rootItem.getChildren()){
			for(TreeItem<?> child1: child.getChildren()){
	            expandTreeView(child1);
	        }
        }
		
		//initialize the listview
		initListView();
	}
	
	private void expandTreeView(TreeItem<?> item){
	    if(item != null && !item.isLeaf()){
	        item.setExpanded(false);
	        for(TreeItem<?> child:item.getChildren()){
	            expandTreeView(child);
	        }
	    }
	}
	
	private void initListView(){
		this.groupListView.setItems(this.groupList);
		//this.parameterListView.setItems(this.parameterList);
		
		this.groupAddBtn.setOnAction((event) -> {
			String gname = this.groupTextField.getText();
		    if(!gname.equals("") && !this.groupList.contains(gname)){
		    	this.groupList.add(this.groupTextField.getText());
		    	if(!this.group_param_map.containsKey(gname)){
		    		group_param_map.put(gname, FXCollections.observableArrayList());
		    		this.parameterListView.setItems(group_param_map.get(gname));
		    	}
		    		
		    }
		});
		this.groupDelBtn.setOnAction((event) -> {
			String selected = this.groupListView.getSelectionModel().getSelectedItem();
		    this.groupList.remove(selected);
		    this.group_param_map.get(selected).clear();
		    this.group_param_map.remove(selected);
		});
		
		this.groupListView.getSelectionModel().selectedItemProperty().addListener(new ChangeListener<String>() {
		    @Override
		    public void changed(ObservableValue<? extends String> observable, String oldValue, String newValue) {
		    	if(newValue != null){
			        groupDelBtn.setDisable(false);
			        paramterAddBtn.setDisable(false);
			      //  paramterDelBtn.setDisable(false);
			        parameterListView.setItems(group_param_map.get(newValue));
		    	}else{
		    		groupDelBtn.setDisable(true);
		    		paramterAddBtn.setDisable(true);
			       // paramterDelBtn.setDisable(true);
		    	}
		        
		    }
		});
		
		this.paramterAddBtn.setOnAction((event) -> {
			TreeItem<TreeViewNode> tItem = this.parameterTreeView.getSelectionModel().getSelectedItem();
			if(tItem!= null && tItem.isLeaf()){
				String nodeName = tItem.getValue().getParameterName();
				String gname = groupListView.getSelectionModel().getSelectedItem();
				if(!group_param_map.get(gname).contains(nodeName)){
					group_param_map.get(gname).add(nodeName);
					parameterListView.getSelectionModel().select(nodeName);
				}
					
			}
		});
		this.paramterDelBtn.setOnAction((event) -> {
			String gname = this.groupListView.getSelectionModel().getSelectedItem();
			String paramName = this.parameterListView.getSelectionModel().getSelectedItem();
			this.group_param_map.get(gname).remove(paramName);
			param_value_map.remove(paramName);
		});
		
		this.parameterListView.getSelectionModel().selectedItemProperty().addListener(new ChangeListener<String>() {
		    @Override
		    public void changed(ObservableValue<? extends String> observable, String oldValue, String newValue) {
		    	if(newValue != null){
		    		valueTextField.setDisable(false);
		    		paramterDelBtn.setDisable(false);
		    		if(param_value_map.containsKey(newValue))
		    			valueTextField.setText(param_value_map.get(newValue));
		    		else
		    			valueTextField.setText("");
		    	}else{
		    		valueTextField.setDisable(true);
		    		paramterDelBtn.setDisable(true);
		    	}        
		    }
		});
		
		valueTextField.textProperty().addListener((observable, oldValue, newValue) -> {
			String paramName = parameterListView.getSelectionModel().getSelectedItem();
			param_value_map.put(paramName, newValue);
		});
		
		//before closing
		this.parentStage.setOnCloseRequest(new EventHandler<WindowEvent>() {
		      public void handle(WindowEvent we) {
		    	 save();
		      }
		  }); 
	}
	
	public void savetoFile(String path){
		JSONObject json=new JSONObject();
		for(Map.Entry<String, ObservableList<String>> entry: this.group_param_map.entrySet()){
			String gname = entry.getKey();
			JSONObject groupObj = new JSONObject();
			ObservableList<String> paramList = entry.getValue();
			for(int i=0;i<paramList.size();i++){
				String paramName = paramList.get(i);
				groupObj.put(paramName, param_value_map.get(paramName));
			}
			json.put(gname, groupObj);	
		}
		String finalStr = json.toString(3);
		Filehelper.save_string_to_file(path, finalStr);
	}
	
	@FXML
	public void save(){
		if(batch_file_path.equals("")){
			saveAs();
		}else{
			savetoFile(batch_file_path);
		}
	}
	
	@FXML
	public void saveAs(){
		FileChooser fileChooser = new FileChooser();
		String lastOpened = this.mwController.getLastOpenedPath(Const.LAST_OPNED_BATCH_FILE_PATH);
		if (lastOpened != null && new File(lastOpened).exists()){
			fileChooser.setInitialDirectory(new File(lastOpened));
		}else{
			if(this.mwController.simulation_path != null)
				fileChooser.setInitialDirectory(new File(this.mwController.simulation_path));
		}
		fileChooser.getExtensionFilters().add(new FileChooser.ExtensionFilter("Batch File", "*.json"));
		File file = fileChooser.showSaveDialog(this.parentStage);
        if(file !=null)
        {
        	this.mwController.setLastOpenedPath(Const.LAST_OPNED_BATCH_FILE_PATH,file.getParent().toString());
        	batch_file_path = file.toString();
        	savetoFile(file.toString());
        	this.parentStage.setTitle(Const.LESS_BATCH_TOOL_TITLE +"-" +file.toString());
        }
	}
	
	
	@FXML 
	public void load(){
		
		FileChooser fileChooser = new FileChooser();
		String lastOpened = this.mwController.getLastOpenedPath(Const.LAST_OPNED_BATCH_FILE_PATH);
		if (lastOpened != null && new File(lastOpened).exists()){
			fileChooser.setInitialDirectory(new File(lastOpened));
		}else{
			if(this.mwController.simulation_path != null)
				fileChooser.setInitialDirectory(new File(this.mwController.simulation_path));
		}
		fileChooser.getExtensionFilters().add(new FileChooser.ExtensionFilter("Batch File", "*.json"));
		File file = fileChooser.showOpenDialog(this.parentStage);
        if(file !=null)
        {
        	this.mwController.setLastOpenedPath(Const.LAST_OPNED_BATCH_FILE_PATH,file.getParent().toString());
        	loadJson2Map(file.toString());
        	this.parentStage.setTitle(Const.LESS_BATCH_TOOL_TITLE +"-" +file.toString());
        	batch_file_path = file.toString();
        }
	}
	
	
	public void loadJson2Map(String path){
		group_param_map.clear();
		param_value_map.clear();
		groupList.clear();
		JSONTokener jsonTokener = null;
		try {
			jsonTokener = new JSONTokener(new FileReader(new File(path)));
		} catch (FileNotFoundException e) {
			e.printStackTrace();
		}  
		JSONObject data = new JSONObject(jsonTokener);
		Iterator<?> keys = data.keys();
		while( keys.hasNext() ) {
		    String gname = (String)keys.next();
		    if(!this.group_param_map.containsKey(gname)){
		    	this.group_param_map.put(gname, FXCollections.observableArrayList());
		    }
		    this.groupList.add(gname);
		    JSONObject value = data.getJSONObject(gname);
		    Iterator<?> subkeys = value.keys();
		    while(subkeys.hasNext()){
		    	String paramName = (String)subkeys.next();
		    	this.group_param_map.get(gname).add(paramName);
		    	String paramValue = value.getString(paramName);
		    	param_value_map.put(paramName, paramValue);
		    }
		    
		}
		
	}
	
	@FXML
	private void runBatch(){
		save();
		if(!batch_file_path.equals("") && !this.mwController.isRunning){
			this.mwController.before_run();
			CountDownLatch latch = new CountDownLatch(1);
			this.mwController.currentPyLaucherThread = new PyLauncher();
			this.mwController.currentPyLaucherThread.setLessMainController(this.mwController);
			this.mwController.currentPyLaucherThread.setTmpData(this.batch_file_path);
			this.mwController.currentPyLaucherThread.prepare(this.mwController.simulation_path, PyLauncher.Operation.RUN_BATCH, latch, this.mwController.outputConsole);
			this.mwController.currentRunningStatusThread = new RunningStatusThread(this.mwController.currentPyLaucherThread, this.mwController.outputConsole, this.mwController.runBtn);
			this.mwController.currentRunningStatusThread.setMainController(this.mwController);
			this.mwController.currentRunningStatusThread.start();
		}
		
	}
	
}
