package less.gui.model;

import javafx.beans.property.SimpleStringProperty;

public class FacetOptical {
	private SimpleStringProperty opticalName;
	private SimpleStringProperty reflectanceFront;
	private SimpleStringProperty reflectanceBack;
	private SimpleStringProperty transmittance;
	
	public FacetOptical(String oName, String rF, String rB, String t){
		this.opticalName = new SimpleStringProperty(oName);
		this.reflectanceFront = new SimpleStringProperty(rF);
		this.reflectanceBack = new SimpleStringProperty(rB);
		this.transmittance = new SimpleStringProperty(t);
	}
	public String getOpticalName() {
		return opticalName.get();
	}
	public String getReflectanceFront() {
		return reflectanceFront.get();
	}

	public String getReflectanceBack() {
		return reflectanceBack.get();
	}

	public String getTransmittance() {
		return transmittance.get();
	}

	public void setOpticalName(String opticalName) {
		this.opticalName.set(opticalName);
	}

	public void setReflectanceFront(String reflectanceFront) {
		this.reflectanceFront.set(reflectanceFront);
	}

	public void setReflectanceBack(String reflectanceBack) {
		this.reflectanceBack.set(reflectanceBack);
	}

	public void setTransmittance(String transmittance) {
		this.transmittance.set(transmittance);
	}
	
	

	
}
