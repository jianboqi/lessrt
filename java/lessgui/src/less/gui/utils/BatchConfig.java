package less.gui.utils;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.nio.file.Paths;
import java.util.Iterator;

import org.json.JSONObject;
import org.json.JSONTokener;

import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import less.gui.helper.PyLauncher;
import less.gui.model.FacetOptical;
import less.gui.model.TreeViewNode;

public class BatchConfig {
public JSONObject data;
	
	public BatchConfig(){
		String jsonPath;
		if(Const.LESS_MODE.equals("development")){
			jsonPath= Paths.get(PyLauncher.getLessPyFolderPath(),Const.LESS_BATCH_JSON_NAME).toString();
		}else{
			jsonPath = Paths.get(System.getProperty("user.dir"),"bin","scripts","Lesspy",Const.LESS_BATCH_JSON_NAME).toString();
		}
		JSONTokener jsonTokener = null;
		try {
			jsonTokener = new JSONTokener(new FileReader(new File(jsonPath)));
		} catch (FileNotFoundException e) {
			e.printStackTrace();
		}  
		data = new JSONObject(jsonTokener);
        
	}
	
	public void iterChild(TreeViewNode node, JSONObject obj){
		Iterator<?> keys = obj.keys();
		while( keys.hasNext() ) {
		    String key = (String)keys.next();
		    Object value = obj.get(key);
		    TreeViewNode childNode ;
		    if(! (value instanceof JSONObject)){
		    	childNode= new TreeViewNode(key, (String)value);
		    }else{
		    	childNode= new TreeViewNode(key, "");
		    }
		    node.getChildren().add(childNode);
		    if(value instanceof JSONObject){
		    	iterChild(childNode, (JSONObject)value);
		    }
		}
	}
	
	public void constructTree(TreeViewNode root){
		iterChild(root, data);		
	}
}
