package less.gui.model;

import javafx.scene.paint.Color;

/**
 * optical properties
 * @author Jim
 *
 */
public class OpticalThermalProperty {
	private String opticalName;
	private String temperatureName="-"; //temperature with default value equals to -
	private Color componentColor = Color.DARKGREEN; // the color of each component.
	

	public OpticalThermalProperty(String o, String t){
		this.opticalName = o;
		this.temperatureName = t;
	}
	
	public OpticalThermalProperty(String o, String t, String colorStr){
		this.opticalName = o;
		this.temperatureName = t;
		String pureColorStr = colorStr.substring(0, colorStr.length()-2);
		String opcityStr = colorStr.substring(colorStr.length()-2);
		int opcityInt = Integer.parseInt(opcityStr, 16);
		this.componentColor = Color.web(pureColorStr, opcityInt/255.0);
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
