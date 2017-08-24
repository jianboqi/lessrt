package less.gui.utils;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.nio.file.Paths;

import org.json.JSONObject;
import org.json.JSONTokener;

/**
 * 从json配置文件中读取所有的常量
 * @author Jim
 *
 */
public class ConstConfig {
	public JSONObject data;
	
	public ConstConfig(){
		String jsonPath;
		if(Const.LESS_MODE.equals("development")){
			jsonPath= Const.LESS_LAUNCH_PATH + Const.LESS_CONST_JSON_NAME;
		}else{
			jsonPath = Paths.get(System.getProperty("user.dir"),"bin","scripts","Lesspy",Const.LESS_CONST_JSON_NAME).toString();
		}	
		JSONTokener jsonTokener = null;
		try {
			jsonTokener = new JSONTokener(new FileReader(new File(jsonPath)));
		} catch (FileNotFoundException e) {
			e.printStackTrace();
		}  
		data = new JSONObject(jsonTokener);
        
	}
}
