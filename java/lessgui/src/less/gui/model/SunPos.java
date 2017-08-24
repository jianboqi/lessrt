package less.gui.model;

import org.json.JSONObject;

public class SunPos {
	public int year;
	public int month;
	public int day;
	public int hour;
	public int minute;
	public int second;
	public int timezone;
	public double lat;
	public double lon;
	public double altitude;
	
	
	public JSONObject toJsonObject(){
		JSONObject jsonObject = new JSONObject();
		jsonObject.put("year", year);
		jsonObject.put("month", month);
		jsonObject.put("day", day);
		jsonObject.put("hour", hour);
		jsonObject.put("minute", minute);
		jsonObject.put("second", second);
		jsonObject.put("timezone", timezone);
		jsonObject.put("lat", lat);
		jsonObject.put("lon", lon);
		jsonObject.put("altitude", altitude);
		return jsonObject;
	}
	
	public void fromJsonObject(JSONObject jsonObject){
		year = jsonObject.getInt("year");
		month = jsonObject.getInt("month");
		day = jsonObject.getInt("day");
		hour = jsonObject.getInt("hour");
		minute = jsonObject.getInt("minute");
		second = jsonObject.getInt("second");
		timezone = jsonObject.getInt("timezone");
		lat = jsonObject.getDouble("lat");
		lon = jsonObject.getDouble("lon");
		altitude = jsonObject.getDouble("altitude");
	}
}
