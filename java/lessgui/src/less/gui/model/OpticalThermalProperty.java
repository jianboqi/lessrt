package less.gui.model;

import javafx.scene.paint.Color;

/**
 * 保存光谱的温度信息
 * @author Jim
 *
 */
public class OpticalThermalProperty {
	private String opticalName;
	private String temperatureName="-"; //temperature有一个默认初始值-, 在非thermalmode情况下。
	private Color componentColor = Color.DARKGREEN; //记录每个component显示时的颜色。
	

	public OpticalThermalProperty(String o, String t){
		this.opticalName = o;
		this.temperatureName = t;
	}
	
	public OpticalThermalProperty(String o){
		this.opticalName = o;
	}
	public OpticalThermalProperty(Color componentColor){
		this.componentColor = componentColor;
	}
	
	public Color getComponentColor() {
		return componentColor;
	}

	public void setComponentColor(Color componentColor) {
		this.componentColor = componentColor;
	}
	
	public String getOpticalName(){
		return this.opticalName;
	}
	public void setOpticalName(String o){
		this.opticalName = o;
	}
	
	public String getTermperatureName(){
		return this.temperatureName;
	}	
	public void setTemperatureName(String t){
		this.temperatureName = t;
	}
	
	
}
