package less.gui.model;

import org.json.JSONObject;

public class ProspectDParams {
	public String opName = "";
	public double N = 1.5;
	public double Car = 10.0;
	public double BP = 0.0;
	public double Cm = 0.009;
	public double Cab = 30.0;
	public double Anth = 1.0;
	public double Cw = 0.015;
	public boolean isProsect5 = false;
	
	public JSONObject toJsonObject(){
		JSONObject jsonObject = new JSONObject();
		jsonObject.put("opName", opName);
		jsonObject.put("N", N);
		jsonObject.put("Car", Car);
		jsonObject.put("BP", BP);
		jsonObject.put("Cm", Cm);
		jsonObject.put("Cab", Cab);
		jsonObject.put("Anth", Anth);
		jsonObject.put("Cw", Cw);
		jsonObject.put("isProsect5", isProsect5);
		return jsonObject;
	}
	
	public void fromJsonObject(JSONObject jsonObject){
		opName = jsonObject.getString("opName");
		N = jsonObject.getDouble("N");
		Car = jsonObject.getDouble("Car");
		BP = jsonObject.getDouble("BP");
		Cm = jsonObject.getDouble("Cm");
		Cab = jsonObject.getDouble("Cab");
		Anth = jsonObject.getDouble("Anth");
		Cw = jsonObject.getDouble("Cw");
		isProsect5 = jsonObject.getBoolean("isProsect5");
	}
	
}
