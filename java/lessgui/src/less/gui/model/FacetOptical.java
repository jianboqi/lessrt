package less.gui.model;

import javafx.beans.property.SimpleIntegerProperty;
import javafx.beans.property.SimpleStringProperty;

public class FacetOptical {
	private SimpleStringProperty opticalName;
	private SimpleStringProperty reflectanceFront;
	private SimpleStringProperty reflectanceBack;
	private SimpleStringProperty transmittance;
	private SimpleIntegerProperty opType;
	
	
//	public FacetOptical(String oName, String rF, String rB, String t){
//		this.opticalName = new SimpleStringProperty(oName);
//		this.reflectanceFront = new SimpleStringProperty(rF);
//		this.reflectanceBack = new SimpleStringProperty(rB);
//		this.transmittance = new SimpleStringProperty(t);
//		this.opType = new SimpleStringProperty("DB");//The default value is "DB" from Database.
//	}
	
	public FacetOptical(String oName, String rF, String rB, String t, int type){
		this.opticalName = new SimpleStringProperty(oName);
		this.reflectanceFront = new SimpleStringProperty(rF);
		this.reflectanceBack = new SimpleStringProperty(rB);
		this.transmittance = new SimpleStringProperty(t);
		this.opType = new SimpleIntegerProperty(type);//The default value is "DB" from Database.
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
	
	public int getOpType() {
		return this.opType.get();
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
	
	public void setOpType(int optype) {
		this.opType.set(optype);
	}

	
}
