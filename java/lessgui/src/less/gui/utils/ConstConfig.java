package less.gui.utils;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.nio.file.Paths;

import org.json.JSONObject;
import org.json.JSONTokener;

import less.gui.helper.PyLauncher;

/**
 * ��json�����ļ��ж�ȡ���еĳ���
 * @author Jim
 *
 */
public class ConstConfig {
	public JSONObject data;
	
	public ConstConfig(){
		String jsonPath;
		if(Const.LESS_MODE.equals("development")){
			jsonPath= Paths.get(PyLauncher.getLessPyFolderPath(), Const.LESS_CONST_JSON_NAME).toString();
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
