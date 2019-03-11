package less.gui.model;

import org.json.JSONObject;

import less.gui.utils.Const;

public class AtmosphereParams {
	public String calculationMode = Const.LESS_ATS_CAL_MODE_TWOSTEP;
	
	public JSONObject toJsonObject(){
		JSONObject jsonObject = new JSONObject();
		jsonObject.put("atsCalMode", calculationMode);
		return jsonObject;
	}
	
	public void fromJsonObject(JSONObject jsonObject){
		calculationMode = jsonObject.getString("atsCalMode");
	}
}
