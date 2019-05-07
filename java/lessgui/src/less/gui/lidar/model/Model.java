package less.gui.lidar.model;

import java.io.BufferedWriter;
import java.io.File;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.Map;

import org.apache.commons.io.FileUtils;
import org.apache.commons.io.FilenameUtils;
import org.json.JSONObject;

public class Model {
	
	public void setField(String fieldName, Object value) {
		try {
			String firstLetter = fieldName.substring(0, 1).toUpperCase();
			String setter = "set" + firstLetter + fieldName.substring(1);
//			Method method = this.getClass().getMethod(setter, new Class[] {});
			
			for (Method m : this.getClass().getMethods()) {
				if (setter.equals(m.getName())) {
					m.invoke(this, value);
					break;
				}
			}
			
//			method.invoke(this, value);
		} catch (Exception e) {
			e.printStackTrace();
		}
	}
	
	public Object getField(String fieldName) {
		try {
			String firstLetter = fieldName.substring(0, 1).toUpperCase();
			String setter = "get" + firstLetter + fieldName.substring(1);
//			Method method = this.getClass().getMethod(setter, new Class[] {});
			
			for (Method m : this.getClass().getMethods()) {
				if (setter.equals(m.getName())) {
					Object value = m.invoke(this);
//					System.out.println(fieldName + ": " + value.toString());
					return value;
				}
			}
			
//			method.invoke(this, value);
			
		} catch (Exception e) {
			e.printStackTrace();
		}
		return null;
	}
	
	public Map<String, String> labelMap = new HashMap<String, String>();
	
	public String getLabel(String fieldName) {
		return labelMap.get(fieldName);
	}
	
	public void setLabel(String fieldName, String label) {
		labelMap.put(fieldName, label);
	}
	
	public void load(String filename) {
		try {
			String content = FileUtils.readFileToString(new File(filename));
			JSONObject json = new JSONObject(content);
			
			for (Field f : this.getClass().getFields()) {
				
				if (f.getType().getName().equals("double")) {
					setField(f.getName(), json.getDouble(f.getName()));
				} else if (f.getType().getName().equals("int")) {
					setField(f.getName(), json.getInt(f.getName()));
				}
				
			}
		} catch (Exception e) {
			e.printStackTrace();
		}
	}
	
	public void load(JSONObject json) {
		try {
			
			for (Field f : this.getClass().getFields()) {
				
				if (f.getType().getName().equals("double")) {
					setField(f.getName(), json.getDouble(f.getName()));
				} else if (f.getType().getName().equals("int")) {
					setField(f.getName(), json.getInt(f.getName()));
				}
				
			}
		} catch (Exception e) {
			e.printStackTrace();
		}
	}
	
	public void save(String filename) {
		try {
			JSONObject json = new JSONObject();
			
			for (Field f : this.getClass().getFields()) {
				json.put(f.getName(), this.getField(f.getName()));
			}
			
			BufferedWriter writer = Files.newBufferedWriter(Paths.get(filename));
//			json.write(writer);
			writer.write(json.toString(2));
			writer.close();
		} catch (Exception e) {
			e.printStackTrace();
		}
	}
	
	public JSONObject getJson() {
		try {
			JSONObject json = new JSONObject();
			
			for (Field f : this.getClass().getFields()) {
				json.put(f.getName(), this.getField(f.getName()));
			}
			
			return json;
		} catch (Exception e) {
			e.printStackTrace();
		}
		
		return null;
	}
}
